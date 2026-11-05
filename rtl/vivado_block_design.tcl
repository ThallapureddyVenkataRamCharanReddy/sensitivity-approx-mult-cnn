# ============================================================
# vivado_block_design.tcl
# Full PYNQ-Z2 Block Design for CNN Accelerator
# ============================================================
# Creates:
#   - Zynq PS (xc7z020) with DDR + UART + AXI HP port
#   - AXI DMA controller (S2MM + MM2S channels)
#   - CNN Accelerator IP (our custom RTL wrapped as AXI-Stream IP)
#   - AXI Interconnect + SmartConnect
#   - Interrupt lines to PS
#
# Run in Vivado Tcl Console:
#   source vivado_block_design.tcl
#
# Target board: PYNQ-Z2 (xc7z020clg400-1)
# ============================================================

# ── Project Setup ─────────────────────────────────────────────
set proj_name   "cnn_axm_accelerator"
set proj_dir    "./vivado_project"
set part        "xc7z020clg400-1"
set board_part  "tul.com.tw:pynq-z2:part0:1.0"

create_project $proj_name $proj_dir -part $part -force
set_property board_part $board_part [current_project]

# ── Add RTL Sources as IP ──────────────────────────────────────
set rtl_dir "[file dirname [info script]]"
add_files -norecurse [glob $rtl_dir/rtl/*.v]
update_compile_order -fileset sources_1

# ── Package Custom IP (CNN Accelerator) ───────────────────────
# Wrap cnn_accelerator_top as AXI-Stream IP core
ipx::package_project \
    -root_dir "$proj_dir/ip/cnn_axm_ip" \
    -vendor   "kluniversity.edu.in" \
    -library  "user" \
    -taxonomy "/UserIP" \
    -import_files

set_property top cnn_accelerator_top [current_fileset]
ipx::create_xgui_files [ipx::current_core]
ipx::update_checksums  [ipx::current_core]
ipx::save_core         [ipx::current_core]
set_property ip_repo_paths "$proj_dir/ip" [current_project]
update_ip_catalog

puts "Custom IP packaged successfully."

# ── Create Block Design ───────────────────────────────────────
create_bd_design "cnn_axm_bd"
open_bd_design   "cnn_axm_bd"

# ── Add Zynq PS ───────────────────────────────────────────────
set ps [create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 \
        processing_system7_0]

# Apply PYNQ-Z2 board preset
apply_bd_automation -rule xilinx.com:bd_rule:processing_system7 \
    -config { make_external "FIXED_IO, DDR" apply_board_preset "1" } \
    $ps

# Enable AXI HP0 port for DMA (high-performance slave port)
set_property -dict [list \
    CONFIG.PCW_USE_S_AXI_HP0 {1} \
    CONFIG.PCW_USE_FABRIC_INTERRUPT {1} \
    CONFIG.PCW_IRQ_F2P_INTR {1} \
    CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ {100} \
] $ps

# ── Add AXI DMA Controller ────────────────────────────────────
set dma [create_bd_cell -type ip \
         -vlnv xilinx.com:ip:axi_dma:7.1 axi_dma_0]

set_property -dict [list \
    CONFIG.c_include_sg          {0} \
    CONFIG.c_sg_include_stscntrl_strm {0} \
    CONFIG.c_m_axi_mm2s_data_width {32} \
    CONFIG.c_m_axis_mm2s_tdata_width {32} \
    CONFIG.c_mm2s_burst_size     {16} \
    CONFIG.c_s2mm_burst_size     {16} \
    CONFIG.c_m_axi_s2mm_data_width {32} \
    CONFIG.c_s_axis_s2mm_tdata_width {32} \
] $dma

# ── Add CNN Accelerator IP ────────────────────────────────────
set axm_ip [create_bd_cell -type ip \
            -vlnv kluniversity.edu.in:user:cnn_accelerator_top:1.0 \
            cnn_axm_0]

# ── AXI SmartConnect (GP0 → DMA → PS HP0) ────────────────────
set smartcon [create_bd_cell -type ip \
              -vlnv xilinx.com:ip:smartconnect:1.0 smartconnect_0]
set_property CONFIG.NUM_SI {1} $smartcon

# ── AXI Interconnect (HP0 ← DMA) ─────────────────────────────
set intercon [create_bd_cell -type ip \
              -vlnv xilinx.com:ip:axi_interconnect:2.1 axi_interconnect_0]
set_property -dict [list \
    CONFIG.NUM_SI {2} \
    CONFIG.NUM_MI {1} \
] $intercon

# ── Clock and Reset ───────────────────────────────────────────
apply_bd_automation \
    -rule xilinx.com:bd_rule:clkrst \
    -config { Clk "/processing_system7_0/FCLK_CLK0 (100 MHz)" } \
    [get_bd_pins axi_dma_0/s_axi_lite_aclk]

# ── Connect AXI Interfaces ────────────────────────────────────
# PS M_AXI_GP0 → SmartConnect → DMA S_AXI_LITE (control)
connect_bd_intf_net \
    [get_bd_intf_pins processing_system7_0/M_AXI_GP0] \
    [get_bd_intf_pins smartconnect_0/S00_AXI]
connect_bd_intf_net \
    [get_bd_intf_pins smartconnect_0/M00_AXI] \
    [get_bd_intf_pins axi_dma_0/S_AXI_LITE]

# DMA MM2S (memory→stream) → CNN Accelerator S_AXIS (input)
connect_bd_intf_net \
    [get_bd_intf_pins axi_dma_0/M_AXIS_MM2S] \
    [get_bd_intf_pins cnn_axm_0/S_AXIS]

# CNN Accelerator M_AXIS (output) → DMA S2MM (stream→memory)
connect_bd_intf_net \
    [get_bd_intf_pins cnn_axm_0/M_AXIS] \
    [get_bd_intf_pins axi_dma_0/S_AXIS_S2MM]

# DMA AXI masters → AXI Interconnect → PS S_AXI_HP0
connect_bd_intf_net \
    [get_bd_intf_pins axi_dma_0/M_AXI_MM2S] \
    [get_bd_intf_pins axi_interconnect_0/S00_AXI]
connect_bd_intf_net \
    [get_bd_intf_pins axi_dma_0/M_AXI_S2MM] \
    [get_bd_intf_pins axi_interconnect_0/S01_AXI]
connect_bd_intf_net \
    [get_bd_intf_pins axi_interconnect_0/M00_AXI] \
    [get_bd_intf_pins processing_system7_0/S_AXI_HP0]

# ── Interrupt Lines ───────────────────────────────────────────
# DMA MM2S complete + S2MM complete → PS interrupt controller
create_bd_cell -type ip -vlnv xilinx.com:ip:xlconcat:2.1 xlconcat_0
set_property CONFIG.NUM_PORTS {2} [get_bd_cells xlconcat_0]

connect_bd_net \
    [get_bd_pins axi_dma_0/mm2s_introut] \
    [get_bd_pins xlconcat_0/In0]
connect_bd_net \
    [get_bd_pins axi_dma_0/s2mm_introut] \
    [get_bd_pins xlconcat_0/In1]
connect_bd_net \
    [get_bd_pins xlconcat_0/dout] \
    [get_bd_pins processing_system7_0/IRQ_F2P]

# ── Validate and Save ─────────────────────────────────────────
validate_bd_design
save_bd_design
make_wrapper -files [get_files cnn_axm_bd.bd] -top
add_files -norecurse "$proj_dir/cnn_axm_accelerator.srcs/sources_1/bd/cnn_axm_bd/hdl/cnn_axm_bd_wrapper.v"
set_property top cnn_axm_bd_wrapper [current_fileset]
update_compile_order -fileset sources_1

# ── Generate Bitstream ────────────────────────────────────────
puts "\nRunning synthesis, implementation, and bitstream generation..."
puts "This will take 15-30 minutes on a typical PC."
launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1

# ── Export Hardware (for PYNQ) ────────────────────────────────
set bit_file "$proj_dir/cnn_axm_accelerator.runs/impl_1/cnn_axm_bd_wrapper.bit"
set hwh_file "$proj_dir/cnn_axm_accelerator.gen/sources_1/bd/cnn_axm_bd/hw_handoff/cnn_axm_bd.hwh"

file copy -force $bit_file "$proj_dir/cnn_axm.bit"
file copy -force $hwh_file "$proj_dir/cnn_axm.hwh"

puts "\n=================================================="
puts "  BITSTREAM GENERATION COMPLETE"
puts "  Copy to PYNQ-Z2 board:"
puts "    cnn_axm.bit"
puts "    cnn_axm.hwh"
puts "=================================================="
