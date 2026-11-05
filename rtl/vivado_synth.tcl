# ============================================================
# vivado_synth.tcl
# Automated Vivado Out-of-Context Synthesis Script
# Project: Sensitivity-Guided Approximate Multiplier Mapping
# Target:  Xilinx Zynq-7020 (PYNQ-Z2), xc7z020clg400-1
# ============================================================
# Run from Vivado Tcl Console or:
#   vivado -mode batch -source vivado_synth.tcl
# ============================================================

# ── Project Setup ────────────────────────────────────────────
set project_name "axm_cnn_accelerator"
set part_number  "xc7z020clg400-1"
set rtl_dir      "[file dirname [info script]]"
set output_dir   "$rtl_dir/vivado_output"

file mkdir $output_dir

# ── Create In-Memory Project ─────────────────────────────────
create_project -in_memory -part $part_number
set_property target_language Verilog [current_project]

# ── Add RTL Sources ──────────────────────────────────────────
read_verilog "$rtl_dir/axm_8x8.v"
read_verilog "$rtl_dir/mac_unit.v"
read_verilog "$rtl_dir/conv_pe.v"
read_verilog "$rtl_dir/layer_controller.v"
read_verilog "$rtl_dir/cnn_accelerator_top.v"

puts "RTL files loaded."

# ── Synthesis Settings ───────────────────────────────────────
set_property top cnn_accelerator_top [current_fileset]
set_property include_dirs $rtl_dir [current_fileset]

# ── Run Synthesis ─────────────────────────────────────────────
puts "Running synthesis for part: $part_number ..."
synth_design \
    -top cnn_accelerator_top \
    -part $part_number \
    -flatten_hierarchy rebuilt \
    -directive PerformanceOptimized

# ── Extract Utilization Reports ──────────────────────────────
puts "\n==== UTILIZATION REPORT ===="
report_utilization -hierarchical -file "$output_dir/utilization.rpt"
report_utilization

puts "\n==== TIMING REPORT ===="
report_timing_summary -max_paths 10 -file "$output_dir/timing.rpt"
report_timing_summary

puts "\n==== POWER REPORT ===="
report_power -file "$output_dir/power.rpt"

# ── Per-Module Synthesis (axm_8x8 standalone) ────────────────
# Synthesize axm_8x8 alone to get the exact LUT count
puts "\n\n==== STANDALONE axm_8x8 SYNTHESIS (4 modes) ===="

foreach mode_name {exact trunc compensated orbased} {
    set mode_idx 0
    if {$mode_name eq "trunc"}       { set mode_idx 1 }
    if {$mode_name eq "compensated"} { set mode_idx 2 }
    if {$mode_name eq "orbased"}     { set mode_idx 3 }

    # Synthesize with fixed mode input tied off
    synth_design \
        -top axm_8x8 \
        -part $part_number \
        -mode out_of_context \
        -flatten_hierarchy full

    report_utilization -quiet
    puts "Mode: $mode_name ($mode_idx) — see utilization above"
}

# ── Save Checkpoint ──────────────────────────────────────────
write_checkpoint -force "$output_dir/post_synth.dcp"
puts "\nCheckpoint saved: $output_dir/post_synth.dcp"

puts "\n=============================================="
puts "  Synthesis COMPLETE"
puts "  Reports in: $output_dir/"
puts "=============================================="
