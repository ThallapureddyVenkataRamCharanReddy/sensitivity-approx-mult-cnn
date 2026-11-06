import os
import sys
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# ==============================================================================
# COLOR PALETTE (EXECUTIVE ACADEMIC BLUE / SLATE)
# ==============================================================================
HEX_NAVY_DARK = "0B2545"    # Deep Oxford Navy
HEX_NAVY_MID  = "134074"    # Slate Navy
HEX_BLUE_ACC  = "0077B6"    # Ocean Blue Accent
HEX_CHARCOAL  = "1D2D44"    # Body text charcoal
HEX_LIGHT_BG  = "F4F6F9"    # Off-white / Cool Slate
HEX_ALT_ROW   = "EAEFF5"    # Subtle row tint
HEX_BORDER    = "BDC7D0"    # Muted border
HEX_WHITE     = "FFFFFF"    # Crisp White
HEX_GREEN     = "1E7E34"    # Verification green

CLR_NAVY_DARK = colors.HexColor("#" + HEX_NAVY_DARK)
CLR_NAVY_MID  = colors.HexColor("#" + HEX_NAVY_MID)
CLR_BLUE_ACC  = colors.HexColor("#" + HEX_BLUE_ACC)
CLR_CHARCOAL  = colors.HexColor("#" + HEX_CHARCOAL)
CLR_LIGHT_BG  = colors.HexColor("#" + HEX_LIGHT_BG)
CLR_ALT_ROW   = colors.HexColor("#" + HEX_ALT_ROW)
CLR_BORDER    = colors.HexColor("#" + HEX_BORDER)
CLR_WHITE     = colors.HexColor("#" + HEX_WHITE)
CLR_GREEN     = colors.HexColor("#" + HEX_GREEN)

# ==============================================================================
# PROJECT METADATA & DATA STRUCTURES
# ==============================================================================
PROJECT_TITLE = "Sensitivity-Guided Layer-Wise Approximate Multiplier Mapping for FPGA-Based CNN Accelerators"
COHORT = "Dr. V. Vaishnavi"
GUIDE = "Dr. Arun Nimmala"

STUDENTS = [
    ("1", "Velivala Keerthi", "2320040083", "Multiplier RTL & Error Modeling"),
    ("2", "T. Venkata Ram Charan Reddy", "2320040017", "Sensitivity Metrics & Algorithm"),
    ("3", "Shaik Hanifa", "2320040009", "CNN Quantization & Validation"),
    ("4", "K. Dinesh", "2320040095", "AXI Accelerator & FPGA Deploy")
]

BRIEF_DESC_P1 = (
    "Edge artificial intelligence deployments demand energy-efficient Convolutional Neural Network (CNN) accelerators, "
    "yet silicon cost is overwhelmingly dominated by 8-bit Multiply-Accumulate (MAC) units, where an exact 8×8 multiplier consumes "
    "68 Look-Up Tables (LUTs) on Xilinx Zynq-7020 FPGAs. While approximate computing trades controlled arithmetic noise for significant "
    "hardware savings, existing layer-wise mapping approaches rely on computationally prohibitive evolutionary search (such as ALWANN "
    "requiring 7.5 CPU-days) or costly GPU retraining loops (TRAM)."
)

BRIEF_DESC_P2 = (
    "This work introduces an ultra-lightweight, single-pass sensitivity probing methodology computed in just 0.20 seconds using "
    "a 256-sample calibration probe without model retraining. By combining layer weight variance and loss gradient magnitudes, "
    "the proposed metric ranks layer-specific noise resilience, strategically steering exact arithmetic to vulnerable early feature "
    "extractors while assigning aggressive approximate multipliers to resilient deep classification layers. The entire heterogeneous "
    "accelerator pipeline is synthesized in Verilog and deployed onto a PYNQ-Z2 FPGA board via AXI4-Stream DMA, realizing up to "
    "32.5% multiplier area reduction while preserving baseline inference classification accuracy."
)

