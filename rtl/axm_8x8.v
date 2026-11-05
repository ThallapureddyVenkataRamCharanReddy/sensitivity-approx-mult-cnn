// ============================================================
// axm_8x8.v
// Approximate 8x8 Unsigned Multiplier — Multi-Mode Design
// ============================================================
// Mode select (mode[1:0]):
//   2'b00 : EXACT        — full 64 partial products
//   2'b01 : TRUNCATED    — drop columns 0..T-1
//   2'b10 : COMPENSATED  — truncated + 2^(T-1) rounding bias
//   2'b11 : OR-BASED     — OR gates for dropped columns
//
// Parameter T sets the truncation depth (default T=6).
// All modes share the same port list for easy IP-core reuse.
//
// Inputs  : A[7:0], B[7:0]  — unsigned 8-bit operands
//           mode[1:0]        — multiplier mode select
//           clk, rst_n       — clock and active-low reset
// Outputs : P[15:0]          — 16-bit product (registered)
// ============================================================

`timescale 1ns/1ps

module axm_8x8 #(
    parameter T = 6          // truncation depth (columns dropped)
)(
    input  wire        clk,
    input  wire        rst_n,
    input  wire [7:0]  A,
    input  wire [7:0]  B,
    input  wire [1:0]  mode,  // 00=exact,01=trunc,10=comp,11=orbased
    output reg  [15:0] P
);

// ── Partial-Product Generation ────────────────────────────────
// pp_and[i][j] = A[i] AND B[j]   (exact PP bit)
// pp_or [i][j] = A[i] OR  B[j]   (OR-based PP bit)
wire pp_and [0:7][0:7];
wire pp_or  [0:7][0:7];

genvar gi, gj;
generate
    for (gi = 0; gi < 8; gi = gi + 1) begin : gen_i
        for (gj = 0; gj < 8; gj = gj + 1) begin : gen_j
            assign pp_and[gi][gj] = A[gi] & B[gj];
            assign pp_or [gi][gj] = A[gi] | B[gj];
        end
    end
endgenerate

// ── Column Sums ───────────────────────────────────────────────
// For each output column k (0..14), sum all pp_and bits where i+j==k.
// We use integer arrays in an always block for clarity.
// synthesis tools will optimize this into a carry-save adder tree.
integer k, i, j;
reg [15:0] sum_exact;
reg [15:0] sum_dropped_and;   // contribution from dropped columns (AND)
reg [15:0] sum_dropped_or;    // contribution from dropped columns (OR)

always @(*) begin
    sum_exact       = 16'd0;
    sum_dropped_and = 16'd0;
    sum_dropped_or  = 16'd0;

    for (k = 0; k < 16; k = k + 1) begin
        for (i = 0; i < 8; i = i + 1) begin
            j = k - i;
            if (j >= 0 && j < 8) begin
                sum_exact = sum_exact + (pp_and[i][j] << k);
                if (k < T) begin
                    sum_dropped_and = sum_dropped_and + (pp_and[i][j] << k);
                    sum_dropped_or  = sum_dropped_or  + (pp_or [i][j] << k);
                end
            end
        end
    end
end

// ── Mode Multiplexer (combinational) ──────────────────────────
localparam [15:0] COMP_BIAS = (1 << (T-1));  // 2^(T-1) = 32 for T=6

reg [15:0] P_comb;
always @(*) begin
    case (mode)
        2'b00: P_comb = sum_exact;                             // EXACT
        2'b01: P_comb = sum_exact - sum_dropped_and;           // TRUNCATED
        2'b10: P_comb = sum_exact - sum_dropped_and + COMP_BIAS; // COMPENSATED
        2'b11: P_comb = sum_exact - sum_dropped_and
                        + sum_dropped_or;                      // OR-BASED
        default: P_comb = sum_exact;
    endcase
end

// ── Output Register ───────────────────────────────────────────
always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        P <= 16'd0;
    else
        P <= P_comb;
end

endmodule
