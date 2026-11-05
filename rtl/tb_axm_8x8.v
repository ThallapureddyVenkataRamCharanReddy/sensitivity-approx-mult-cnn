// ============================================================
// tb_axm_8x8.v
// Exhaustive Testbench for axm_8x8 Multi-Mode Multiplier
// ============================================================
// Tests ALL 65,536 input pairs for all 4 modes.
// Compares outputs against reference model.
// Reports: total tests, mismatches, pass/fail per mode.
//
// Run with: iverilog -o tb_axm tb_axm_8x8.v axm_8x8.v && vvp tb_axm
// ============================================================

`timescale 1ns/1ps

module tb_axm_8x8;

// ── DUT Ports ─────────────────────────────────────────────
reg        clk, rst_n;
reg  [7:0] A, B;
reg  [1:0] mode;
wire [15:0] P;

// ── DUT Instantiation ─────────────────────────────────────
axm_8x8 #(.T(6)) dut (
    .clk   (clk),
    .rst_n (rst_n),
    .A     (A),
    .B     (B),
    .mode  (mode),
    .P     (P)
);

// ── Clock: 10ns period (100 MHz) ──────────────────────────
initial clk = 0;
always #5 clk = ~clk;

// ── Reference Functions ───────────────────────────────────
// These mirror the Python behavioral model (0 mismatches verified)
function automatic [15:0] ref_exact;
    input [7:0] a, b;
    ref_exact = a * b;
endfunction

function automatic [15:0] ref_trunc;
    input [7:0] a, b;
    integer k, i, j;
    reg [15:0] s_drop;
    begin
        s_drop = 0;
        for (k = 0; k < 6; k = k + 1)
            for (i = 0; i < 8; i = i + 1) begin
                j = k - i;
                if (j >= 0 && j < 8)
                    s_drop = s_drop + ((a[i] & b[j]) << k);
            end
        ref_trunc = (a * b) - s_drop;
    end
endfunction

function automatic [15:0] ref_comp;
    input [7:0] a, b;
    ref_comp = ref_trunc(a, b) + 16'd32;  // T=6 → bias = 2^5 = 32
endfunction

function automatic [15:0] ref_orbased;
    input [7:0] a, b;
    integer k, i, j;
    reg [15:0] s_or;
    begin
        s_or = 0;
        for (k = 0; k < 6; k = k + 1)
            for (i = 0; i < 8; i = i + 1) begin
                j = k - i;
                if (j >= 0 && j < 8)
                    s_or = s_or + ((a[i] | b[j]) << k);
            end
        ref_orbased = ref_trunc(a, b) + s_or;
    end
endfunction

// ── Test Variables ────────────────────────────────────────
integer a_val, b_val;
integer total, mismatch_exact, mismatch_trunc;
integer mismatch_comp, mismatch_or;
reg [15:0] expected;

// ── Test Sequence ─────────────────────────────────────────
initial begin
    $display("=================================================");
    $display("  axm_8x8 Exhaustive Testbench (T=6)");
    $display("  Testing all 65,536 input pairs × 4 modes");
    $display("=================================================");

    // Reset
    rst_n = 0; A = 0; B = 0; mode = 2'b00;
    repeat(4) @(posedge clk);
    rst_n = 1;
    @(posedge clk);

    total          = 0;
    mismatch_exact = 0;
    mismatch_trunc = 0;
    mismatch_comp  = 0;
    mismatch_or    = 0;

    // ── Mode 0: EXACT ──────────────────────────────────────
    $display("\n[1/4] Testing EXACT mode (mode=2'b00)...");
    mode = 2'b00;
    for (a_val = 0; a_val < 256; a_val = a_val + 1) begin
        for (b_val = 0; b_val < 256; b_val = b_val + 1) begin
            A = a_val[7:0]; B = b_val[7:0];
            @(posedge clk); #1;
            expected = ref_exact(A, B);
            if (P !== expected) begin
                mismatch_exact = mismatch_exact + 1;
                if (mismatch_exact <= 5)
                    $display("  MISMATCH: A=%0d B=%0d Got=%0d Exp=%0d",
                             A, B, P, expected);
            end
            total = total + 1;
        end
    end
    $display("  EXACT   : %0d tests, %0d mismatches %s",
             65536, mismatch_exact,
             (mismatch_exact == 0) ? "PASS" : "FAIL");

    // ── Mode 1: TRUNCATED ─────────────────────────────────
    $display("\n[2/4] Testing TRUNCATED mode (mode=2'b01)...");
    mode = 2'b01;
    for (a_val = 0; a_val < 256; a_val = a_val + 1) begin
        for (b_val = 0; b_val < 256; b_val = b_val + 1) begin
            A = a_val[7:0]; B = b_val[7:0];
            @(posedge clk); #1;
            expected = ref_trunc(A, B);
            if (P !== expected) begin
                mismatch_trunc = mismatch_trunc + 1;
                if (mismatch_trunc <= 5)
                    $display("  MISMATCH: A=%0d B=%0d Got=%0d Exp=%0d",
                             A, B, P, expected);
            end
        end
    end
    $display("  TRUNCATED: %0d tests, %0d mismatches %s",
             65536, mismatch_trunc,
             (mismatch_trunc == 0) ? "PASS" : "FAIL");

    // ── Mode 2: COMPENSATED ───────────────────────────────
    $display("\n[3/4] Testing COMPENSATED mode (mode=2'b10)...");
    mode = 2'b10;
    for (a_val = 0; a_val < 256; a_val = a_val + 1) begin
        for (b_val = 0; b_val < 256; b_val = b_val + 1) begin
            A = a_val[7:0]; B = b_val[7:0];
            @(posedge clk); #1;
            expected = ref_comp(A, B);
            if (P !== expected) begin
                mismatch_comp = mismatch_comp + 1;
                if (mismatch_comp <= 5)
                    $display("  MISMATCH: A=%0d B=%0d Got=%0d Exp=%0d",
                             A, B, P, expected);
            end
        end
    end
    $display("  COMPENSATED: %0d tests, %0d mismatches %s",
             65536, mismatch_comp,
             (mismatch_comp == 0) ? "PASS" : "FAIL");

    // ── Mode 3: OR-BASED ──────────────────────────────────
    $display("\n[4/4] Testing OR-BASED mode (mode=2'b11)...");
    mode = 2'b11;
    for (a_val = 0; a_val < 256; a_val = a_val + 1) begin
        for (b_val = 0; b_val < 256; b_val = b_val + 1) begin
            A = a_val[7:0]; B = b_val[7:0];
            @(posedge clk); #1;
            expected = ref_orbased(A, B);
            if (P !== expected) begin
                mismatch_or = mismatch_or + 1;
                if (mismatch_or <= 5)
                    $display("  MISMATCH: A=%0d B=%0d Got=%0d Exp=%0d",
                             A, B, P, expected);
            end
        end
    end
    $display("  OR-BASED: %0d tests, %0d mismatches %s",
             65536, mismatch_or,
             (mismatch_or == 0) ? "PASS" : "FAIL");

    // ── Final Summary ─────────────────────────────────────
    $display("\n=================================================");
    $display("  FINAL SUMMARY");
    $display("=================================================");
    $display("  EXACT       : %0d mismatches", mismatch_exact);
    $display("  TRUNCATED   : %0d mismatches", mismatch_trunc);
    $display("  COMPENSATED : %0d mismatches", mismatch_comp);
    $display("  OR-BASED    : %0d mismatches", mismatch_or);

    if ((mismatch_exact + mismatch_trunc + mismatch_comp + mismatch_or) == 0)
        $display("\n  *** ALL TESTS PASSED — RTL verified ***");
    else
        $display("\n  *** FAILURES DETECTED — review RTL ***");
    $display("=================================================");

    $finish;
end

endmodule
