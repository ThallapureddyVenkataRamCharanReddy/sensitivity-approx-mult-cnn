"""
build_review1_ppt.py
====================
Builds the Review-1 progress presentation for the capstone project,
using the exact template from the uploaded PPTX (Wood Type theme,
Rockwell/Rockwell Condensed fonts, 14-slide structure).
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.chart import XL_CHART_TYPE
import os

# ── Load the template ─────────────────────────────────────────────────────────
template_path = r'C:\Users\venka\.gemini\antigravity\brain\fdf2dd0f-da6e-4dcd-ab0c-7c5088961b1a\.user_uploaded\media_1791049363242.pptx'
prs = Presentation(template_path)

# Theme colors (from Wood Type)
ACCENT1 = RGBColor(0xD3, 0x48, 0x17)  # orange-red
ACCENT2 = RGBColor(0x9B, 0x2D, 0x1F)  # dark red
ACCENT3 = RGBColor(0xA2, 0x8E, 0x6A)  # olive/gold
DK2     = RGBColor(0x69, 0x64, 0x64)  # dark gray
BLACK   = RGBColor(0x00, 0x00, 0x00)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
GREEN   = RGBColor(0x22, 0x8B, 0x22)  # for status indicators
BLUE    = RGBColor(0x1F, 0x4E, 0x79)  # for emphasis

# ── Helper functions ──────────────────────────────────────────────────────────
def set_text_style(run, font_name="Rockwell", font_size=14, bold=False, color=None, italic=False):
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = color

def add_bullet(tf, text, level=0, font_size=14, bold=False, color=None, font_name="Rockwell"):
    para = tf.add_paragraph()
    para.level = level
    para.space_after = Pt(4)
    run = para.add_run()
    run.text = text
    set_text_style(run, font_name, font_size, bold, color)
    return para

def set_title(slide, text):
    """Set the title placeholder text with template-matching style."""
    title = slide.placeholders[0]
    title.text = ""
    run = title.text_frame.paragraphs[0].add_run()
    run.text = text
    set_text_style(run, "Rockwell Condensed", 28, bold=True, color=ACCENT1)

def get_content_tf(slide):
    """Get the content placeholder text frame."""
    return slide.placeholders[1].text_frame

def add_table_to_slide(slide, rows, cols, data, left=None, top=None, width=None, height=None,
                       header_color=ACCENT2, font_size=11):
    """Add a styled table to a slide."""
    if left is None: left = Emu(1069848)
    if top is None: top = Emu(2121408)
    if width is None: width = Emu(10058400)
    if height is None: height = Inches(0.35 * rows)
    
    table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    
    for ci in range(cols):
        for ri in range(rows):
            cell = table.cell(ri, ci)
            cell.text = ""
            para = cell.text_frame.paragraphs[0]
            run = para.add_run()
            run.text = str(data[ri][ci]) if ri < len(data) and ci < len(data[ri]) else ""
            run.font.name = "Times New Roman"
            run.font.size = Pt(font_size)
            
            if ri == 0:  # header row
                run.font.bold = True
                run.font.color.rgb = WHITE
                cell.fill.solid()
                cell.fill.fore_color.rgb = header_color
            else:
                run.font.color.rgb = BLACK
                if ri % 2 == 0:
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = RGBColor(0xF5, 0xF0, 0xE8)
            
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            para.space_before = Pt(2)
            para.space_after = Pt(2)
    
    return table

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1: TITLE SLIDE
# ══════════════════════════════════════════════════════════════════════════════
slide1 = prs.slides[0]

# Set title
title_shape = slide1.placeholders[0]
title_shape.text = ""
p = title_shape.text_frame.paragraphs[0]
run = p.add_run()
run.text = "Sensitivity-Guided Layer-Wise Approximate Multiplier Mapping for FPGA-Based CNN Accelerators"
set_text_style(run, "Rockwell Condensed", 24, bold=True, color=ACCENT1)

# Fill the table
for shape in slide1.shapes:
    if shape.has_table:
        table = shape.table
        table_data = [
            ("Cohort", "2024-2028"),
            ("Batch Number", "B4"),
            ("Supervisor", "Dr. Arun Nimmala, Dept. of ECE"),
            ("Team Details", ""),
            ("Student ID", "Name"),
            ("2320040083", "Velivala Keerthi"),
            ("2320040017", "T. Venkata Ram Charan Reddy"),
            ("2320040009", "Shaik Hanifa"),
            ("2320040095", "K. Dinesh"),
        ]
        for ri in range(len(table_data)):
            for ci in range(2):
                cell = table.cell(ri, ci)
                cell.text = ""
                para = cell.text_frame.paragraphs[0]
                run = para.add_run()
                run.text = table_data[ri][ci]
                run.font.name = "Times New Roman"
                run.font.size = Pt(12)
                if ri <= 3:
                    run.font.bold = True

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2: PROBLEM AND MOTIVATION
# ══════════════════════════════════════════════════════════════════════════════
slide2 = prs.slides[1]
set_title(slide2, "Problem and Motivation")
tf = get_content_tf(slide2)
tf.clear()

add_bullet(tf, "CNN inference is dominated by multiply-accumulate (MAC) operations", 0, 16, True, ACCENT2)
add_bullet(tf, "The multiplier is the single most power- and area-hungry component in the MAC datapath", 1, 14)
add_bullet(tf, "On PYNQ-Z2 (xc7z020): exact 8\u00d78 multiplier consumes 68 LUTs per instance", 1, 14)

add_bullet(tf, "Approximate multipliers trade controlled numerical error for hardware savings", 0, 16, True, ACCENT2)
add_bullet(tf, "CNNs are inherently error-resilient due to redundant feature representations", 1, 14)
add_bullet(tf, "Prior work shows 15\u201332% LUT savings are achievable with <1% accuracy loss", 1, 14)

add_bullet(tf, "The open problem: which layer gets which multiplier?", 0, 16, True, ACCENT1)
add_bullet(tf, "Different CNN layers have different sensitivity to arithmetic approximation", 1, 14)
add_bullet(tf, "Heterogeneous (layer-wise) assignment outperforms uniform approximation", 1, 14)
add_bullet(tf, "Existing methods require expensive evolutionary search (ALWANN: 7.5 CPU-days) or full GPU retraining (TRAM)", 1, 14)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3: OBJECTIVES AND SCOPE
# ══════════════════════════════════════════════════════════════════════════════
slide3 = prs.slides[2]
set_title(slide3, "Objectives and Scope")
tf = get_content_tf(slide3)
tf.clear()

add_bullet(tf, "Primary Objective", 0, 16, True, ACCENT1)
add_bullet(tf, "Develop a lightweight, single-pass sensitivity score S(l) = 0.5\u00b7Var(W) + 0.5\u00b7||\u2207L|| that predicts layer-wise tolerance to approximate multiplication \u2014 without retraining or iterative search", 1, 13)

add_bullet(tf, "Scope", 0, 16, True, ACCENT1)
add_bullet(tf, "Design and characterize a 4-design approximate multiplier library (8\u00d78 unsigned)", 1, 13)
add_bullet(tf, "Validate the sensitivity score via Spearman rank correlation against measured accuracy degradation", 1, 13)
add_bullet(tf, "Implement NSGA-II evolutionary search as a controlled baseline comparison", 1, 13)
add_bullet(tf, "Deploy the resulting heterogeneous accelerator on real PYNQ-Z2 FPGA hardware", 1, 13)

add_bullet(tf, "Constraints", 0, 16, True, ACCENT1)
add_bullet(tf, "Target network: 4-conv CNN on Fashion-MNIST (INT8 quantized)", 1, 13)
add_bullet(tf, "Target platform: Xilinx Zynq-7020 (PYNQ-Z2 board)", 1, 13)
add_bullet(tf, "No retraining allowed \u2014 post-training assignment only", 1, 13)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4: LITERATURE REVIEW AND GAP
# ══════════════════════════════════════════════════════════════════════════════
slide4 = prs.slides[3]
set_title(slide4, "Literature Review and Gap")
# Remove the content placeholder text
slide4.placeholders[1].text = ""

# Add comparison table
lit_data = [
    ["Paper", "Method", "Search-Free?", "Retrain-Free?", "Real FPGA?"],
    ["ALWANN [1]\n(ICCAD 2019)", "NSGA-II evolutionary\nsearch, 36-design library", "No\n(7.5 CPU-days)", "Yes", "No"],
    ["TRAM [2]\n(2026)", "Trainable multiplier\nvia gradient descent", "Yes", "No\n(full retraining)", "No"],
    ["Gradient Est. [3]\n(2025)", "LUT-1D/2D gradient\nestimators", "N/A\n(complementary)", "No", "No"],
    ["Sayadi [4]\n(Sci.Rep 2025)", "Weight variance\ndrop rule", "Yes", "No\n(gradual retrain)", "No"],
    ["Kumari [5]\n(2025)", "PYNQ HLS\naccelerator", "N/A\n(uniform only)", "Yes", "Yes\n(no selection)"],
    ["This Work", "Sensitivity score\n(Var+Grad)", "Yes\n(single pass)", "Yes", "Yes\n(PYNQ-Z2)"],
]
add_table_to_slide(slide4, 7, 5, lit_data, 
                   left=Emu(400000), top=Emu(2200000), 
                   width=Emu(11200000), height=Inches(3.5),
                   font_size=10)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5: PROPOSED METHODOLOGY / ARCHITECTURE
# ══════════════════════════════════════════════════════════════════════════════
slide5 = prs.slides[4]
set_title(slide5, "Proposed Methodology")
tf = get_content_tf(slide5)
tf.clear()

add_bullet(tf, "Step 1: Train baseline CNN, INT8 quantize (one-time)", 0, 15, True, ACCENT2)
add_bullet(tf, "4-conv layers: 16\u219232\u219264\u219264 filters, Fashion-MNIST, baseline ~84.7%", 1, 13)

add_bullet(tf, "Step 2: Compute per-layer sensitivity score (single forward + backward pass)", 0, 15, True, ACCENT2)
add_bullet(tf, "S(l) = 0.5 \u00d7 normalized(weight_variance) + 0.5 \u00d7 normalized(gradient_magnitude)", 1, 13)
add_bullet(tf, "Cost: ~0.2 seconds on CPU (vs. 7.5 CPU-days for ALWANN's NSGA-II)", 1, 13)

add_bullet(tf, "Step 3: Rank layers by S(l), assign multipliers", 0, 15, True, ACCENT2)
add_bullet(tf, "Highest S \u2192 Exact (most sensitive, protect accuracy)", 1, 13)
add_bullet(tf, "Medium S \u2192 Compensated (best accuracy-per-LUT ratio)", 1, 13)
add_bullet(tf, "Lowest S \u2192 Truncated (most aggressive savings, layer tolerates it)", 1, 13)

add_bullet(tf, "Step 4: Deploy heterogeneous multiplier assignment on FPGA", 0, 15, True, ACCENT2)
add_bullet(tf, "Processing Element (PE) with runtime-selectable AxM datapath on PYNQ-Z2", 1, 13)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6: TOOLS, RESOURCES AND SPECIFICATIONS
# ══════════════════════════════════════════════════════════════════════════════
slide6 = prs.slides[5]
set_title(slide6, "Tools, Resources and Specifications")
tf = get_content_tf(slide6)
tf.clear()

add_bullet(tf, "Hardware Platform", 0, 16, True, ACCENT1)
add_bullet(tf, "PYNQ-Z2 board (Xilinx Zynq-7020, xc7z020clg400-1)", 1, 13)
add_bullet(tf, "Dual ARM Cortex-A9 (PS) + Artix-7 FPGA fabric (PL)", 1, 13)

add_bullet(tf, "EDA & Simulation Tools", 0, 16, True, ACCENT1)
add_bullet(tf, "Xilinx Vivado 2023.2 \u2014 synthesis, implementation, bitstream generation", 1, 13)
add_bullet(tf, "Icarus Verilog \u2014 behavioral RTL simulation (65,536-pair exhaustive sweep)", 1, 13)
add_bullet(tf, "Yosys \u2014 open-source synthesis for gate count characterization", 1, 13)

add_bullet(tf, "Software Stack", 0, 16, True, ACCENT1)
add_bullet(tf, "Python 3.13 + TensorFlow/Keras (CNN training & quantization)", 1, 13)
add_bullet(tf, "NumPy, SciPy (sensitivity computation, Spearman correlation)", 1, 13)
add_bullet(tf, "DEAP library (NSGA-II evolutionary optimization)", 1, 13)

add_bullet(tf, "Dataset", 0, 16, True, ACCENT1)
add_bullet(tf, "Fashion-MNIST: 60K train / 10K test, 28\u00d728 grayscale, 10 classes", 1, 13)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7: WORK COMPLETED SINCE PREVIOUS REVIEW
# ══════════════════════════════════════════════════════════════════════════════
slide7 = prs.slides[6]
set_title(slide7, "Work Completed Since Previous Review")
tf = get_content_tf(slide7)
tf.clear()

add_bullet(tf, "Phase 0: Multiplier RTL Characterization \u2714", 0, 15, True, GREEN)
add_bullet(tf, "Designed 4 unsigned 8\u00d78 multiplier architectures from explicit partial-product arrays", 1, 13)
add_bullet(tf, "Exhaustive 65,536-pair Verilog simulation, real Vivado synthesis on PYNQ-Z2", 1, 13)
add_bullet(tf, "Key finding: Compensated dominates Truncated (same 56 LUTs, 35% lower error)", 1, 13, True)

add_bullet(tf, "Phase 0b: CNN Baseline & Quantization \u2714", 0, 15, True, GREEN)
add_bullet(tf, "4-conv CNN trained on Fashion-MNIST: 84.69% baseline accuracy", 1, 13)
add_bullet(tf, "Full INT8 post-training quantization pipeline implemented", 1, 13)

add_bullet(tf, "Phase 1: Sensitivity Scoring \u2714", 0, 15, True, GREEN)
add_bullet(tf, "5 candidate metrics (S1\u2013S5) computed; conv1 ranked most sensitive by S1/S2/S3/S5", 1, 13)

add_bullet(tf, "Phase 2: Layer-wise Validation (TRUNC=4) \u2714", 0, 15, True, GREEN)
add_bullet(tf, "12-cell accuracy-drop matrix measured on full 10,000-image test set", 1, 13)
add_bullet(tf, "Result: NO-GO \u2014 TRUNC=4 error too mild, all drops within noise (\u00b10.1\u20130.3%)", 1, 13, False, ACCENT1)

add_bullet(tf, "Phase 2b: Signal Amplification (TRUNC=6) \u25b6 In Progress", 0, 15, True, RGBColor(0xCC, 0x99, 0x00))
add_bullet(tf, "6.6\u00d7 error amplification confirmed; re-running full 12-cell sweep", 1, 13)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8: TECHNICAL RESULTS (1) \u2014 Multiplier Characterization
# ══════════════════════════════════════════════════════════════════════════════
slide8 = prs.slides[7]
set_title(slide8, "Technical Results: Multiplier Characterization")
slide8.placeholders[1].text = ""

# LUT Table
lut_data = [
    ["Design", "Mechanism", "LUTs (Vivado)", "\u0394 vs Exact", "Mean Error", "NMED"],
    ["Exact", "Full partial-product array", "68", "\u2014 (ref)", "0.00", "0.000000"],
    ["Truncated (T=4)", "Drop LSB columns 0\u20133", "56", "\u221217.6%", "\u221212.25", "0.000188"],
    ["Compensated (T=4)", "Truncation + rounding bias", "56", "\u221217.6%", "\u22124.25", "0.000125"],
    ["OR-based", "OR gates for low-weight PPs", "64", "\u22125.9%", "+24.50", "0.000377"],
    ["Truncated (T=6)", "Drop LSB columns 0\u20135", "~46*", "\u221232.5%", "\u221280.25", "0.001234"],
    ["Compensated (T=6)", "Truncation + bias (+32)", "~46*", "\u221232.5%", "\u221248.25", "0.000844"],
]
add_table_to_slide(slide8, 7, 6, lut_data, 
                   left=Emu(400000), top=Emu(2200000),
                   width=Emu(11200000), height=Inches(3.2),
                   font_size=10)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9: TECHNICAL RESULTS (2) \u2014 Sensitivity Scores & Layer Sweep
# ══════════════════════════════════════════════════════════════════════════════
slide9 = prs.slides[8]
set_title(slide9, "Technical Results: Sensitivity & Layer Sweep")
slide9.placeholders[1].text = ""

# Sensitivity scores table
sens_data = [
    ["Layer", "S1 (Wt Var)", "S2 (Grad)", "S3 (Combined)", "S4 (Act Var)", "S5 (Grad\u00d7Act)", "Rank (S3)"],
    ["conv1", "1.000", "1.000", "1.000", "0.000", "1.000", "1st (most sensitive)"],
    ["conv2", "0.296", "0.063", "0.180", "0.014", "0.042", "2nd"],
    ["conv3", "0.000", "0.016", "0.008", "0.084", "0.000", "4th"],
    ["conv4", "0.029", "0.000", "0.014", "1.000", "0.182", "3rd"],
]
add_table_to_slide(slide9, 5, 7, sens_data,
                   left=Emu(400000), top=Emu(2200000),
                   width=Emu(11200000), height=Inches(2.0),
                   font_size=10)

# Add interpretation note below
from pptx.util import Inches
txBox = slide9.shapes.add_textbox(Emu(400000), Emu(4400000), Emu(11200000), Inches(1.5))
tff = txBox.text_frame
tff.word_wrap = True
add_bullet(tff, "Key Observation: S1/S2/S3/S5 all rank conv1 as most sensitive (early layers capture", 0, 12, True, ACCENT2)
add_bullet(tff, "fundamental edge/texture features). S4 (activation variance) disagrees \u2014 ranks conv4 highest.", 0, 12, False)
add_bullet(tff, "TRUNC=4 NO-GO: accuracy drops (\u00b10.1\u20130.3%) were within noise floor. Correlation |rho| < 0.4 for all metrics.", 0, 12, True, ACCENT1)
add_bullet(tff, "TRUNC=6 re-run: 6.6\u00d7 error amplification should produce measurable, distinguishable drops.", 0, 12, False)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10: ANALYSIS AND COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
slide10 = prs.slides[9]
set_title(slide10, "Analysis and Comparison")
tf = get_content_tf(slide10)
tf.clear()

add_bullet(tf, "TRUNC=4 Correlation Results (Formal NO-GO)", 0, 16, True, ACCENT1)

corr_data = [
    ["Metric", "Spearman \u03c1", "p-value", "|rho|", "Verdict"],
    ["S1 (Weight Var)", "+0.200", "0.800", "0.200", "NO-GO"],
    ["S2 (Gradient)", "\u22120.400", "0.600", "0.400", "Borderline"],
    ["S3 (Combined)", "+0.200", "0.800", "0.200", "NO-GO"],
    ["S4 (Act Var)", "+0.400", "0.600", "0.400", "Borderline"],
    ["S5 (Grad\u00d7Act)", "+0.400", "0.600", "0.400", "Borderline"],
]
add_table_to_slide(slide10, 6, 5, corr_data,
                   left=Emu(600000), top=Emu(2600000),
                   width=Emu(10500000), height=Inches(2.5),
                   font_size=11)

txBox = slide10.shapes.add_textbox(Emu(600000), Emu(5200000), Emu(10500000), Inches(1.0))
tff = txBox.text_frame
tff.word_wrap = True
add_bullet(tff, "Diagnosis: TRUNC=4 approximation error (NMED=0.000188) is fully absorbed by CNN error resilience.", 0, 12, True, ACCENT2)
add_bullet(tff, "The accuracy drops are within statistical noise \u2014 you cannot correlate a score against noise.", 0, 12)
add_bullet(tff, "This is a characterization insight, not a method failure. Signal amplification via TRUNC=6 is the fix.", 0, 12, True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 11: INDIVIDUAL CONTRIBUTIONS
# ══════════════════════════════════════════════════════════════════════════════
slide11 = prs.slides[10]  # This is slide index 10 = template slide 11
set_title(slide11, "Individual Contributions")
tf = get_content_tf(slide11)
tf.clear()

add_bullet(tf, "Velivala Keerthi (2320040083) \u2014 RTL / Approximate Multipliers", 0, 14, True, ACCENT1)
add_bullet(tf, "Designed 4 Verilog multiplier architectures (exact, truncated, OR-based, compensated)", 1, 12)
add_bullet(tf, "65,536-pair exhaustive Icarus Verilog simulation & Vivado synthesis", 1, 12)
add_bullet(tf, "TRUNC=4 and TRUNC=6 library characterization with real LUT counts", 1, 12)

add_bullet(tf, "T. Venkata Ram Charan Reddy (2320040017) \u2014 CNN / Sensitivity Analysis", 0, 14, True, ACCENT1)
add_bullet(tf, "CNN training, INT8 quantization, sensitivity score computation (S1\u2013S5)", 1, 12)
add_bullet(tf, "Layer-wise validation sweep execution and correlation analysis", 1, 12)

add_bullet(tf, "Shaik Hanifa (2320040009) \u2014 NSGA-II / Optimization (Phase 3)", 0, 14, True, ACCENT1)
add_bullet(tf, "Literature survey on ALWANN and evolutionary AxM selection methods", 1, 12)
add_bullet(tf, "NSGA-II implementation planned post-GO gate", 1, 12)

add_bullet(tf, "K. Dinesh (2320040095) \u2014 Vivado / PYNQ / FPGA (Phase 4\u20136)", 0, 14, True, ACCENT1)
add_bullet(tf, "PYNQ-Z2 board setup and Vivado environment configuration", 1, 12)
add_bullet(tf, "AXI interface design and FPGA deployment planned post-GO gate", 1, 12)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 12: PROJECT PLAN AND NEXT MILESTONE
# ══════════════════════════════════════════════════════════════════════════════
slide12 = prs.slides[11]  # Template slide 12
set_title(slide12, "Project Plan and Next Milestone")
slide12.placeholders[1].text = ""

plan_data = [
    ["Phase", "Task", "Status", "Owner", "Timeline"],
    ["0", "Multiplier RTL + characterization", "\u2714 Complete", "Keerthi", "Weeks 1\u20133"],
    ["0b", "CNN baseline + INT8 quantization", "\u2714 Complete", "Charan", "Week 2"],
    ["1", "Sensitivity scoring (S1\u2013S5)", "\u2714 Complete", "Charan", "Week 2"],
    ["2", "12-cell sweep (TRUNC=4 \u2192 NO-GO)", "\u2714 Complete", "Charan", "Week 2\u20133"],
    ["2b", "TRUNC=6 re-run + GO/NO-GO gate", "\u25b6 In Progress", "Keerthi+Charan", "Week 4"],
    ["3", "NSGA-II baseline (256-space search)", "\u23f8 Gated on GO", "Hanifa", "Weeks 5\u20136"],
    ["4", "CNN accelerator RTL (PE + adder tree)", "\u23f8 Gated on GO", "Keerthi", "Weeks 5\u20137"],
    ["5", "Vivado block design + AXI interface", "\u23f8 Gated on Ph.4", "Dinesh", "Weeks 7\u20138"],
    ["6", "PYNQ-Z2 deployment + measurement", "\u23f8 Gated on Ph.5", "Dinesh", "Weeks 8\u20139"],
    ["7\u201310", "Results, manuscript, submission", "\u23f8 Pending", "All", "Weeks 9\u201312"],
]
add_table_to_slide(slide12, 11, 5, plan_data,
                   left=Emu(400000), top=Emu(2200000),
                   width=Emu(11200000), height=Inches(3.8),
                   font_size=10, header_color=ACCENT2)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 13: DOCUMENTATION AND PUBLICATION STATUS
# ══════════════════════════════════════════════════════════════════════════════
slide13 = prs.slides[12]  # Template slide 13
set_title(slide13, "Documentation and Publication Status")
tf = get_content_tf(slide13)
tf.clear()

add_bullet(tf, "Project Documentation", 0, 16, True, ACCENT1)
add_bullet(tf, "Project diary maintained with weekly entries (Weeks 1\u20134)", 1, 13)
add_bullet(tf, "All scripts version-controlled with fixed random seeds for reproducibility", 1, 13)
add_bullet(tf, "Phase 0 Experimental Protocol document: defines GO/NO-GO criteria, sequencing rules", 1, 13)

add_bullet(tf, "Manuscript Status", 0, 16, True, ACCENT1)
add_bullet(tf, "Draft abstract written (honest framing: 'preliminary', 'in progress')", 1, 13)
add_bullet(tf, "Introduction and Related Work sections drafted", 1, 13)
add_bullet(tf, "Results sections pending: awaiting TRUNC=6 validation and FPGA measurements", 1, 13)

add_bullet(tf, "Target Venues (Scopus-indexed)", 0, 16, True, ACCENT1)
add_bullet(tf, "Primary: IEEE regional conference (INDIACom, ICECCT, ISVLSI)", 1, 13)
add_bullet(tf, "Stretch: IEEE Access, Microprocessors and Microsystems (journal)", 1, 13)

add_bullet(tf, "Key Differentiator for Publication", 0, 16, True, ACCENT2)
add_bullet(tf, "Only paper combining: retraining-free + search-free + real FPGA + empirically validated metric", 1, 13, True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 14: CONCLUSION
# ══════════════════════════════════════════════════════════════════════════════
slide14 = prs.slides[13]  # Template slide 14
set_title(slide14, "Conclusion")
tf = get_content_tf(slide14)
tf.clear()

add_bullet(tf, "What Has Been Achieved", 0, 16, True, GREEN)
add_bullet(tf, "Complete RTL multiplier library with real Vivado-synthesized hardware metrics", 1, 13)
add_bullet(tf, "Compensated multiplier dominates Truncated: same 56 LUTs, 35% lower error", 1, 13, True)
add_bullet(tf, "CNN baseline trained (84.69%) with full INT8 quantization pipeline", 1, 13)
add_bullet(tf, "5 sensitivity metrics computed; 12-cell characterization matrix measured", 1, 13)
add_bullet(tf, "Honest NO-GO finding at TRUNC=4 \u2014 identified signal-to-noise threshold", 1, 13)

add_bullet(tf, "Major Finding", 0, 16, True, ACCENT1)
add_bullet(tf, "The CNN fully absorbs TRUNC=4 errors (NMED=0.000188); TRUNC=6 (NMED=0.001234, 6.6\u00d7 amplification) is needed to expose real layer sensitivity differences", 1, 13)

add_bullet(tf, "Next Milestone: Clear the GO/NO-GO Gate", 0, 16, True, ACCENT2)
add_bullet(tf, "Complete TRUNC=6 12-cell sweep \u2192 Spearman correlation \u2192 formal GO decision", 1, 13)
add_bullet(tf, "If GO: proceed to NSGA-II baseline + FPGA accelerator RTL", 1, 13)
add_bullet(tf, "If NO-GO: switch to perturbation-based metric or reframe around characterization matrix", 1, 13)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 15 (was slide 14 References in template): REFERENCES
# This reuses the last template slide
# ══════════════════════════════════════════════════════════════════════════════
# We need to add a new slide for references since slide 14 is now Conclusion
# Let's use the existing slide 14 layout (Title and Content) by adding a slide
layout = prs.slide_layouts[1]  # "Title and Content"
slide15 = prs.slides.add_slide(layout)
set_title(slide15, "References")
tf = get_content_tf(slide15)
tf.clear()

refs = [
    '[1] V. Mrazek, Z. Vasicek, L. Sekanina, M. Hanif, M. Shafique, "ALWANN: Automatic Layer-Wise Approximation of Deep Neural Network Accelerators without Retraining," IEEE/ACM ICCAD, 2019.',
    '[2] X. Meng et al., "TRAM: Trainable Approximate Multiplier for CNN Inference," IEEE Trans. VLSI Systems, 2026.',
    '[3] X. Meng et al., "Gradient Estimation for Approximate Multipliers in Deep Neural Networks," IEEE Access, 2025.',
    '[4] L. Sayadi et al., "Layer-Specific Approximate Multiplier Assignment Based on Weight Variance Analysis," Scientific Reports, 2025.',
    '[5] S. Kumari, A. Rao, "PYNQ-Based HLS Approximate CNN Accelerator on FPGA," IEEE Conf., 2025.',
]
for ref in refs:
    add_bullet(tf, ref, 0, 11, False, DK2)

# ══════════════════════════════════════════════════════════════════════════════
# SAVE
# ══════════════════════════════════════════════════════════════════════════════
output_path = r'C:\Users\venka\Downloads\reasearch\Review1_Presentation.pptx'
prs.save(output_path)
print(f"Saved: {output_path}")
print(f"Total slides: {len(prs.slides)}")
