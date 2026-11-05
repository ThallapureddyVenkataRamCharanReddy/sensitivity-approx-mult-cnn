// ============================================================
// conv_pe.v
// Convolutional Processing Element (PE)
// ============================================================
// Computes ONE output feature map pixel for a 3×3 convolution.
// Supports all 4 approximate multiplier modes via mode[1:0].
//
// Operation:
//   For a 3×3×Cin kernel and one output channel:
//     out = SUM_{r=0}^{2} SUM_{c=0}^{2} SUM_{cin=0}^{Cin-1}
//               AxM(act[r,c,cin], |w[r,c,cin]|) * sign(w[r,c,cin])
//           + bias
//
// This PE computes one (r,c,cin) triple per clock cycle.
// The controller drives 9*Cin enable pulses then asserts done.
//
// Parameters:
//   CIN_MAX   — maximum number of input channels (64)
//   ACC_BITS  — accumulator width (32 bits)
//
// Ports:
//   clk, rst_n
//   start         — pulse to begin a new pixel computation
//   mode[1:0]     — multiplier mode for this layer
//   act_in[7:0]   — current activation pixel (streamed in)
//   w_mag[7:0]    — current weight magnitude (streamed in)
//   w_sign        — current weight sign
//   bias_in[31:0] — bias value for this output channel
//   result[31:0]  — raw integer output (before dequantization)
//   valid         — result is valid this cycle
// ============================================================

`timescale 1ns/1ps

module conv_pe #(
    parameter CIN_MAX  = 64,
    parameter KSZ      = 9,      // 3×3 kernel positions
    parameter ACC_BITS = 32
)(
    input  wire                  clk,
    input  wire                  rst_n,
    input  wire                  start,
    input  wire [1:0]            mode,
    input  wire [7:0]            act_in,
    input  wire [7:0]            w_mag,
    input  wire                  w_sign,
    input  wire [ACC_BITS-1:0]   bias_in,
    output wire [ACC_BITS-1:0]   result,
    output reg                   valid
);

// ── Internal State Machine ─────────────────────────────────
localparam IDLE    = 2'd0;
localparam COMPUTE = 2'd1;
localparam OUTPUT  = 2'd2;

reg [1:0]  state;
reg        mac_en, mac_clear;
wire [ACC_BITS-1:0] acc;

// ── MAC Unit Instantiation ────────────────────────────────
mac_unit u_mac (
    .clk     (clk),
    .rst_n   (rst_n),
    .en      (mac_en),
    .clear   (mac_clear),
    .A_in    (act_in),
    .W_mag   (w_mag),
    .W_sign  (w_sign),
    .mode    (mode),
    .acc_out (acc),
    .done    ()
);

// ── Result: accumulator + bias ────────────────────────────
assign result = acc + bias_in;

// ── FSM ───────────────────────────────────────────────────
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        state     <= IDLE;
        mac_en    <= 1'b0;
        mac_clear <= 1'b0;
        valid     <= 1'b0;
    end else begin
        case (state)
            IDLE: begin
                valid     <= 1'b0;
                mac_en    <= 1'b0;
                if (start) begin
                    mac_clear <= 1'b1;
                    state     <= COMPUTE;
                end
            end

            COMPUTE: begin
                mac_clear <= 1'b0;
                mac_en    <= 1'b1;
                // Controller drives act_in/w_mag/w_sign for each
                // of the 9*Cin cycles; when it de-asserts mac_en
                // externally we transition to OUTPUT.
                // (For simulation, controller uses 'start' as done)
                if (start) begin     // re-using start as "all done"
                    mac_en <= 1'b0;
                    state  <= OUTPUT;
                end
            end

            OUTPUT: begin
                valid <= 1'b1;
                state <= IDLE;
            end

            default: state <= IDLE;
        endcase
    end
end

endmodule
