// ============================================================
// cnn_accelerator_top.v
// Top-Level CNN Accelerator with AXI4-Stream Interface
// ============================================================
// Integrates:
//   - layer_controller  : drives mode[1:0] per layer
//   - conv_pe           : one Processing Element (systolic)
//   - AXI4-Stream slave : receives activation + weight data
//   - AXI4-Stream master: sends output feature map pixels
//
// AXI4-Stream Protocol (simplified):
//   S_AXIS (slave)  : input data stream {act[7:0], wmag[7:0],
//                     wsign[0], tlast}
//   M_AXIS (master) : output result stream {result[31:0], tlast}
//
// Data packet format over S_AXIS (17 bits per beat):
//   [16]    = w_sign
//   [15:8]  = w_mag[7:0]
//   [7:0]   = act_in[7:0]
//
// The host (ARM PS) writes:
//   1. layer_id register (via AXI-Lite, simplified here as input pin)
//   2. bias register
//   3. Streams 9×Cin data beats per output pixel
//   4. Asserts tlast on the final beat of each pixel
//
// The accelerator:
//   1. Reads mode from layer_controller based on layer_id
//   2. Accumulates 9×Cin MACs in the PE
//   3. Outputs result + bias on M_AXIS with tlast
// ============================================================

`timescale 1ns/1ps

module cnn_accelerator_top (
    // Clock & Reset
    input  wire        clk,
    input  wire        rst_n,

    // Layer control (driven by PS via AXI-Lite in full design)
    input  wire [1:0]  layer_id,      // 0=conv1,1=conv2,2=conv3,3=conv4
    input  wire [31:0] bias_in,       // bias for current output channel

    // AXI4-Stream Slave (Input: activation + weight data)
    input  wire [16:0] s_axis_tdata,  // {w_sign, w_mag[7:0], act[7:0]}
    input  wire        s_axis_tvalid,
    input  wire        s_axis_tlast,  // last beat of a pixel (9*Cin beats)
    output wire        s_axis_tready,

    // AXI4-Stream Master (Output: convolution result)
    output reg  [31:0] m_axis_tdata,
    output reg         m_axis_tvalid,
    output reg         m_axis_tlast,
    input  wire        m_axis_tready
);

// ── Mode from Layer Controller ────────────────────────────
wire [1:0] mode;
layer_controller u_ctrl (
    .layer_id (layer_id),
    .mode     (mode)
);

// ── AXI4-Stream Slave Handshake ───────────────────────────
wire s_handshake = s_axis_tvalid & s_axis_tready;
assign s_axis_tready = 1'b1;   // always ready (back-pressure not implemented)

// ── Unpack input data ─────────────────────────────────────
wire [7:0] act_in = s_axis_tdata[7:0];
wire [7:0] w_mag  = s_axis_tdata[15:8];
wire       w_sign = s_axis_tdata[16];

// ── PE Control Signals ────────────────────────────────────
reg  pe_start;
wire pe_valid;
wire [31:0] pe_result;

// ── Processing Element ────────────────────────────────────
conv_pe #(.CIN_MAX(64), .KSZ(9), .ACC_BITS(32)) u_pe (
    .clk     (clk),
    .rst_n   (rst_n),
    .start   (pe_start),
    .mode    (mode),
    .act_in  (act_in),
    .w_mag   (w_mag),
    .w_sign  (w_sign),
    .bias_in (bias_in),
    .result  (pe_result),
    .valid   (pe_valid)
);

// ── Datapath FSM ─────────────────────────────────────────
localparam WAIT_DATA = 2'd0;
localparam STREAM_IN = 2'd1;
localparam SEND_OUT  = 2'd2;

reg [1:0] state;

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        state         <= WAIT_DATA;
        pe_start      <= 1'b0;
        m_axis_tdata  <= 32'd0;
        m_axis_tvalid <= 1'b0;
        m_axis_tlast  <= 1'b0;
    end else begin
        pe_start <= 1'b0;

        case (state)
            // ── Wait for first valid data beat ──────────
            WAIT_DATA: begin
                m_axis_tvalid <= 1'b0;
                m_axis_tlast  <= 1'b0;
                if (s_handshake) begin
                    pe_start <= 1'b1;   // clear accumulator
                    state    <= STREAM_IN;
                end
            end

            // ── Stream 9×Cin beats into PE ───────────────
            STREAM_IN: begin
                if (s_handshake) begin
                    if (s_axis_tlast) begin
                        // Last beat: PE will compute final result
                        pe_start <= 1'b1;
                        state    <= SEND_OUT;
                    end
                end
            end

            // ── Output result on M_AXIS ──────────────────
            SEND_OUT: begin
                if (pe_valid) begin
                    m_axis_tdata  <= pe_result;
                    m_axis_tvalid <= 1'b1;
                    m_axis_tlast  <= 1'b1;
                    if (m_axis_tready) begin
                        m_axis_tvalid <= 1'b0;
                        m_axis_tlast  <= 1'b0;
                        state         <= WAIT_DATA;
                    end
                end
            end

            default: state <= WAIT_DATA;
        endcase
    end
end

endmodule
