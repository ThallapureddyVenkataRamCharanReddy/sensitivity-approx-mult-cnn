// ============================================================
// layer_controller.v
// Layer-Wise Approximate Multiplier Mode Controller
// ============================================================
// Stores the sensitivity-guided assignment for each layer
// and drives the correct mode[1:0] to the PE array.
//
// Assignment (from sensitivity analysis):
//   conv1 → 2'b00 (EXACT)        sensitivity = 1.000
//   conv2 → 2'b10 (COMPENSATED)  sensitivity = 0.180
//   conv3 → 2'b10 (COMPENSATED)  sensitivity = 0.008
//   conv4 → 2'b01 (TRUNCATED)    sensitivity = 0.014
//
// The layer_id input selects which layer is currently running:
//   0=conv1, 1=conv2, 2=conv3, 3=conv4
//
// This can be easily changed for any other assignment by
// modifying the MODE_TABLE parameter.
// ============================================================

`timescale 1ns/1ps

module layer_controller (
    input  wire [1:0] layer_id,   // which CNN layer is executing
    output reg  [1:0] mode        // multiplier mode for PE array
);

// Mode encoding:  00=EXACT, 01=TRUNC, 10=COMP, 11=ORBASED
// Sensitivity-guided assignment (your project result):
localparam [7:0] MODE_TABLE = {
    2'b01,   // layer 3 (conv4) → TRUNCATED   (sensitivity 0.014)
    2'b10,   // layer 2 (conv3) → COMPENSATED (sensitivity 0.008)
    2'b10,   // layer 1 (conv2) → COMPENSATED (sensitivity 0.180)
    2'b00    // layer 0 (conv1) → EXACT        (sensitivity 1.000)
};

always @(*) begin
    case (layer_id)
        2'd0: mode = MODE_TABLE[1:0];    // conv1 → EXACT
        2'd1: mode = MODE_TABLE[3:2];    // conv2 → COMPENSATED
        2'd2: mode = MODE_TABLE[5:4];    // conv3 → COMPENSATED
        2'd3: mode = MODE_TABLE[7:6];    // conv4 → TRUNCATED
        default: mode = 2'b00;           // safe default: EXACT
    endcase
end

endmodule
