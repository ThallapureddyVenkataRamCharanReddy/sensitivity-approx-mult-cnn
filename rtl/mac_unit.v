// ============================================================
// mac_unit.v
// Multiply-Accumulate Unit for CNN Processing Element
// ============================================================
// Performs:   ACC = ACC + sign(W) * AxM(|A|, |W|)
//
// Ports:
//   clk, rst_n    — clock, active-low synchronous reset
//   en            — enable accumulation this cycle
//   clear         — synchronous clear accumulator to zero
//   A_in[7:0]     — unsigned quantized activation (INT8)
//   W_mag[7:0]    — unsigned magnitude of weight   (INT8)
//   W_sign        — 1-bit sign of weight (1=negative, 0=positive)
//   mode[1:0]     — multiplier mode (passed to axm_8x8)
//   acc_out[31:0] — accumulated integer result (signed)
//   done          — accumulation complete strobe (1 cycle pulse)
// ============================================================

`timescale 1ns/1ps

module mac_unit (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        en,
    input  wire        clear,
    input  wire [7:0]  A_in,
    input  wire [7:0]  W_mag,
    input  wire        W_sign,    // 0=positive, 1=negative
    input  wire [1:0]  mode,
    output reg  [31:0] acc_out,
    output reg         done
);

// ── Approximate Multiplier Instance ──────────────────────────
wire [15:0] product;

axm_8x8 #(.T(6)) u_axm (
    .clk   (clk),
    .rst_n (rst_n),
    .A     (A_in),
    .B     (W_mag),
    .mode  (mode),
    .P     (product)
);

// ── Signed Extension & Accumulation ──────────────────────────
// product is always non-negative (unsigned × unsigned)
// W_sign determines whether to add or subtract
wire [31:0] product_ext = {{16{1'b0}}, product};
wire [31:0] signed_product = W_sign ? (~product_ext + 1'b1) : product_ext;

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        acc_out <= 32'sd0;
        done    <= 1'b0;
    end else if (clear) begin
        acc_out <= 32'sd0;
        done    <= 1'b0;
    end else if (en) begin
        acc_out <= acc_out + $signed(signed_product);
        done    <= 1'b0;
    end else begin
        done    <= 1'b0;
    end
end

endmodule
