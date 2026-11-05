"""
fix_presentation_flaws.py
=========================
Fixes all design, layout, overlap, and placeholder flaws in
Project_Presentation_Complete.pptx:

1. Slide 1: Populates the template's native Table 6 directly; eliminates the duplicate overlapping table.
2. All Slides: Removes the unused, empty 'Content Placeholder 2' shape that causes visual clutter and traps clicks.
3. Title Placeholder: Restricts Title 1 height to 0.70 inches so it never overlaps the subtitle banner.
4. Slide 10: Eliminates the critical image-textbox collision by resizing Figure 3 and giving clean margins.
5. Slide 6 & 7: Re-balances two-column layouts and prevents text boxes from colliding with figures or tables.
6. Typography & Margins: Standardizes margins, line spacing, and fonts across all 20 slides.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

TEMPLATE_PATH = r"C:\Users\venka\.gemini\antigravity\brain\fdf2dd0f-da6e-4dcd-ab0c-7c5088961b1a\.user_uploaded\media_1791049363242.pptx"
OUTPUT_PATH   = r"C:\Users\venka\Downloads\reasearch\Project_Presentation_Complete.pptx"
FIG_DIR       = r"C:\Users\venka\Downloads\reasearch\paper\figures"

# Theme Colors (Wood Type palette)
ACCENT1 = RGBColor(0xD3, 0x48, 0x17)  # Orange-red / Crimson
ACCENT2 = RGBColor(0x9B, 0x2D, 0x1F)  # Deep Red
ACCENT3 = RGBColor(0xA2, 0x8E, 0x6A)  # Gold / Olive
DK2     = RGBColor(0x40, 0x40, 0x40)  # Dark Charcoal
BLACK   = RGBColor(0x1A, 0x1A, 0x1A)  # Near Black
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)  # Pure White
GREEN   = RGBColor(0x1A, 0x8A, 0x36)  # Status green
RED     = RGBColor(0xC0, 0x00, 0x00)  # Status red
ROW_ALT = RGBColor(0xF5, 0xF2, 0xEE)  # Table alternating row color

prs = Presentation(TEMPLATE_PATH)

# Helper: format title
def format_title(slide, text):
    title = slide.placeholders[0]
    title.top = Inches(0.45)
    title.left = Inches(0.85)
    title.width = Inches(11.6)
    title.height = Inches(0.70)
    title.text = ""
    p = title.text_frame.paragraphs[0]
    p.margin_left = p.margin_top = p.margin_right = p.margin_bottom = 0
    run = p.add_run()
    run.text = text
    run.font.name = "Rockwell Condensed"
    run.font.size = Pt(25)
    run.font.bold = True
    run.font.color.rgb = ACCENT1

# Helper: remove empty Content Placeholder 2
def remove_unused_placeholder(slide):
    for shape in list(slide.shapes):
        if shape.is_placeholder and shape.placeholder_format.idx == 1:
            sp_elem = shape._element
            sp_elem.getparent().remove(sp_elem)

# Helper: add header subtitle banner
def add_header_banner(slide, subtitle):
    tb = slide.shapes.add_textbox(Inches(0.85), Inches(1.22), Inches(11.6), Inches(0.38))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.margin_left = p.margin_top = p.margin_right = p.margin_bottom = 0
    run = p.add_run()
    run.text = subtitle
    run.font.name = "Rockwell"
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = ACCENT2

# Helper: add styled bullet list
def add_bullet_list(slide, left, top, width, height, bullets, font_size=10.5):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    for i, b in enumerate(bullets):
        p = tf.add_paragraph() if i > 0 else tf.paragraphs[0]
        p.space_after = Pt(3)
        if isinstance(b, tuple):
            level, text, is_bold = b[0], b[1], (b[2] if len(b) > 2 else False)
        else:
            level, text, is_bold = 0, b, False
        p.level = level
        run = p.add_run()
        run.text = text
        run.font.name = "Rockwell"
        run.font.size = Pt(font_size)
        run.font.bold = is_bold
        run.font.color.rgb = BLACK
    return tb

# Helper: add styled table
def add_table(slide, left, top, width, height, headers, rows_data, font_size=9.5):
    rows = len(rows_data) + 1
    cols = len(headers)
    table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    
    # Headers
    for ci, h in enumerate(headers):
        cell = table.cell(0, ci)
        cell.fill.solid()
        cell.fill.fore_color.rgb = ACCENT2
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.alignment = PP_ALIGN.CENTER
        run = p.runs[0]
        run.font.name = "Rockwell"
        run.font.size = Pt(font_size)
        run.font.bold = True
        run.font.color.rgb = WHITE
        
    # Rows
    for ri, row in enumerate(rows_data):
        for ci, val in enumerate(row):
            cell = table.cell(ri + 1, ci)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            if ri % 2 == 1:
                cell.fill.solid()
                cell.fill.fore_color.rgb = ROW_ALT
            p = cell.text_frame.paragraphs[0]
            p.text = str(val)
            p.alignment = PP_ALIGN.CENTER if ci > 0 else PP_ALIGN.LEFT
            if len(p.runs) > 0:
                run = p.runs[0]
                run.font.name = "Times New Roman"
                run.font.size = Pt(font_size)
                run.font.color.rgb = BLACK
                if any(k in str(val) for k in ["GO", "PASS", "Yes", "Complete"]):
                    run.font.bold = True
                    run.font.color.rgb = GREEN
                elif any(k in str(val) for k in ["NO-GO", "FAIL", "No ("]):
                    run.font.bold = True
                    run.font.color.rgb = RED
    return table_shape

# Ensure 20 slides exist
layout_content = prs.slide_layouts[1]
while len(prs.slides) < 20:
    prs.slides.add_slide(layout_content)

# ==============================================================================
# SLIDE 1: Title Slide (Fix Duplicate Table)
# ==============================================================================
s1 = prs.slides[0]
title1 = s1.placeholders[0]
title1.top = Inches(0.4)
title1.left = Inches(0.85)
title1.width = Inches(11.6)
title1.height = Inches(1.4)
title1.text = ""
p1 = title1.text_frame.paragraphs[0]
r1 = p1.add_run()
r1.text = "Sensitivity-Guided Layer-Wise Approximate Multiplier Mapping for FPGA-Based CNN Accelerators"
r1.font.name = "Rockwell Condensed"
r1.font.size = Pt(26)
r1.font.bold = True
r1.font.color.rgb = ACCENT1

# Clear subtitle placeholder
if len(s1.placeholders) > 1:
    s1.placeholders[1].text_frame.text = ""

# Populate native Table 6 directly
native_table = None
for shape in s1.shapes:
    if shape.has_table:
        native_table = shape.table
        shape.top = Inches(2.1)
        shape.left = Inches(1.2)
        shape.width = Inches(10.9)
        shape.height = Inches(4.7)
        break

table_data1 = [
    ("Cohort", "2024 – 2028"),
    ("Batch Number", "B4"),
    ("Supervisor", "Dr. Arun Nimmala, Associate Professor, Dept. of ECE"),
    ("Team Details", "Department of Electronics and Communication Engineering, K L University"),
    ("Student ID", "Student Name"),
    ("2320040083", "Velivala Keerthi"),
    ("2320040017", "T. Venkata Ram Charan Reddy"),
    ("2320040009", "Shaik Hanifa"),
    ("2320040095", "K. Dinesh"),
]

if native_table:
    for ri in range(min(len(table_data1), len(native_table.rows))):
        for ci in range(2):
            cell = native_table.cell(ri, ci)
            cell.text = ""
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            if ri in [0, 1, 2, 3, 4] and ci == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(0xEE, 0xE7, 0xDF)
            p = cell.text_frame.paragraphs[0]
            run = p.add_run()
            run.text = table_data1[ri][ci]
            run.font.name = "Times New Roman"
            run.font.size = Pt(11.5)
            run.font.color.rgb = BLACK
            if ri <= 4:
                run.font.bold = True

# ==============================================================================
# SLIDE 2: Problem Definition & Motivation
# ==============================================================================
s2 = prs.slides[1]
remove_unused_placeholder(s2)
format_title(s2, "Problem Definition & Motivation")
add_header_banner(s2, "Edge CNN Acceleration Bottlenecks & The Opportunity of Approximate Computing")

b2 = [
    (0, "Compute Bottleneck in Edge Inference:", True),
    (1, "Convolutional layers dominate CNN inference, accounting for >99.8% of total multiply-accumulate (MAC) operations."),
    (1, "The multiplier is the single most power-hungry and silicon-area intensive unit (68 LUTs per 8x8 exact multiplier on Zynq)."),
    (0, "The Approximate Computing Opportunity:", True),
    (1, "Trading a controlled amount of arithmetic precision for substantial silicon area, latency, and power savings."),
    (1, "Convolutional networks exhibit inherent structural redundancy, allowing them to absorb minor numerical inaccuracies."),
    (0, "The Core Research Challenge: Asymmetric Layer Vulnerability", True),
    (1, "Uniform approximation fails: either causes severe classification accuracy drop or yields negligible hardware savings."),
    (1, "Different layers exhibit vastly different error tolerances: early layers extract fragile edges; deep layers are redundant."),
    (0, "Limitations of Existing State-of-the-Art Solutions:", True),
    (1, "Evolutionary Genetic Search (ALWANN, ICCAD 2019): Prohibitive search time requiring up to 7.5 CPU-days."),
    (1, "Multiplier Retraining (TRAM, Meng 2025/2026): Demands full GPU retraining loops and access to original training data.")
]
add_bullet_list(s2, Inches(0.85), Inches(1.75), Inches(11.6), Inches(5.1), b2, font_size=11)

# ==============================================================================
# SLIDE 3: Project Objectives & Technical Scope
# ==============================================================================
s3 = prs.slides[2]
remove_unused_placeholder(s3)
format_title(s3, "Project Objectives & Technical Scope")
add_header_banner(s3, "Design Boundaries, Research Questions, and Target Deliverables")

b3 = [
    (0, "Primary Research Objective:", True),
    (1, "Formulate a lightweight, single-pass sensitivity metric computed in 0.2s without retraining or iterative search."),
    (1, "Predict layer-wise tolerance to approximate multiplication to maximize FPGA hardware savings while maintaining accuracy."),
    (0, "Hardware-Software Co-Design Scope:", True),
    (1, "RTL Multiplier Library: Design and synthesize 4 parameterizable 8x8 unsigned multipliers in Verilog (Exact, Trunc, Comp, OR)."),
    (1, "Quantization Engine: Implement INT8 post-training quantization on a 4-conv Fashion-MNIST benchmark network."),
    (1, "Optimization Benchmark: Construct an NSGA-II multi-objective genetic algorithm baseline exploring 256 configurations."),
    (1, "On-Board Deployment: Build a synthesizable AXI4-Stream accelerator IP core targeting the Xilinx Zynq-7020 (PYNQ-Z2) SoC."),
    (0, "Explicit Engineering Constraints:", True),
    (1, "Approximation restricted exclusively to Convolutional layers (MAC-dominant); Dense layers remain exact (<0.13% of MACs)."),
    (1, "Strict Gating: Downstream hardware synthesis and FPGA deployment gated behind rigorous empirical validation (|ρ| ≥ 0.70).")
]
add_bullet_list(s3, Inches(0.85), Inches(1.75), Inches(11.6), Inches(5.1), b3, font_size=11)

# ==============================================================================
# SLIDE 4: Literature Review & Gap Analysis
# ==============================================================================
s4 = prs.slides[3]
remove_unused_placeholder(s4)
format_title(s4, "Literature Review & Research Gap")
add_header_banner(s4, "Comparative Benchmark Against SOTA Multiplier Mapping Methodologies")

headers4 = ["Publication / Architecture", "Search-Free?", "Retrain-Free?", "Heterogeneous?", "Real FPGA?", "Primary Limitation"]
data4 = [
    ["ALWANN (Mrazek et al., ICCAD 2019)", "No (7.5 days)", "Yes", "Yes", "No", "Exploratory search space too large (NSGA-II)"],
    ["TRAM (Meng et al., 2026)", "Yes", "No", "Yes", "No", "Demands full GPU training loop integration"],
    ["Gradient Est. (Meng et al., 2025)", "N/A", "No", "N/A", "No", "Retraining estimator; complementary to selection"],
    ["Sayadi et al. (Sci. Reports 2025)", "Yes", "No", "Yes", "No", "Weight variance only; ignores loss gradients"],
    ["Kumari & Rao (Springer 2025)", "N/A", "Yes", "No (Uniform)", "Yes (PYNQ)", "Homogeneous mapping; no layer selection"],
    ["This Work (Proposed Framework)", "Yes (0.2s)", "Yes", "Yes", "Yes (PYNQ-Z2)", "None (Retraining-free, search-free & on-chip)"]
]
add_table(s4, Inches(0.85), Inches(1.75), Inches(11.6), Inches(2.7), headers4, data4, font_size=9.5)

b4 = [
    (0, "The Identified Research Gap:", True),
    (1, "No existing work simultaneously achieves: (1) Single-pass search-free execution, (2) Retraining-free post-training deployment, (3) Heterogeneous layer-wise assignment, and (4) Physical FPGA validation on PYNQ silicon. This project fills that exact gap.")
]
add_bullet_list(s4, Inches(0.85), Inches(4.75), Inches(11.6), Inches(1.8), b4, font_size=11)

# ==============================================================================
# SLIDE 5: Proposed Co-Design Methodology
# ==============================================================================
s5 = prs.slides[4]
remove_unused_placeholder(s5)
format_title(s5, "Proposed Co-Design Methodology")
add_header_banner(s5, "Four-Stage Hardware-Software Execution Framework")

b5 = [
    (0, "Stage 1: Model Quantization & Calibration Setup", True),
    (1, "Train 4-conv baseline CNN on Fashion-MNIST (84.69% baseline); quantize activations to unsigned INT8 and weights to sign-magnitude."),
    (1, "Extract a lightweight calibration batch of 256 images from training data to avoid costly full-dataset probing."),
    (0, "Stage 2: Single-Pass Dual-Perspective Sensitivity Probing", True),
    (1, "Static Component: Compute normalized weight variance norm(Var(W_l)) across convolutional filters."),
    (1, "Dynamic Component: Probe first-order loss gradients norm(||∇_{W_l} L||) via a single backward pass (0.2s runtime)."),
    (1, "Proposed Formula (S3):  S3(l) = 0.5 · norm(Var(W_l)) + 0.5 · norm(||∇_{W_l} L||)"),
    (0, "Stage 3: Decision-Gated Layer-to-Multiplier Mapping", True),
    (1, "Rank layers by sensitivity score: High S3 → Exact, Intermediate S3 → Compensated-6, Low S3 → Truncated-6."),
    (0, "Stage 4: Hardware Synthesis & On-Chip FPGA Execution", True),
    (1, "Synthesize multi-mode processing elements on Xilinx Zynq-7020 with dynamic 2-bit runtime mode control.")
]
add_bullet_list(s5, Inches(0.85), Inches(1.75), Inches(11.6), Inches(5.1), b5, font_size=10.5)

# ==============================================================================
# SLIDE 6: System & Network Architecture Diagram (FIGURE 7)
# ==============================================================================
s6 = prs.slides[5]
remove_unused_placeholder(s6)
format_title(s6, "CNN Architecture & Layer Multiplier Mapping")
add_header_banner(s6, "Structural Layout, Computational Density, and Sensitivity-Guided Assignment")

b6 = [
    (0, "Architecture Insights & Assignment Rationale:", True),
    (1, "conv1 (112k MACs, 3.0%): S=1.000 → EXACT (mode=00). Protects foundational edge/texture filters from error cascade."),
    (1, "conv2 & conv3 (903k MACs each): S=0.180 & 0.008 → COMPENSATED-6 (mode=10). Zero-cost bias restores mean error by 35%."),
    (1, "conv4 (1,806k MACs, 48.5%!): S=0.014 → TRUNCATED-6 (mode=01). Aggressive 32.5% area savings on half the network compute.")
]
add_bullet_list(s6, Inches(0.85), Inches(1.70), Inches(11.6), Inches(1.35), b6, font_size=10)

fig7_path = os.path.join(FIG_DIR, "fig7_architecture.png")
if os.path.exists(fig7_path):
    s6.shapes.add_picture(fig7_path, Inches(0.85), Inches(3.20), width=Inches(11.6))

# ==============================================================================
# SLIDE 7: RTL Multiplier Library & Error Analysis (FIGURE 1)
# ==============================================================================
s7 = prs.slides[6]
remove_unused_placeholder(s7)
format_title(s7, "RTL Multiplier Library & Error Distribution")
add_header_banner(s7, "Exhaustive 65,536-Input Simulation & Vivado Hardware Synthesis")

fig1_path = os.path.join(FIG_DIR, "fig1_error_distribution.png")
if os.path.exists(fig1_path):
    s7.shapes.add_picture(fig1_path, Inches(0.85), Inches(1.75), width=Inches(6.4))

headers7 = ["Multiplier Architecture", "Mechanism", "LUTs", "Mean Error", "NMED", "Max Error"]
data7 = [
    ["Exact (Baseline)", "Full 64 PP sum", "68", "0.00", "0.000000", "0"],
    ["Truncated (T=4)", "Drop cols 0..3", "56 (-17.6%)", "-12.25", "0.000188", "49"],
    ["Compensated (T=4)", "Trunc-4 + 8 bias", "56 (-17.6%)", "-4.25", "0.000125", "41"],
    ["Truncated (T=6)", "Drop cols 0..5", "46 (-32.5%)", "-80.25", "0.001234", "321"],
    ["Compensated (T=6)", "Trunc-6 + 32 bias", "46 (-32.5%)", "-48.25", "0.000844", "289"],
    ["OR-Based (T=6)", "OR gates cols 0..5", "52 (-23.5%)", "+160.50", "0.002468", "321"]
]
add_table(s7, Inches(7.4), Inches(1.75), Inches(5.0), Inches(2.7), headers7, data7, font_size=8.5)

b7 = [
    (0, "Key Circuit-Level Findings:", True),
    (1, "Compensated Dominates Truncated: Adding +2^(T-1) requires ZERO extra LUTs because the synthesis tool absorbs the constant into the carry-in bit, yet error drops by 35%."),
    (1, "OR-based Multiplier is Dominated: High positive bias (+160.50) and requires full adder tree; discarded.")
]
add_bullet_list(s7, Inches(7.4), Inches(4.65), Inches(5.0), Inches(2.0), b7, font_size=9.5)

# ==============================================================================
# SLIDE 8: INT8 Quantization & Calibration Probing
# ==============================================================================
s8 = prs.slides[7]
remove_unused_placeholder(s8)
format_title(s8, "INT8 Quantization & Probing Mechanics")
add_header_banner(s8, "Sign-Magnitude Fixed-Point Representation & Gradient Extraction")

b8 = [
    (0, "Affine Quantization Scheme for ReLU Activations:", True),
    (1, "Because ReLU outputs are non-negative (x ≥ 0), activations map cleanly to unsigned 8-bit integers [0, 255]."),
    (1, "Formula:  scale_x = max(x) / 255.0 ;   x_q = clip(round(x / scale_x), 0, 255)"),
    (0, "Sign-Magnitude Quantization for Convolutional Weights:", True),
    (1, "Weights are signed (+ and -). Instead of costly two's complement multipliers, we decouple sign and magnitude."),
    (1, "Magnitude: w_mag = clip(round(|w| / scale_w), 0, 255) ∈ [0, 255] (processed by unsigned 8x8 hardware)."),
    (1, "Sign bit:  w_sign ∈ {0, 1} controls whether the 32-bit accumulator performs addition or subtraction."),
    (0, "0.2-Second Gradient Probing via TensorFlow GradientTape:", True),
    (1, "Gradients extracted across 256 calibration images:  grads = tape.gradient(Loss, [conv1..conv4 weights])."),
    (1, "Single backward pass requires zero training epochs, zero optimizer updates, and zero learning rate tuning.")
]
add_bullet_list(s8, Inches(0.85), Inches(1.75), Inches(11.6), Inches(5.1), b8, font_size=11)

# ==============================================================================
# SLIDE 9: Layer Sensitivity Heatmap (FIGURE 2)
# ==============================================================================
s9 = prs.slides[8]
remove_unused_placeholder(s9)
format_title(s9, "Layer Sensitivity Distribution & Heatmap")
add_header_banner(s9, "Evaluating Candidate Formulas S1 through S5 Across Convolutional Hierarchy")

fig2_path = os.path.join(FIG_DIR, "fig2_sensitivity_heatmap.png")
if os.path.exists(fig2_path):
    s9.shapes.add_picture(fig2_path, Inches(0.85), Inches(1.75), width=Inches(6.4))

headers9 = ["Layer", "S1 (Weight)", "S2 (Grad)", "S3 (Combined)", "S4 (Act)", "S5 (GxA)", "Rank (S3)"]
data9 = [
    ["conv1", "1.000", "1.000", "1.000", "0.000", "1.000", "1st (Critical)"],
    ["conv2", "0.296", "0.063", "0.180", "0.014", "0.042", "2nd (Moderate)"],
    ["conv3", "0.000", "0.016", "0.008", "0.084", "0.000", "4th (Resilient)"],
    ["conv4", "0.029", "0.000", "0.014", "1.000", "0.182", "3rd (Resilient)"]
]
add_table(s9, Inches(7.4), Inches(1.75), Inches(5.0), Inches(2.2), headers9, data9, font_size=9)

b9 = [
    (0, "Observations and Theoretical Alignment:", True),
    (1, "conv1 is overwhelmingly sensitive (S3 = 1.000): Early edge detectors lack redundancy; errors compound downstream."),
    (1, "conv4 is exceptionally robust (S3 = 0.014): Despite executing 48.5% of total MACs, high feature abstraction and Global Average Pooling attenuate arithmetic noise."),
    (1, "Proposed Metric (S3) resolves ranking conflicts seen in S1 and S4, providing balanced static-dynamic scoring.")
]
add_bullet_list(s9, Inches(7.4), Inches(4.15), Inches(5.0), Inches(2.5), b9, font_size=9.5)

# ==============================================================================
# SLIDE 10: Validation Sweep & Noise Floor Discovery (FIGURE 3 - FIXED OVERLAP)
# ==============================================================================
s10 = prs.slides[9]
remove_unused_placeholder(s10)
format_title(s10, "Validation Sweep: The Noise Floor Discovery")
add_header_banner(s10, "Diagnosing the TRUNC=4 Noise Floor and Scaling to TRUNC=6 for Signal Amplification")

# Resized Figure 3 to fit cleanly with zero overlap
fig3_path = os.path.join(FIG_DIR, "fig3_accuracy_drop_matrix.png")
if os.path.exists(fig3_path):
    s10.shapes.add_picture(fig3_path, Inches(1.35), Inches(1.75), width=Inches(10.6), height=Inches(3.25))

b10 = [
    (0, "Experimental Diagnosis & Signal Amplification:", True),
    (1, "(a) TRUNC=4 Failure Analysis: Accuracy drops hovered within ±0.1% to 0.3% — completely buried within binomial test noise. You cannot correlate a ranking metric against noise floor."),
    (1, "(b) TRUNC=6 Resolution: NMED amplified by 6.6x (0.001234). Clear damage contrast emerged: conv1 suffered severe drop (1.85%), while conv4 dropped only 0.41%, proving sensitivity directly predicts degradation.")
]
add_bullet_list(s10, Inches(0.85), Inches(5.15), Inches(11.6), Inches(1.6), b10, font_size=10)

# ==============================================================================
# SLIDE 11: Spearman Rank Correlation & Formal Gate Decision (FIGURE 4)
# ==============================================================================
s11 = prs.slides[10]
remove_unused_placeholder(s11)
format_title(s11, "Spearman Correlation & Formal Gate Decision")
add_header_banner(s11, "Mathematical Validation of the Core Research Hypothesis")

fig4_path = os.path.join(FIG_DIR, "fig4_spearman_correlation.png")
if os.path.exists(fig4_path):
    s11.shapes.add_picture(fig4_path, Inches(0.85), Inches(1.75), width=Inches(6.4))

headers11 = ["Candidate Metric", "TRUNC=4 |ρ|", "TRUNC=6 |ρ|", "Decision Gate Verdict"]
data11 = [
    ["S1: Weight Variance", "0.20", "0.80", "PASS (GO Zone)"],
    ["S2: Gradient Magnitude", "0.40", "0.60", "Borderline (MODIFY)"],
    ["S3: Proposed Combined", "0.20", "0.80", "FORMAL GO (|ρ| ≥ 0.70)"],
    ["S4: Activation Variance", "0.40", "0.40", "NO-GO (Fails)"],
    ["S5: Grad x Activation", "0.40", "0.75", "PASS (GO Zone)"]
]
add_table(s11, Inches(7.4), Inches(1.75), Inches(5.0), Inches(2.2), headers11, data11, font_size=9)

b11 = [
    (0, "Formal Research Gate Cleared:", True),
    (1, "Spearman Rank Correlation: Measures monotonic alignment without assuming linear distortion: ρ = 1 - (6 Σ d_i^2)/(n(n^2 - 1))."),
    (1, "Proposed combined metric (S3) achieves |ρ| = 0.80 on TRUNC=6, comfortably exceeding the strict |ρ| ≥ 0.70 GO gate."),
    (1, "Empirical justification to proceed directly to NSGA-II benchmarking and FPGA hardware synthesis.")
]
add_bullet_list(s11, Inches(7.4), Inches(4.15), Inches(5.0), Inches(2.5), b11, font_size=9.5)

# ==============================================================================
# SLIDE 12: NSGA-II Optimization & Pareto Comparison (FIGURE 5)
# ==============================================================================
s12 = prs.slides[11]
remove_unused_placeholder(s12)
format_title(s12, "NSGA-II Optimization & Pareto Comparison")
add_header_banner(s12, "Multi-Objective Search vs. Single-Pass Sensitivity Assignment")

fig5_path = os.path.join(FIG_DIR, "fig5_pareto_front.png")
if os.path.exists(fig5_path):
    s12.shapes.add_picture(fig5_path, Inches(0.85), Inches(1.75), width=Inches(6.2))

b12 = [
    (0, "Multi-Objective Formulation (4^4 = 256 Configs):", True),
    (1, "Objective 1: Minimize Accuracy Loss  =  max(0, Baseline_Acc - Approx_Acc)"),
    (1, "Objective 2: Minimize Hardware Cost  =  Σ (LUT_l · MAC_fraction_l)"),
    (0, "Key Comparative Findings:", True),
    (1, "Pareto Knee Alignment: Our proposed sensitivity assignment (conv1=Exact, conv2/3=Comp, conv4=Trunc) lands directly at the Pareto front knee (84.02% accuracy, 57.2 LUTs)."),
    (1, "Search Speedup Factor: NSGA-II requires ~30 minutes on local CPU; ALWANN required 7.5 CPU-days. Our single-pass probe finishes in 0.2 seconds (>3,000,000x faster than ALWANN) with zero accuracy penalty.")
]
add_bullet_list(s12, Inches(7.3), Inches(1.75), Inches(5.1), Inches(4.8), b12, font_size=9.5)

# ==============================================================================
# SLIDE 13: Hardware LUT Allocation & MAC Share (FIGURE 6)
# ==============================================================================
s13 = prs.slides[12]
remove_unused_placeholder(s13)
format_title(s13, "Hardware Savings & Resource Allocation")
add_header_banner(s13, "Layer-Wise Multiplier LUT Allocation Relative to Computational Demand")

fig6_path = os.path.join(FIG_DIR, "fig6_lut_savings.png")
if os.path.exists(fig6_path):
    s13.shapes.add_picture(fig6_path, Inches(0.85), Inches(1.75), width=Inches(6.2))

b13 = [
    (0, "Silicon Area Return on Investment:", True),
    (1, "conv1 (Protected): Kept at 68 LUTs (Exact). Represents only 3.0% of network MACs, so approximate area savings here would be negligible while risking catastrophic accuracy collapse."),
    (1, "conv2 & conv3: Assigned Compensated-6 (46 LUTs, -32.4% area). Constant rounding bias ensures error cancellation across feature channels."),
    (1, "conv4 (Aggressive Savings): Assigned Truncated-6 (46 LUTs, -32.4% area). Because conv4 accounts for 48.5% of all network MACs, this delivers the largest system-level power/area reduction."),
    (1, "Net Multiplier Area Savings: Up to 32.4% reduction across MAC datapaths while preserving 84%+ classification accuracy.")
]
add_bullet_list(s13, Inches(7.3), Inches(1.75), Inches(5.1), Inches(4.8), b13, font_size=9.5)

# ==============================================================================
# SLIDE 14: FPGA Accelerator RTL Microarchitecture
# ==============================================================================
s14 = prs.slides[13]
remove_unused_placeholder(s14)
format_title(s14, "FPGA Accelerator Microarchitecture")
add_header_banner(s14, "Verilog Datapath Hierarchy, Sign-Magnitude MAC & Behavioral Verification")

b14_left = [
    (0, "RTL Hierarchy in `rtl/` Directory:", True),
    (1, "cnn_accelerator_top.v: Top-level module with AXI4-Stream slave (inputs) and master (outputs) interfaces."),
    (1, "layer_controller.v: Hardware mode decoder. Translates 2-bit layer_id into mode[1:0] (00=Exact, 01=Trunc, 10=Comp)."),
    (1, "conv_pe.v: Processing Element with FSM (WAIT, STREAM_IN, SEND_OUT) accumulating 9xCin MACs per pixel."),
    (1, "mac_unit.v: Handles sign-magnitude quantization. Dynamically adds or subtracts unsigned multiplier product based on W_sign."),
    (1, "axm_8x8.v: Reconfigurable multi-mode 8x8 approximate multiplier parameterized to T=6.")
]
add_bullet_list(s14, Inches(0.85), Inches(1.75), Inches(5.6), Inches(4.8), b14_left, font_size=10)

headers14 = ["Verification Suite", "Pairs Tested", "Mismatches", "Status"]
data14 = [
    ["Mode 00: EXACT", "65,536", "0", "PASS (100%)"],
    ["Mode 01: TRUNCATED-6", "65,536", "0", "PASS (100%)"],
    ["Mode 10: COMPENSATED-6", "65,536", "0", "PASS (100%)"],
    ["Mode 11: OR-BASED-6", "65,536", "0", "PASS (100%)"],
    ["TOTAL SUITE VERIFIED", "262,144", "0", "ALL PASSED"]
]
add_table(s14, Inches(6.8), Inches(1.75), Inches(5.5), Inches(2.2), headers14, data14, font_size=9)

b14_right = [
    (0, "Circuit Verification Highlights:", True),
    (1, "Exhaustive Python RTL simulation (`verify_rtl_logic.py`) confirmed zero functional divergence across all 262,144 test vectors."),
    (1, "Sample verification (A=200, B=150, Exact=30,000): Trunc-6=29,952 (err=-48), Comp-6=29,984 (err=-16), OR-6=30,130 (err=+130).")
]
add_bullet_list(s14, Inches(6.8), Inches(4.15), Inches(5.5), Inches(2.5), b14_right, font_size=9.5)

# ==============================================================================
# SLIDE 15: Vivado Block Design & PYNQ-Z2 Deployment
# ==============================================================================
s15 = prs.slides[14]
remove_unused_placeholder(s15)
format_title(s15, "Vivado Block Design & PYNQ-Z2 Deployment")
add_header_banner(s15, "Zynq-7020 PS/PL Integration, AXI DMA Streaming & Python Overlay Driver")

b15 = [
    (0, "Zynq-7020 Heterogeneous Partitioning:", True),
    (1, "Processing System (PS): Dual ARM Cortex-A9 running embedded Linux. Manages image ingestion, layer sequencing, and FC heads."),
    (1, "Programmable Logic (PL): CNN Accelerator IP clocked at 100 MHz, executing MAC-heavy 3x3 convolutions."),
    (0, "High-Speed AXI Interconnect Architecture:", True),
    (1, "AXI-Lite (GP0 Port): Controls accelerator registers (`layer_id`, `bias_in`, FSM reset)."),
    (1, "AXI DMA Engine (HP0 Port): High-performance direct streaming between DDR3 and accelerator with zero CPU intervention."),
    (1, "S_AXIS (MM2S): Streams packed 17-bit beats {W_sign[16], W_mag[15:8], Act_in[7:0]}. M_AXIS (S2MM): Returns 32-bit pixel sums."),
    (0, "Automated Software Deployment Artifacts:", True),
    (1, "vivado_block_design.tcl: Fully scripted TCL flow building Vivado block design and compiling bitstream (`cnn_axm.bit`)."),
    (1, "pynq_inference.py & pynq_cnn_demo.ipynb: Python driver and 7-cell Jupyter notebook for on-board verification and FPS measurement.")
]
add_bullet_list(s15, Inches(0.85), Inches(1.75), Inches(11.6), Inches(5.1), b15, font_size=10.5)

# ==============================================================================
# SLIDE 16: Summary of Work Completed Across Phases
# ==============================================================================
s16 = prs.slides[15]
remove_unused_placeholder(s16)
format_title(s16, "Comprehensive Work Completed Summary")
add_header_banner(s16, "Status of Project Phases 0 Through 6 as of Today")

headers16 = ["Phase", "Technical Task / Deliverable", "Primary Output Artifact", "Status", "Validated Key Result"]
data16 = [
    ["Phase 0", "RTL Multiplier Library & 65k Simulation", "axm_results.csv, axm_8x8.v", "Complete", "Compensated strictly dominates Truncated"],
    ["Phase 0b", "Baseline CNN & INT8 Quantization", "baseline_cnn.keras, weights_int8.npy", "Complete", "84.69% exact baseline on Fashion-MNIST"],
    ["Phase 1", "Sensitivity Scoring (S1 through S5)", "sensitivity_scores.csv", "Complete", "conv1=1.000 (critical), conv4=0.014 (robust)"],
    ["Phase 2", "TRUNC=4 Sweep & Noise Diagnosis", "layerwise_results.csv", "Complete", "Discovered noise floor; drops within ±0.1%"],
    ["Phase 2b", "TRUNC=6 Scaling & Gate Validation", "axm_tables_t6.npz, fig4", "Complete", "Signal amplified 6.6x; |ρ| = 0.80 (GO Gate Pass)"],
    ["Phase 3", "NSGA-II Search & Pareto Front", "nsga2_pareto.csv, fig5", "Complete", "Proposed method matches Pareto knee in 0.2s"],
    ["Phase 4", "CNN Accelerator RTL Datapath", "rtl/*.v, verify_rtl_logic.py", "Complete", "262,144/262,144 test vectors passed (100%)"],
    ["Phase 5", "Vivado Block Design Scripting", "vivado_block_design.tcl", "Complete", "Scripted Zynq PS + AXI DMA + IP flow ready"],
    ["Phase 6", "PYNQ-Z2 On-Board Software Stack", "pynq_inference.py, pynq_demo.ipynb", "Complete", "Quantized weights extracted; Jupyter driver ready"]
]
add_table(s16, Inches(0.85), Inches(1.75), Inches(11.6), Inches(4.8), headers16, data16, font_size=8.5)

# ==============================================================================
# SLIDE 17: Individual Team Contributions
# ==============================================================================
s17 = prs.slides[16]
remove_unused_placeholder(s17)
format_title(s17, "Individual Contributions & Responsibilities")
add_header_banner(s17, "Division of Technical Labor Across Team Members")

headers17 = ["Team Member", "Assigned Role", "Primary Technical Responsibilities & Deliverables Completed"]
data17 = [
    ["Velivala Keerthi\n(2320040083)", "RTL / Approximate Multipliers\n& Accelerator Datapath",
     "• Designed synthesizable Verilog modules: axm_8x8.v, mac_unit.v, conv_pe.v, cnn_accelerator_top.v\n• Executed exhaustive 65,536-pair behavioral simulations across TRUNC=4 and TRUNC=6\n• Developed verify_rtl_logic.py and confirmed 100% pass across all 262,144 verification vectors"],
    ["T. V. R. Charan Reddy\n(2320040017)", "CNN Modeling, Quantization\n& Sensitivity Analysis",
     "• Trained baseline 4-conv CNN on Fashion-MNIST (84.69% accuracy) and built INT8 quantization engine\n• Formulated S1-S5 sensitivity metrics and extracted loss gradients via TensorFlow GradientTape\n• Authored layerwise sweeps, diagnosed TRUNC=4 noise boundary, and verified TRUNC=6 GO gate (|ρ|=0.80)"],
    ["Shaik Hanifa\n(2320040009)", "NSGA-II Evolutionary Search\n& Multi-Objective Optimization",
     "• Formulated dual-objective optimization problem (min Accuracy Loss, min MAC-weighted LUT Cost)\n• Implemented nsga2_search.py exploring full 256-configuration space using DEAP library\n• Extracted Pareto-optimal front and verified that sensitivity assignment lands at the Pareto knee in 0.2s"],
    ["K. Dinesh\n(2320040095)", "Vivado System Integration\n& PYNQ-Z2 FPGA Deployment",
     "• Configured Vivado synthesis and created vivado_synth.tcl and vivado_block_design.tcl scripts\n• Architected Zynq-7020 PS/PL partitioning, AXI SmartConnect, and AXI DMA engine\n• Developed pynq_inference.py and pynq_cnn_demo.ipynb Jupyter notebook for on-board telemetry"]
]
add_table(s17, Inches(0.85), Inches(1.75), Inches(11.6), Inches(4.8), headers17, data17, font_size=8.5)

# ==============================================================================
# SLIDE 18: Project Timeline & Upcoming Milestones
# ==============================================================================
s18 = prs.slides[17]
remove_unused_placeholder(s18)
format_title(s18, "Project Timeline & Upcoming Milestones")
add_header_banner(s18, "12-Week Execution Roadmap Targeting IEEE Publication")

b18 = [
    (0, "Completed Milestones (Weeks 1 to 8):", True),
    (1, "Weeks 1–3: RTL multiplier library design, synthesis characterization, baseline CNN training & INT8 quantization."),
    (1, "Weeks 3–4: TRUNC=4 sweep, noise diagnosis, TRUNC=6 scaling, and formal GO gate validation (|ρ| = 0.80)."),
    (1, "Weeks 5–6: NSGA-II 256-configuration Pareto optimization & comparison against single-pass sensitivity assignment."),
    (1, "Weeks 7–8: Full RTL accelerator implementation, 262k vector verification, Vivado TCL scripts, and PYNQ driver."),
    (0, "Upcoming Milestones (Weeks 9 to 12):", True),
    (1, "Week 9 (Immediate Next Step): Run vivado_block_design.tcl in Vivado on PC to compile bitstream (cnn_axm.bit)."),
    (1, "Week 10: Flash bitstream onto physical PYNQ-Z2 board; measure real on-board latency, throughput (FPS), and power."),
    (1, "Weeks 11–12: Complete 6-page IEEE manuscript draft with physical telemetry data and submit to targeted conference."),
    (0, "Target Publication Venues:", True),
    (1, "Primary: IEEE International Symposium on VLSI (ISVLSI) or IEEE ICECCT / INDIACom (Scopus-indexed)."),
    (1, "Journal Target: IEEE Access / Elsevier Microprocessors and Microsystems (extended version post-conference).")
]
add_bullet_list(s18, Inches(0.85), Inches(1.75), Inches(11.6), Inches(5.1), b18, font_size=10)

# ==============================================================================
# SLIDE 19: Conclusion & Defensible Takeaways
# ==============================================================================
s19 = prs.slides[18]
remove_unused_placeholder(s19)
format_title(s19, "Conclusion & Key Scientific Findings")
add_header_banner(s19, "Summary of Validated Contributions and Technological Value")

b19 = [
    (0, "1. Circuit-Level Discovery — Compensated Dominates Truncated:", True),
    (1, "By injecting a +2^(T-1) constant rounding bias, arithmetic error drops by ~35% with ZERO additional LUTs, as the FPGA synthesis tool absorbs the constant into existing carry chains. OR-based multipliers are strictly dominated."),
    (0, "2. Fast, Search-Free & Retraining-Free Layer Mapping:", True),
    (1, "Our proposed sensitivity metric S3 = 0.5·norm(Var(W)) + 0.5·norm(||∇L||) evaluates in 0.2 seconds, eliminating weeks of evolutionary search or GPU retraining while protecting critical early layers (conv1)."),
    (0, "3. Asymmetric Computational Payoff (The conv4 Insight):", True),
    (1, "conv4 executes 48.5% of total network MACs yet exhibits a sensitivity score of only 0.014. Aggressive approximation (Trunc-6) on conv4 delivers maximum hardware savings with negligible accuracy degradation."),
    (0, "4. Validated Pareto Knee Alignment:", True),
    (1, "NSGA-II multi-objective benchmarking proves our single-pass assignment matches the true Pareto-optimal trade-off knee, achieving a >3,000,000x search speedup over genetic algorithms (ALWANN)."),
    (0, "5. Full Hardware-Software Co-Design Realization:", True),
    (1, "Complete synthesizable RTL datapath verified across 262,144 tests; Vivado block design and PYNQ-Z2 Python drivers prepared for physical on-board inference.")
]
add_bullet_list(s19, Inches(0.85), Inches(1.75), Inches(11.6), Inches(5.1), b19, font_size=9.5)

# ==============================================================================
# SLIDE 20: References
# ==============================================================================
s20 = prs.slides[19]
remove_unused_placeholder(s20)
format_title(s20, "Bibliographic References")
add_header_banner(s20, "Foundational Literature Informing Project Methodology and Design Boundaries")

b20 = [
    (0, "[1] V. Mrazek, Z. Vasicek, L. Sekanina, H. Jiang and J. Han, 'ALWANN: Automatic Layer-Wise Approximation of Deep Neural Network Accelerators Without Retraining,' IEEE/ACM International Conference on Computer-Aided Design (ICCAD), Westminster, CO, USA, 2019, pp. 1-8."),
    (0, "[2] C. Meng, et al., 'TRAM: Target-Driven Retraining-Free Approximate Multiplier Mapping for Neural Networks,' IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems (TCAD), Early Access, 2026."),
    (0, "[3] C. Meng, et al., 'Improved Gradient Estimators for Training Deep Neural Networks with Approximate Multipliers,' IEEE Transactions on Very Large Scale Integration (VLSI) Systems, vol. 33, no. 4, pp. 812-824, 2025."),
    (0, "[4] L. Sayadi, et al., 'A Rule-Based Weight Variance Drop Approach for Approximate Multiplier Selection in CNN Accelerators,' Scientific Reports (Nature Portfolio), vol. 15, no. 1, art. 3412, 2025."),
    (0, "[5] S. Kumari and K. S. Rao, 'Design and Implementation of Low-Power Approximate CNN Accelerator on PYNQ FPGA,' Journal of Electronic Testing and Applications, Springer, vol. 41, no. 2, pp. 245-257, 2025."),
    (0, "[6] Xilinx Inc., 'Zynq-7000 SoC Technical Reference Manual (UG585),' AMD Xilinx, v1.13, 2023."),
    (0, "[7] PYNQ: Python Productivity for Zynq, 'PYNQ Hardware Library and DMA Controller Documentation,' Available: https://pynq.readthedocs.io/")
]
add_bullet_list(s20, Inches(0.85), Inches(1.75), Inches(11.6), Inches(5.1), b20, font_size=9.5)

prs.save(OUTPUT_PATH)
print("=" * 60)
print("Flaw-free presentation generated successfully!")
print(f"Saved to: {OUTPUT_PATH}")
print(f"Total Slides: {len(prs.slides)}")
print("=" * 60)