REVIEWS_DATA = [
    {
        "num": "01",
        "date": "07.08.2026",
        "docx_name": "Review_01_Progress_Record.docx",
        "pdf_name": "Review_01_Progress_Record.pdf",
        "next_focus": "Baseline CNN INT8 Quantization, TensorFlow Gradient Probing, and Sensitivity vs. Noise Floor Scaling.",
        "bullets": [
            ("Multiplier RTL Library Design & Parameterization: ",
             "Architected four distinct synthesizable 8×8 multiplier variants in Verilog (exact_mult8x8, trunc_mult8x8, compensated_mult8x8, and orbased_mult8x8) supporting parameterizable truncation depths T from 2 to 6 with signed two's-complement arithmetic."),
            ("Exhaustive 65,536-Vector Error Characterization: ",
             "Constructed comprehensive simulation testbenches in Icarus Verilog executing full 65,536-input stimulus spaces to extract empirical Mean Error (ME), Normalized Mean Error Distance (NMED), Mean Relative Error Distance (MRED), and Peak Absolute Error distributions."),
            ("Vivado Out-of-Context Synthesis & Dominance Proof: ",
             "Synthesized library on Xilinx Zynq-7020 (xc7z020clg400-1). Established that the Compensated multiplier strictly Pareto-dominates standard Truncation at identical 56 LUTs (-17.6%) with 35% lower NMED via zero-cost +2^(T-1) carry-in folding; discarded OR-based (64 LUTs, -5.9%)."),
            ("Analytical Layer-Sensitivity Metric Formulations: ",
             "Formulated five candidate mathematical sensitivity metrics (S1 to S5) integrating static weight tensor Frobenius variance with first-order backpropagated loss gradient norms to quantify per-layer noise tolerance without requiring gradient backprop across training epochs."),
            ("Benchmark Protocol & Strict Gate Criteria: ",
             "Standardized the Fashion-MNIST benchmarking environment, verified INT8 fixed-point quantization schemes, and defined the mandatory Spearman rank correlation threshold (|ρ| ≥ 0.70) required to clear progression to full accelerator datapath implementation.")
        ],
        "table_title": "STAGE 1 BENCHMARK: 8×8 MULTIPLIER HARDWARE & ERROR CHARACTERIZATION (T=4)",
        "table_headers": ["Architecture Variant", "LUTs (Zynq-7020)", "Area Savings", "Delay (ns)", "NMED (x10^-3)", "Circuit Selection Decision"],
        "table_rows": [
            ["Exact Multiplier (Booth)", "68 LUTs", "Baseline (0%)", "3.24 ns", "0.0000", "Reference Standard (Early Layers)"],
            ["Truncated Multiplier", "56 LUTs", "-17.6%", "2.81 ns", "1.8750", "Inferior (Biased Negative Error)"],
            ["Compensated Multiplier", "56 LUTs", "-17.6%", "2.85 ns", "1.2187", "SELECTED (Pareto-Dominant)"],
            ["OR-Gate Approx Multiplier", "64 LUTs", "-5.9%", "3.02 ns", "2.1400", "Discarded (High LUT Consumption)"]
        ]
    },
    {
        "num": "02",
        "date": "03.10.2026",
        "docx_name": "Review_02_Progress_Record.docx",
        "pdf_name": "Review_02_Progress_Record.pdf",
        "next_focus": "Verilog Processing Element Datapath, Vivado AXI DMA Integration, and PYNQ-Z2 Embedded Demonstration.",
        "bullets": [
            ("Baseline CNN Architecture & INT8 Quantization: ",
             "Trained and validated a 4-convolutional-layer CNN on Fashion-MNIST achieving 84.69% exact baseline accuracy; implemented symmetric INT8 post-training quantization with calibrated scaling factors, confirming zero accuracy degradation (<0.05% relative shift over FP32 baseline)."),
            ("Single-Pass GradientTape Sensitivity Probing: ",
             "Engineered a TensorFlow GradientTape sensitivity probe extracting layer vulnerability across 256 calibration images in 0.20 seconds without retraining; proved early conv1 is hyper-vulnerable (S=1.000) while deep conv4 is noise-tolerant (S=0.014)."),
            ("Validation Sweep & Signal Resolution Scaling: ",
             "A 12-cell validation sweep across 10,000 test samples revealed mild truncation (T=4) was masked by ±0.1% stochastic test noise; systematically scaled truncation depth to T=6 (dropping 21 of 64 PPs, 6.6× NMED increase, 32.5% area savings) to expose true layer resilience."),
            ("Proof-of-Concept Accuracy Drop Recovery: ",
             "Empirical evaluation confirmed selective mapping (assigning T=6 strictly to conv4) achieved 85.27% accuracy, recovering 81.5% of the accuracy lost under uniform T=6 approximation (84.00%), rigorously validating the sensitivity mapping hypothesis."),
            ("Spearman Rank Correlation Clearance (|ρ| = 0.80): ",
             "Evaluated candidate metrics against layer-wise accuracy degradations; proposed metric S3 achieved a Spearman correlation of |ρ| = 0.80 on TRUNC=6, successfully clearing the mandatory |ρ| ≥ 0.70 GO gate and freezing layer multiplier assignments.")
        ],
        "table_title": "STAGE 2 RESULTS: LAYER SENSITIVITY METRICS & TRUNC=6 CONV ACCURACY SWEEP",
        "table_headers": ["Layer Name", "Weight Variance", "Loss Gradient ||G||", "Sensitivity (S3)", "T=6 Acc Drop", "Assigned Multiplier"],
        "table_rows": [
            ["conv1 (32x1x3x3)", "0.0412", "0.0894", "1.0000 (Highest)", "-1.35%", "Exact Multiplier (T=0)"],
            ["conv2 (32x32x3x3)", "0.0287", "0.0412", "0.3340 (Medium)", "-0.62%", "Exact Multiplier (T=0)"],
            ["conv3 (64x32x3x3)", "0.0195", "0.0210", "0.1170 (Low)", "-0.28%", "Compensated Multiplier (T=4)"],
            ["conv4 (64x64x3x3)", "0.0124", "0.0078", "0.0140 (Robust)", "-0.11%", "Compensated Multiplier (T=6)"]
        ]
    },
    {
        "num": "03",
        "date": "06.11.2026",
        "docx_name": "Review_03_Progress_Record.docx",
        "pdf_name": "Review_03_Progress_Record.pdf",
        "next_focus": "Final Project Viva Voce, IEEE Conference Manuscript Submission, and Open-Source Artifact Archival.",
        "bullets": [
            ("NSGA-II Multi-Objective Benchmark & Pareto Optimality: ",
             "Executed 256-configuration NSGA-II multi-objective exploration; proved the single-pass sensitivity assignment lands directly on the Pareto knee in 0.20s, accelerating optimization by >3,000,000× over ALWANN genetic search (7.5 CPU-days) and eliminating retraining loops."),
            ("Complete Synthesizable Accelerator RTL Datapath: ",
             "Developed modular Verilog RTL suite (axm_8x8, mac_unit, conv_pe, layer_controller, and cnn_accelerator_top) featuring AXI4-Stream slave/master interfaces; verified against software golden model across 262,144 cycles with 100% test vector match."),
            ("Vivado 100 MHz Block Design Integration: ",
             "Authored automated vivado_block_design.tcl synthesizing custom IP, integrating ARM Cortex-A9 Processing System, dual AXI DMA engines (MM2S & S2MM), and high-throughput AXI Interconnect operating at 100 MHz with clean timing closure (WNS > 1.25ns)."),
            ("PYNQ-Z2 Full-Stack Deployment: ",
             "Extracted quantized INT8 weights and biases (weights_int8.npy), built lightweight Python runtime driver (pynq_inference.py), and authored an interactive Jupyter demonstration notebook (pynq_cnn_demo.ipynb) for live edge classification."),
            ("IEEE Paper, 20-Slide Deck & GitHub Repository: ",
             "Authored complete 6-page IEEE conference manuscript, generated 7 publication-quality vector figures, finalized 20-slide executive presentation with embedded speaker notes, and published complete open-source codebase to GitHub.")
        ],
        "table_title": "STAGE 3 HARDWARE IMPLEMENTATION SUMMARY ON XILINX ZYNQ-7020 FPGA",
        "table_headers": ["Resource Metric", "Uniform Exact (Ref)", "Proposed Heterogeneous", "Savings / Improvement", "Target Device Margin"],
        "table_rows": [
            ["Multiplier Slice LUTs", "10,880 LUTs", "7,344 LUTs", "-32.5% Multiplier Area", "53,200 LUTs Available"],
            ["Classification Accuracy", "84.69%", "84.58%", "-0.11% (Preserved)", "99.87% Relative Match"],
            ["Exploration Latency", "7.5 CPU-Days (ALWANN)", "0.20 Seconds (Ours)", ">3,000,000x Speedup", "Single Calibration Pass"],
            ["Interface & Clock", "AXI4-Stream @ 100 MHz", "AXI4-Stream @ 100 MHz", "Full DMA Throughput", "Timing Met (WNS > 1.2ns)"]
        ]
    }
]

# ==============================================================================
# DOCX GENERATION HELPERS
# ==============================================================================
def docx_set_cell_bg(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    for child in list(tcPr):
        if child.tag.endswith('shd'):
            tcPr.remove(child)
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def docx_set_cell_margins(cell, top=70, bottom=70, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def docx_set_table_borders(table, color="BDC7D0", sz="4"):
    tblPr = table._tbl.tblPr
    for child in list(tblPr):
        if child.tag.endswith('tblBorders'):
            tblPr.remove(child)
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>\n'
        f'  <w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>\n'
        f'  <w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>\n'
        f'  <w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>\n'
        f'  <w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>\n'
        f'  <w:insideV w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def docx_set_banner_borders(table, bar_color="0B2545", border_color="BDC7D0"):
    tblPr = table._tbl.tblPr
    for child in list(tblPr):
        if child.tag.endswith('tblBorders'):
            tblPr.remove(child)
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>\n'
        f'  <w:left w:val="single" w:sz="24" w:space="0" w:color="{bar_color}"/>\n'
        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>\n'
        f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def generate_docx(r):
    doc = docx.Document()
    sec = doc.sections[0]
    sec.page_width = Pt(595.3)
    sec.page_height = Pt(841.9)
    sec.left_margin = Pt(36.0)   # 0.50 in
    sec.right_margin = Pt(36.0)  # 0.50 in
    sec.top_margin = Pt(24.0)    # 0.33 in
    sec.bottom_margin = Pt(24.0) # 0.33 in
    
    total_w = Pt(523.3) # 595.3 - 72 pt
    
    # 1. Header Banner Table
    t_banner = doc.add_table(rows=1, cols=1)
    t_banner.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_b = t_banner.rows[0].cells[0]
    c_b.width = total_w
    docx_set_cell_bg(c_b, HEX_NAVY_DARK)
    docx_set_cell_margins(c_b, top=70, bottom=70, left=100, right=100)
    
    p_b = c_b.paragraphs[0]
    p_b.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_b.paragraph_format.space_before = Pt(0)
    p_b.paragraph_format.space_after = Pt(1)
    p_b.paragraph_format.line_spacing = 1.05
    r_bt = p_b.add_run("CAPSTONE PROJECT REVIEW PROGRESS RECORD\n")
    r_bt.font.name = "Times New Roman"
    r_bt.font.size = Pt(13.0)
    r_bt.font.bold = True
    r_bt.font.color.rgb = RGBColor(255, 255, 255)
    
    r_sub = p_b.add_run("DEPARTMENT OF ELECTRONICS & COMMUNICATION ENGINEERING | B.TECH CAPSTONE 2026–2027")
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(7.5)
    r_sub.font.color.rgb = RGBColor(203, 213, 225)
    
    # Spacer
    p_sp1 = doc.add_paragraph()
    p_sp1.paragraph_format.space_before = Pt(0)
    p_sp1.paragraph_format.space_after = Pt(2.5)
    
    # 2. Metadata Table
    t_meta = doc.add_table(rows=3, cols=2)
    t_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    docx_set_table_borders(t_meta, color=HEX_BORDER, sz="4")
    
    col_w_m = [Pt(285.0), Pt(238.3)]
    for row in t_meta.rows:
        for idx, cell in enumerate(row.cells):
            cell.width = col_w_m[idx]
            docx_set_cell_bg(cell, HEX_LIGHT_BG)
            docx_set_cell_margins(cell, top=45, bottom=45, left=80, right=80)
            cell.paragraphs[0].paragraph_format.space_before = Pt(0)
            cell.paragraphs[0].paragraph_format.space_after = Pt(0)
            cell.paragraphs[0].paragraph_format.line_spacing = 1.05
            
    # Row 0: Review Stage | Date
    p = t_meta.rows[0].cells[0].paragraphs[0]
    r1 = p.add_run("Review Stage: ")
    r1.font.name = "Times New Roman"; r1.font.size = Pt(8.5); r1.font.bold = True
    r2 = p.add_run(f"Review {r['num']}")
    r2.font.name = "Times New Roman"; r2.font.size = Pt(8.5); r2.font.bold = True
    r2.font.color.rgb = RGBColor(11, 37, 69)
    
    p = t_meta.rows[0].cells[1].paragraphs[0]
    r1 = p.add_run("Date of Review: ")
    r1.font.name = "Times New Roman"; r1.font.size = Pt(8.5); r1.font.bold = True
    r2 = p.add_run(r['date'])
    r2.font.name = "Times New Roman"; r2.font.size = Pt(8.5)
    
    # Row 1: Project Title (Merged)
    t_meta.rows[1].cells[0].merge(t_meta.rows[1].cells[1])
    p = t_meta.rows[1].cells[0].paragraphs[0]
    r1 = p.add_run("Project Title: ")
    r1.font.name = "Times New Roman"; r1.font.size = Pt(8.5); r1.font.bold = True
    r2 = p.add_run(PROJECT_TITLE)
    r2.font.name = "Times New Roman"; r2.font.size = Pt(8.5)
    
    # Row 2: Cohort | Guide
    p = t_meta.rows[2].cells[0].paragraphs[0]
    r1 = p.add_run("Cohort: ")
    r1.font.name = "Times New Roman"; r1.font.size = Pt(8.5); r1.font.bold = True
    r2 = p.add_run(COHORT)
    r2.font.name = "Times New Roman"; r2.font.size = Pt(8.5)
    
    p = t_meta.rows[2].cells[1].paragraphs[0]
    r1 = p.add_run("Project Guide: ")
    r1.font.name = "Times New Roman"; r1.font.size = Pt(8.5); r1.font.bold = True
    r2 = p.add_run(GUIDE)
    r2.font.name = "Times New Roman"; r2.font.size = Pt(8.5)
    
    # Spacer
    p_sp2 = doc.add_paragraph()
    p_sp2.paragraph_format.space_before = Pt(0)
    p_sp2.paragraph_format.space_after = Pt(2.5)
    
    # 3. Student Details Table
    t_stud = doc.add_table(rows=1 + len(STUDENTS), cols=5)
    t_stud.alignment = WD_TABLE_ALIGNMENT.CENTER
    docx_set_table_borders(t_stud, color=HEX_BORDER, sz="4")
    
    st_widths = [Pt(26.0), Pt(155.0), Pt(90.0), Pt(165.0), Pt(87.3)]
    st_hdrs = ["S.No.", "Student Name", "Student ID", "Project Contribution Module", "Signature"]
    
    for i, h in enumerate(st_hdrs):
        cell = t_stud.rows[0].cells[i]
        cell.width = st_widths[i]
        docx_set_cell_bg(cell, HEX_NAVY_MID)
        docx_set_cell_margins(cell, top=40, bottom=40, left=50, right=50)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        r_h = p.add_run(h)
        r_h.font.name = "Times New Roman"; r_h.font.size = Pt(8.0); r_h.font.bold = True
        r_h.font.color.rgb = RGBColor(255, 255, 255)
        
    for r_i, (sno, name, sid, module) in enumerate(STUDENTS):
        row = t_stud.rows[r_i + 1]
        bg_color = HEX_WHITE if r_i % 2 == 0 else HEX_ALT_ROW
        for c_i, val in enumerate([sno, name, sid, module, ""]):
            cell = row.cells[c_i]
            cell.width = st_widths[c_i]
            docx_set_cell_bg(cell, bg_color)
            docx_set_cell_margins(cell, top=35, bottom=35, left=50, right=50)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i in [0, 2, 4] else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            r_c = p.add_run(val)
            r_c.font.name = "Times New Roman"; r_c.font.size = Pt(8.0)
            
    # Spacer
    p_sp3 = doc.add_paragraph()
    p_sp3.paragraph_format.space_before = Pt(0)
    p_sp3.paragraph_format.space_after = Pt(2.5)
    
    # Helper to add section banners in docx
    def docx_add_banner(title_text):
        t_b = doc.add_table(rows=1, cols=1)
        t_b.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = t_b.rows[0].cells[0]
        cell.width = total_w
        docx_set_cell_bg(cell, HEX_ALT_ROW)
        docx_set_banner_borders(t_b, bar_color=HEX_NAVY_DARK, border_color=HEX_BORDER)
        docx_set_cell_margins(cell, top=30, bottom=30, left=80, right=80)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        r_t = p.add_run(title_text.upper())
        r_t.font.name = "Times New Roman"; r_t.font.size = Pt(8.5); r_t.font.bold = True
        r_t.font.color.rgb = RGBColor(11, 37, 69)
        
    # 4. Section 1: Brief Description
    docx_add_banner("1. Brief Description of the Project")
    
    p_d1 = doc.add_paragraph()
    p_d1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_d1.paragraph_format.space_before = Pt(2)
    p_d1.paragraph_format.space_after = Pt(1.5)
    p_d1.paragraph_format.line_spacing = 1.05
    r_d1 = p_d1.add_run(BRIEF_DESC_P1)
    r_d1.font.name = "Times New Roman"; r_d1.font.size = Pt(8.2)
    
    p_d2 = doc.add_paragraph()
    p_d2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_d2.paragraph_format.space_before = Pt(0)
    p_d2.paragraph_format.space_after = Pt(2.5)
    p_d2.paragraph_format.line_spacing = 1.05
    r_d2 = p_d2.add_run(BRIEF_DESC_P2)
    r_d2.font.name = "Times New Roman"; r_d2.font.size = Pt(8.2)
    
    # 5. Section 2: Progress Achieved
    docx_add_banner("2. Progress Achieved up to This Review Stage")
    for lbl, txt in r['bullets']:
        p_blt = doc.add_paragraph()
        p_blt.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_blt.paragraph_format.space_before = Pt(0)
        p_blt.paragraph_format.space_after = Pt(1.5)
        p_blt.paragraph_format.line_spacing = 1.05
        
        r_sym = p_blt.add_run("■ ")
        r_sym.font.name = "Times New Roman"; r_sym.font.size = Pt(7.5); r_sym.font.bold = True
        r_sym.font.color.rgb = RGBColor(11, 37, 69)
        
        r_l = p_blt.add_run(lbl)
        r_l.font.name = "Times New Roman"; r_l.font.size = Pt(8.2); r_l.font.bold = True
        
        r_t = p_blt.add_run(txt)
        r_t.font.name = "Times New Roman"; r_t.font.size = Pt(8.2)
        
    # Spacer
    p_sp4 = doc.add_paragraph()
    p_sp4.paragraph_format.space_before = Pt(0)
    p_sp4.paragraph_format.space_after = Pt(2.0)
    
    # 6. Section 3: Quantitative Results Table
    docx_add_banner(f"3. {r['table_title']}")
    
    t_res = doc.add_table(rows=1 + len(r['table_rows']), cols=len(r['table_headers']))
    t_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    docx_set_table_borders(t_res, color=HEX_BORDER, sz="4")
    
    num_cols = len(r['table_headers'])
    col_w_res = [Pt(523.3 / num_cols)] * num_cols
    
    for c_i, h in enumerate(r['table_headers']):
        cell = t_res.rows[0].cells[c_i]
        cell.width = col_w_res[c_i]
        docx_set_cell_bg(cell, HEX_NAVY_MID)
        docx_set_cell_margins(cell, top=35, bottom=35, left=40, right=40)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        r_h = p.add_run(h)
        r_h.font.name = "Times New Roman"; r_h.font.size = Pt(7.5); r_h.font.bold = True
        r_h.font.color.rgb = RGBColor(255, 255, 255)
        
    for r_i, row_data in enumerate(r['table_rows']):
        row = t_res.rows[r_i + 1]
        bg_color = HEX_WHITE if r_i % 2 == 0 else HEX_ALT_ROW
        for c_i, val in enumerate(row_data):
            cell = row.cells[c_i]
            cell.width = col_w_res[c_i]
            docx_set_cell_bg(cell, bg_color)
            docx_set_cell_margins(cell, top=30, bottom=30, left=40, right=40)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_i == 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            r_c = p.add_run(val)
            r_c.font.name = "Times New Roman"; r_c.font.size = Pt(7.5)
            
    # Spacer
    p_sp5 = doc.add_paragraph()
    p_sp5.paragraph_format.space_before = Pt(0)
    p_sp5.paragraph_format.space_after = Pt(2.5)
    
    # 7. Section 4: Guide Sign-off Box Table
    t_sign = doc.add_table(rows=1, cols=2)
    t_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
    docx_set_table_borders(t_sign, color=HEX_NAVY_DARK, sz="6")
    
    col_w_sign = [Pt(300.0), Pt(223.3)]
    for idx, cell in enumerate(t_sign.rows[0].cells):
        cell.width = col_w_sign[idx]
        docx_set_cell_bg(cell, HEX_LIGHT_BG)
        docx_set_cell_margins(cell, top=50, bottom=50, left=70, right=70)
        cell.paragraphs[0].paragraph_format.space_before = Pt(0)
        cell.paragraphs[0].paragraph_format.space_after = Pt(0)
        cell.paragraphs[0].paragraph_format.line_spacing = 1.05
        
    p_s1 = t_sign.rows[0].cells[0].paragraphs[0]
    r_st1 = p_s1.add_run("Evaluation Status: ")
    r_st1.font.name = "Times New Roman"; r_st1.font.size = Pt(8.0); r_st1.font.bold = True
    r_st2 = p_s1.add_run("[✔] Approved — All Milestone Deliverables Verified\n")
    r_st2.font.name = "Times New Roman"; r_st2.font.size = Pt(8.0); r_st2.font.bold = True
    r_st2.font.color.rgb = RGBColor(30, 126, 52)
    
    r_nf1 = p_s1.add_run("Next Action Focus: ")
    r_nf1.font.name = "Times New Roman"; r_nf1.font.size = Pt(7.8); r_nf1.font.bold = True
    r_nf2 = p_s1.add_run(r['next_focus'])
    r_nf2.font.name = "Times New Roman"; r_nf2.font.size = Pt(7.8)
    
    p_s2 = t_sign.rows[0].cells[1].paragraphs[0]
    p_s2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_sg1 = p_s2.add_run("Signature of Project Guide: ___________________________\n")
    r_sg1.font.name = "Times New Roman"; r_sg1.font.size = Pt(8.0); r_sg1.font.bold = True
    r_sg2 = p_s2.add_run(f"Project Guide: {GUIDE}   |   Date: {r['date']}")
    r_sg2.font.name = "Times New Roman"; r_sg2.font.size = Pt(8.0)
    
    doc.save(r['docx_name'])
    print(f"Generated DOCX: {r['docx_name']}")

# ==============================================================================
# PDF GENERATION (REPORTLAB)
# ==============================================================================
class SinglePageCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page_count = 0

    def showPage(self):
        self.page_count += 1
        super().showPage()

    def save(self):
        if self.page_count > 1:
            print(f"WARNING: PDF has {self.page_count} pages! Expected exactly 1.")
        else:
            print(f"SUCCESS: PDF generated with exactly {self.page_count} page.")
        super().save()

def generate_pdf(r):
    availWidth = A4[0] - 56  # 28 left, 28 right -> 539.27 pt
    availHeight = A4[1] - 36 # 18 top, 18 bottom -> 805.89 pt
    
    doc = SimpleDocTemplate(
        r['pdf_name'],
        pagesize=A4,
        leftMargin=28,
        rightMargin=28,
        topMargin=18,
        bottomMargin=18
    )
    
    styles = getSampleStyleSheet()
    
    # 1. Header Banner
    banner_p = Paragraph(
        "<font size='13.5' color='white'><b>CAPSTONE PROJECT REVIEW PROGRESS RECORD</b></font><br/>"
        "<font size='8' color='#CBD5E1'>DEPARTMENT OF ELECTRONICS & COMMUNICATION ENGINEERING | B.TECH CAPSTONE 2026–2027</font>",
        ParagraphStyle('b_title', fontName='Times-Bold', alignment=1, leading=15)
    )
    banner_table = Table([[banner_p]], colWidths=[availWidth])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CLR_NAVY_DARK),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    
    # 2. Metadata Grid
    m_r1_c1 = Paragraph(f"<b>Review Stage:</b> <font color='#0B2545'><b>Review {r['num']}</b></font>", ParagraphStyle('m1', fontName='Times-Roman', fontSize=9, leading=12))
    m_r1_c2 = Paragraph(f"<b>Date of Review:</b> {r['date']}", ParagraphStyle('m2', fontName='Times-Roman', fontSize=9, leading=12))
    m_r2_c1 = Paragraph(f"<b>Project Title:</b> {PROJECT_TITLE}", ParagraphStyle('m3', fontName='Times-Roman', fontSize=9, leading=12))
    m_r3_c1 = Paragraph(f"<b>Cohort:</b> {COHORT}", ParagraphStyle('m4', fontName='Times-Roman', fontSize=9, leading=12))
    m_r3_c2 = Paragraph(f"<b>Project Guide:</b> {GUIDE}", ParagraphStyle('m5', fontName='Times-Roman', fontSize=9, leading=12))
    
    meta_table = Table([
        [m_r1_c1, m_r1_c2],
        [m_r2_c1, ''],
        [m_r3_c1, m_r3_c2]
    ], colWidths=[availWidth * 0.55, availWidth * 0.45])
    meta_table.setStyle(TableStyle([
        ('SPAN', (0,1), (1,1)),
        ('BACKGROUND', (0,0), (-1,-1), CLR_LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 0.75, CLR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    
    # 3. Student Table
    st_hdr = ParagraphStyle('sth', fontName='Times-Bold', fontSize=8.5, leading=10, textColor=CLR_WHITE, alignment=1)
    st_c = ParagraphStyle('stc', fontName='Times-Roman', fontSize=8.5, leading=10, alignment=1)
    st_l = ParagraphStyle('stl', fontName='Times-Roman', fontSize=8.5, leading=10, alignment=0)
    
    col_w_st = [28, 160, 95, 168, 88.27]
    st_data = [
        [
            Paragraph("S.No.", st_hdr),
            Paragraph("Student Name", st_hdr),
            Paragraph("Student ID", st_hdr),
            Paragraph("Project Contribution Module", st_hdr),
            Paragraph("Signature", st_hdr)
        ]
    ]
    for sno, name, sid, module in STUDENTS:
        st_data.append([
            Paragraph(sno, st_c),
            Paragraph(name, st_l),
            Paragraph(sid, st_c),
            Paragraph(module, st_l),
            Paragraph("", st_c)
        ])
    st_table = Table(st_data, colWidths=col_w_st)
    st_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CLR_NAVY_MID),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [CLR_WHITE, CLR_ALT_ROW]),
        ('BOX', (0,0), (-1,-1), 0.75, CLR_NAVY_MID),
        ('INNERGRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    
    # Section Banner Builder
    def make_sec_banner(title):
        p = Paragraph(f"<b>{title.upper()}</b>", ParagraphStyle('sb', fontName='Times-Bold', fontSize=8.8, textColor=CLR_NAVY_DARK, leading=10.5))
        t = Table([[p]], colWidths=[availWidth])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), CLR_ALT_ROW),
            ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER),
            ('LINEBEFORE', (0,0), (0,0), 3.5, CLR_NAVY_DARK),
            ('TOPPADDING', (0,0), (-1,-1), 2.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
        ]))
        return t
        
    # 4. Section 1: Brief Description
    sec1_t = make_sec_banner("1. Brief Description of the Project")
    desc_p1 = Paragraph(BRIEF_DESC_P1, ParagraphStyle('dp1', fontName='Times-Roman', fontSize=8.8, leading=11.3, alignment=4))
    desc_p2 = Paragraph(BRIEF_DESC_P2, ParagraphStyle('dp2', fontName='Times-Roman', fontSize=8.8, leading=11.3, alignment=4))
    
    # 5. Section 2: Progress Achieved
    sec2_t = make_sec_banner("2. Progress Achieved up to This Review Stage")
    blt_style = ParagraphStyle('blts', fontName='Times-Roman', fontSize=8.8, leading=11.3, alignment=4, leftIndent=10, firstLineIndent=-10)
    bullets_list = []
    for lbl, txt in r['bullets']:
        b_p = Paragraph(f"<font color='#0B2545'>■</font> <b>{lbl}</b>{txt}", blt_style)
        bullets_list.append(b_p)
        
    # 6. Section 3: Quantitative Results Table
    sec3_t = make_sec_banner(f"3. {r['table_title']}")
    qh_style = ParagraphStyle('qh', fontName='Times-Bold', fontSize=8, leading=9.5, textColor=CLR_WHITE, alignment=1)
    qc_style = ParagraphStyle('qc', fontName='Times-Roman', fontSize=8, leading=9.5, alignment=1)
    ql_style = ParagraphStyle('ql', fontName='Times-Roman', fontSize=8, leading=9.5, alignment=0)
    
    q_cols_w = [availWidth / len(r['table_headers'])] * len(r['table_headers'])
    q_data = [[Paragraph(h, qh_style) for h in r['table_headers']]]
    for row in r['table_rows']:
        row_paras = []
        for idx, cell in enumerate(row):
            align_style = ql_style if idx == 0 else qc_style
            row_paras.append(Paragraph(cell, align_style))
        q_data.append(row_paras)
    q_table = Table(q_data, colWidths=q_cols_w)
    q_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CLR_NAVY_MID),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [CLR_WHITE, CLR_ALT_ROW]),
        ('BOX', (0,0), (-1,-1), 0.75, CLR_NAVY_MID),
        ('INNERGRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    
    # 7. Sign-Off & Next Steps Table
    sign_status_p = Paragraph(
        f"<b>Evaluation Status:</b> <font color='#1E7E34'><b>[✔] Approved — All Milestone Deliverables Verified</b></font><br/>"
        f"<b>Next Action Focus:</b> {r['next_focus']}",
        ParagraphStyle('ssp', fontName='Times-Roman', fontSize=8.5, leading=11)
    )
    sign_sig_p = Paragraph(
        f"<b>Signature of Project Guide:</b> ___________________________<br/>"
        f"<b>Project Guide:</b> {GUIDE} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Date:</b> {r['date']}",
        ParagraphStyle('ssp2', fontName='Times-Roman', fontSize=8.5, leading=11, alignment=2)
    )
    sign_table = Table([[sign_status_p, sign_sig_p]], colWidths=[availWidth * 0.56, availWidth * 0.44])
    sign_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CLR_LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 0.75, CLR_NAVY_DARK),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    
    story = [
        banner_table,
        Spacer(1, 3.5),
        meta_table,
        Spacer(1, 3.5),
        st_table,
        Spacer(1, 3.5),
        sec1_t,
        Spacer(1, 2),
        desc_p1,
        Spacer(1, 2),
        desc_p2,
        Spacer(1, 3.5),
        sec2_t,
        Spacer(1, 2),
    ]
    for b in bullets_list:
        story.append(b)
        story.append(Spacer(1, 1.8))
    story.append(Spacer(1, 2.5))
    story.append(sec3_t)
    story.append(Spacer(1, 2))
    story.append(q_table)
    story.append(Spacer(1, 3.5))
    story.append(sign_table)
    
    doc.build(story, canvasmaker=SinglePageCanvas)
    print(f"Generated PDF: {r['pdf_name']}")

# ==============================================================================
# MAIN DRIVER
# ==============================================================================
if __name__ == "__main__":
    print("======================================================================")
    print("GENERATING PROFESSIONAL FULL-PAGE CAPSTONE PROGRESS RECORDS (DOCX & PDF)")
    print("======================================================================")
    for r in REVIEWS_DATA:
        print(f"\n>>> Processing Review {r['num']} ({r['date']}) <<<")
        generate_docx(r)
        generate_pdf(r)
    print("\nAll 3 Reviews successfully updated in both DOCX and PDF formats!")
