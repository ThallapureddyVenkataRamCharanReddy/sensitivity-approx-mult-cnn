"""
generate_all_review_records.py
===============================
Generates official Capstone Project Review Progress Records in BOTH
Word (.docx) and PDF (.pdf) formats for:
  - Review 1: 7 August 2026
  - Review 2: 3 October 2026
  - Review 3: 6 November 2026

Customizations applied:
  - Review Stage shows ONLY that specific review (e.g. 'Review: Review–1')
  - Removed Target HW field
  - Left Cohort blank with underline: 'Cohort: ______________________________'
  - Removed Team Leader signature; ONLY Project Guide signature at bottom
  - Available in both .docx and .pdf formats
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# ─────────────────────────────────────────────────────────────────────────────
# COMMON METADATA & CONTENT
# ─────────────────────────────────────────────────────────────────────────────
STUDENTS = [
    ("1", "Velivala Keerthi", "2320040083"),
    ("2", "T. Venkata Ram Charan Reddy", "2320040017"),
    ("3", "Shaik Hanifa", "2320040009"),
    ("4", "K. Dinesh", "2320040095"),
]

PROJECT_TITLE = "Sensitivity-Guided Layer-Wise Approximate Multiplier Mapping for FPGA-Based CNN Accelerators"
PROJECT_GUIDE = "Dr. Arun Nimmala, Associate Professor, Dept. of ECE"

PROJECT_DESC = (
    "Convolutional Neural Network (CNN) edge accelerators are constrained by the high area and "
    "power dissipation of Multiply-Accumulate (MAC) datapaths, where 8x8 exact multipliers dominate silicon "
    "cost (68 LUTs on Xilinx Zynq-7020). While approximate computing trades controlled arithmetic error for "
    "hardware savings, uniform approximation causes severe accuracy degradation or negligible gains. Existing "
    "layer-wise mapping methods rely on computationally prohibitive evolutionary search (ALWANN: 7.5 CPU-days) "
    "or GPU retraining loops (TRAM). This project proposes a lightweight, single-pass sensitivity metric computed "
    "in 0.2 seconds combining static weight variance and dynamic loss gradients via a 256-sample calibration probe "
    "without retraining. Layers are ranked such that error-vulnerable early layers receive exact multipliers while "
    "noise-resilient deep layers receive aggressive approximate multipliers. The heterogeneous design is mapped onto "
    "synthesizable Verilog Processing Elements (PEs) and deployed on a PYNQ-Z2 FPGA board via AXI4-Stream DMA, "
    "achieving up to 32.5% multiplier area reduction while preserving baseline classification accuracy."
)

REVIEWS_DATA = {
    "Review-1": {
        "stage": "Review–1",
        "date": "7 August 2026",
        "filename_base": "Review_1_Progress_Record",
        "milestones": [
            ("RTL Multiplier Library Design: Designed four parameterizable 8x8 unsigned multiplier architectures "
             "in synthesizable Verilog: exact (full partial-product array), truncated (LSB column drop), compensated "
             "(constant midpoint rounding bias), and OR-based logic."),
            ("Exhaustive 65,536-Pair Simulation: Verified all 256x256 input combinations in Icarus Verilog; "
             "extracted golden arithmetic error distributions (Mean Error, NMED, MRED, Max Absolute Error)."),
            ("Vivado Out-of-Context Synthesis on Zynq-7020: Obtained post-synthesis FPGA utilization targeting "
             "xc7z020clg400-1. Exact: 68 LUTs; Trunc-4: 56 LUTs (-17.6%); Comp-4: 56 LUTs (-17.6%); OR-4: 64 LUTs (-5.9%)."),
            ("Circuit-Level Dominance Discovery: Proved that Compensated strictly dominates Truncated at identical "
             "LUT cost (56 LUTs) with 35% lower error, as the synthesis tool absorbs the +2^(T-1) constant into existing "
             "carry logic at zero extra hardware overhead. OR-based design proved inferior and was discarded."),
            ("Literature Benchmark & Experimental Protocol: Formulated formal evaluation protocol against ALWANN, "
             "TRAM, Sayadi et al., and Kumari & Rao, establishing strict Spearman gate criteria (|rho| >= 0.70) before "
             "committing to physical hardware RTL design.")
        ]
    },
    "Review-2": {
        "stage": "Review–2",
        "date": "3 October 2026",
        "filename_base": "Review_2_Progress_Record",
        "milestones": [
            ("Baseline CNN & Affine INT8 Quantization: Trained 4-conv baseline CNN on Fashion-MNIST (84.69% exact "
             "baseline accuracy). Developed post-training INT8 quantization engine (unsigned 8-bit activations [0, 255], "
             "sign-magnitude weights) matching unsigned hardware multipliers."),
            ("Single-Pass Sensitivity Formulation (S1–S5): Formulated candidate sensitivity metrics. Extracted first-order "
             "loss gradients via TensorFlow GradientTape on a 256-sample calibration batch in 0.2s. Proved conv1 is critical "
             "(S=1.000) while conv4 is highly robust (S=0.014)."),
            ("TRUNC=4 Sweep & Noise Floor Discovery: Executed 12-cell validation sweep across 10,000 test images. "
             "Measured accuracy drops fell within ±0.1% to 0.3%, identifying the CNN resilience boundary and revealing an "
             "initial statistical noise floor (formal NO-GO at TRUNC=4)."),
            ("TRUNC=6 Scaling & Signal Amplification: Scaled truncation depth to T=6 (dropping 21 of 64 partial products, "
             "amplifying NMED by 6.6x to 0.001234, saving 32.5% area). Proof-of-concept tests demonstrated sensitivity assignment "
             "achieved 85.27% accuracy, recovering 81.5% of accuracy lost by uniform approximation."),
            ("Spearman Correlation & Formal Gate Clearance: Proposed combined metric S3 achieved Spearman |rho| = 0.80 "
             "on TRUNC=6, clearing the pre-defined |rho| >= 0.70 GO gate and validating the core research hypothesis.")
        ]
    },
    "Review-3": {
        "stage": "Review–3",
        "date": "6 November 2026",
        "filename_base": "Review_3_Progress_Record",
        "milestones": [
            ("NSGA-II Multi-Objective Optimization Benchmark: Implemented evolutionary search across all 256 configurations "
             "optimizing Accuracy Loss vs. LUT Cost. Confirmed our sensitivity-guided assignment lands at the Pareto knee in 0.2s, "
             "achieving a >3,000,000x speedup over genetic search (ALWANN: 7.5 CPU-days)."),
            ("Complete Synthesizable Accelerator RTL: Designed full Verilog datapath (axm_8x8.v, mac_unit.v, conv_pe.v, "
             "layer_controller.v, cnn_accelerator_top.v) with 2-bit runtime mode control and AXI4-Stream interfaces. Verified "
             "across 262,144 exhaustive test vectors with 100% pass (0 mismatches)."),
            ("Automated Vivado Block Design: Developed vivado_block_design.tcl automating Zynq-7020 PS/PL integration, "
             "AXI SmartConnect, and AXI DMA engine (MM2S & S2MM channels) clocked at 100 MHz."),
            ("PYNQ-Z2 On-Board Deployment Pipeline: Extracted INT8 quantized weights (weights_int8.npy), built Python on-board "
             "driver (pynq_inference.py), and authored an interactive 7-cell Jupyter notebook (pynq_cnn_demo.ipynb) for hardware telemetry."),
            ("Publication Readiness & Code Release: Generated all 7 IEEE publication figures, drafted 6-page IEEE manuscript, "
             "compiled comprehensive 20-slide presentation deck with embedded speaker notes, and published repository to GitHub.")
        ]
    }
}


# ─────────────────────────────────────────────────────────────────────────────
# 1. PDF GENERATOR (REPORTLAB)
# ─────────────────────────────────────────────────────────────────────────────
PRIMARY_COLOR   = colors.HexColor("#1A365D")   # Deep Navy
SECONDARY_COLOR = colors.HexColor("#7B1113")   # Maroon / Crimson
TEXT_DARK       = colors.HexColor("#1A202C")   # Near Black
BORDER_COLOR    = colors.HexColor("#CBD5E0")   # Soft Gray
BG_HEADER       = colors.HexColor("#EDF2F7")   # Light Slate
BG_SECTION      = colors.HexColor("#F7FAFC")   # Off-white

STYLES = getSampleStyleSheet()

STYLE_TITLE = ParagraphStyle(
    "DocTitle", parent=STYLES["Normal"],
    fontName="Times-Bold", fontSize=13.5, leading=16.5,
    alignment=1, textColor=PRIMARY_COLOR, spaceAfter=4
)
STYLE_HEADER_KEY = ParagraphStyle(
    "HeaderKey", parent=STYLES["Normal"],
    fontName="Times-Bold", fontSize=9, leading=11.5,
    textColor=PRIMARY_COLOR
)
STYLE_HEADER_VAL = ParagraphStyle(
    "HeaderVal", parent=STYLES["Normal"],
    fontName="Times-Roman", fontSize=9, leading=11.5,
    textColor=TEXT_DARK
)
STYLE_SEC_TITLE = ParagraphStyle(
    "SecTitle", parent=STYLES["Normal"],
    fontName="Times-Bold", fontSize=10, leading=12.5,
    textColor=SECONDARY_COLOR, spaceBefore=4, spaceAfter=1
)
STYLE_SEC_SUB = ParagraphStyle(
    "SecSub", parent=STYLES["Normal"],
    fontName="Times-Italic", fontSize=8, leading=10,
    textColor=colors.HexColor("#4A5568"), spaceAfter=3
)
STYLE_BODY = ParagraphStyle(
    "Body", parent=STYLES["Normal"],
    fontName="Times-Roman", fontSize=8.5, leading=11,
    textColor=TEXT_DARK, spaceAfter=3
)
STYLE_BULLET = ParagraphStyle(
    "Bullet", parent=STYLES["Normal"],
    fontName="Times-Roman", fontSize=8.2, leading=10.8,
    textColor=TEXT_DARK, leftIndent=10, firstLineIndent=-7, spaceAfter=2.5
)
STYLE_TBL_HEAD = ParagraphStyle(
    "TblHead", parent=STYLES["Normal"],
    fontName="Times-Bold", fontSize=8.5, leading=10.5,
    alignment=1, textColor=colors.white
)
STYLE_TBL_CELL = ParagraphStyle(
    "TblCell", parent=STYLES["Normal"],
    fontName="Times-Roman", fontSize=8.5, leading=10.5,
    alignment=1, textColor=TEXT_DARK
)

def create_pdf_elements(r_key):
    data = REVIEWS_DATA[r_key]
    elements = []

    # Title Banner
    elements.append(Paragraph("CAPSTONE PROJECT REVIEW PROGRESS RECORD", STYLE_TITLE))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_COLOR, spaceAfter=5, spaceBefore=0))

    # Header Metadata Table (Clean 3 rows, no Target HW, single review stage, blank cohort)
    header_table_data = [
        [
            Paragraph("<b>Review:</b>", STYLE_HEADER_KEY),
            Paragraph(f"<b>{data['stage']}</b>", STYLE_HEADER_VAL),
            Paragraph("<b>Date of Review:</b>", STYLE_HEADER_KEY),
            Paragraph(f"<b>{data['date']}</b>", STYLE_HEADER_VAL),
        ],
        [
            Paragraph("<b>Project Title:</b>", STYLE_HEADER_KEY),
            Paragraph(f"<b>{PROJECT_TITLE}</b>", STYLE_HEADER_VAL),
            Paragraph("", STYLE_HEADER_KEY),
            Paragraph("", STYLE_HEADER_VAL),
        ],
        [
            Paragraph("<b>Cohort:</b>", STYLE_HEADER_KEY),
            Paragraph("______________________________", STYLE_HEADER_VAL),
            Paragraph("<b>Project Guide:</b>", STYLE_HEADER_KEY),
            Paragraph(PROJECT_GUIDE, STYLE_HEADER_VAL),
        ],
    ]
    t_header = Table(header_table_data, colWidths=[1.1*inch, 2.6*inch, 1.1*inch, 2.4*inch])
    t_header.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_SECTION),
        ('BOX', (0,0), (-1,-1), 1.0, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('SPAN', (1,1), (3,1)), # Project Title spans remaining columns
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_header)
    elements.append(Spacer(1, 4))

    # Student Details Heading & Table
    elements.append(Paragraph("<b>Student Details:</b>", STYLE_HEADER_KEY))
    elements.append(Spacer(1, 2))

    student_table_data = [
        [
            Paragraph("S. No.", STYLE_TBL_HEAD),
            Paragraph("Student Name", STYLE_TBL_HEAD),
            Paragraph("Student ID", STYLE_TBL_HEAD),
            Paragraph("Signature", STYLE_TBL_HEAD),
        ]
    ]
    for s in STUDENTS:
        student_table_data.append([
            Paragraph(s[0], STYLE_TBL_CELL),
            Paragraph(s[1], STYLE_TBL_CELL),
            Paragraph(s[2], STYLE_TBL_CELL),
            Paragraph("", STYLE_TBL_CELL),
        ])

    t_students = Table(student_table_data, colWidths=[0.6*inch, 3.2*inch, 1.7*inch, 1.7*inch])
    t_students.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
        ('BOX', (0,0), (-1,-1), 1.0, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_HEADER]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    elements.append(t_students)
    elements.append(Spacer(1, 5))

    # Section 1: Brief Description of the Project
    elements.append(Paragraph("Brief Description of the Project", STYLE_SEC_TITLE))
    elements.append(Paragraph("Briefly explain the premise of the project, the problem being addressed and the proposed approach. (less than 200 words)", STYLE_SEC_SUB))
    elements.append(Paragraph(PROJECT_DESC, STYLE_BODY))
    elements.append(Spacer(1, 4))

    # Section 2: Progress Achieved up to This Review
    elements.append(Paragraph("Progress Achieved up to This Review", STYLE_SEC_TITLE))
    elements.append(Paragraph("Briefly mention the work completed, implementation/simulation/experimental progress, results obtained and other major milestones achieved up to this review.", STYLE_SEC_SUB))
    for m in data["milestones"]:
        parts = m.split(":", 1)
        if len(parts) == 2:
            elements.append(Paragraph(f"• <b>{parts[0]}:</b>{parts[1]}", STYLE_BULLET))
        else:
            elements.append(Paragraph(f"• {m}", STYLE_BULLET))
    elements.append(Spacer(1, 10))

    # Single Guide Signature Footer (No team leader signature)
    sig_data = [
        [
            Paragraph("<b>Signature of Project Guide:</b> ___________________________", STYLE_HEADER_KEY),
            Paragraph("<b>Date:</b> ___________________________", STYLE_HEADER_KEY),
        ]
    ]
    t_sig = Table(sig_data, colWidths=[4.5*inch, 2.7*inch])
    t_sig.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(KeepTogether([
        HRFlowable(width="100%", thickness=0.8, color=BORDER_COLOR, spaceAfter=4, spaceBefore=2),
        t_sig
    ]))

    return elements


# ─────────────────────────────────────────────────────────────────────────────
# 2. WORD (.DOCX) GENERATOR (PYTHON-DOCX)
# ─────────────────────────────────────────────────────────────────────────────
def set_cell_border(cell, **kwargs):
    """
    Set cell borders: top, bottom, left, right.
    """
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(r'''
        <w:tcBorders xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:top w:val="{top_val}" w:sz="4" w:space="0" w:color="{color}"/>
            <w:left w:val="{left_val}" w:sz="4" w:space="0" w:color="{color}"/>
            <w:bottom w:val="{bottom_val}" w:sz="4" w:space="0" w:color="{color}"/>
            <w:right w:val="{right_val}" w:sz="4" w:space="0" w:color="{color}"/>
        </w:tcBorders>
    '''.format(
        top_val=kwargs.get('top', 'single'),
        left_val=kwargs.get('left', 'single'),
        bottom_val=kwargs.get('bottom', 'single'),
        right_val=kwargs.get('right', 'single'),
        color=kwargs.get('color', 'CCCCCC')
    ))
    tcPr.append(tcBorders)

def set_cell_bg(cell, hex_color):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)

def create_docx(r_key):
    data = REVIEWS_DATA[r_key]
    doc = docx.Document()

    # Set 0.6 inch margins on all sides
    for s in doc.sections:
        s.top_margin = Inches(0.55)
        s.bottom_margin = Inches(0.55)
        s.left_margin = Inches(0.65)
        s.right_margin = Inches(0.65)

    # Document Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    r_title = p_title.add_run("CAPSTONE PROJECT REVIEW PROGRESS RECORD")
    r_title.bold = True
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(13)
    r_title.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    # Horizontal Rule below title
    p_hr = doc.add_paragraph()
    p_hr.paragraph_format.space_before = Pt(0)
    p_hr.paragraph_format.space_after = Pt(5)
    p_hr_border = parse_xml(r'<w:pBdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:bottom w:val="single" w:sz="12" w:space="1" w:color="1A365D"/></w:pBdr>')
    p_hr._p.get_or_add_pPr().append(p_hr_border)

    # Metadata Table (3 rows x 4 columns)
    tbl_meta = doc.add_table(rows=3, cols=4)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_meta.autofit = False

    col_widths = [Inches(1.1), Inches(2.6), Inches(1.1), Inches(2.4)]
    for row in tbl_meta.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width

    # Row 0
    tbl_meta.cell(0, 0).text = "Review:"
    tbl_meta.cell(0, 1).text = data["stage"]
    tbl_meta.cell(0, 2).text = "Date of Review:"
    tbl_meta.cell(0, 3).text = data["date"]

    # Row 1: Project Title spans cols 1..3
    tbl_meta.cell(1, 0).text = "Project Title:"
    cell_title = tbl_meta.cell(1, 1)
    cell_title.merge(tbl_meta.cell(1, 3))
    cell_title.text = PROJECT_TITLE

    # Row 2: Cohort blank, Project Guide
    tbl_meta.cell(2, 0).text = "Cohort:"
    tbl_meta.cell(2, 1).text = "______________________________"
    tbl_meta.cell(2, 2).text = "Project Guide:"
    tbl_meta.cell(2, 3).text = PROJECT_GUIDE

    for row_idx, row in enumerate(tbl_meta.rows):
        for col_idx, cell in enumerate(row.cells):
            set_cell_border(cell, color="CCCCCC")
            set_cell_bg(cell, "F7FAFC")
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                for run in p.runs:
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(8.5)
                    run.font.color.rgb = RGBColor(0x1A, 0x20, 0x2C)
            # Bold label columns
            if col_idx in [0, 2] or (row_idx == 0 and col_idx in [1, 3]):
                for p in cell.paragraphs:
                    for r in p.runs:
                        r.bold = True
                        if col_idx in [0, 2]:
                            r.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    # Student Details Label
    p_stu_lbl = doc.add_paragraph()
    p_stu_lbl.paragraph_format.space_before = Pt(4)
    p_stu_lbl.paragraph_format.space_after = Pt(2)
    r_sl = p_stu_lbl.add_run("Student Details:")
    r_sl.bold = True
    r_sl.font.name = "Times New Roman"
    r_sl.font.size = Pt(9)
    r_sl.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    # Student Details Table (5 rows x 4 columns)
    tbl_stu = doc.add_table(rows=5, cols=4)
    tbl_stu.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_stu.autofit = False

    stu_widths = [Inches(0.6), Inches(3.1), Inches(1.8), Inches(1.7)]
    for row in tbl_stu.rows:
        for idx, width in enumerate(stu_widths):
            row.cells[idx].width = width

    stu_headers = ["S. No.", "Student Name", "Student ID", "Signature"]
    for ci, h in enumerate(stu_headers):
        cell = tbl_stu.cell(0, ci)
        cell.text = h
        set_cell_bg(cell, "1A365D")
        set_cell_border(cell, color="CBD5E0")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        for r in p.runs:
            r.bold = True
            r.font.name = "Times New Roman"
            r.font.size = Pt(8.5)
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for ri, s in enumerate(STUDENTS):
        row = tbl_stu.rows[ri + 1]
        row.cells[0].text = s[0]
        row.cells[1].text = s[1]
        row.cells[2].text = s[2]
        row.cells[3].text = ""

        bg = "FFFFFF" if ri % 2 == 0 else "EDF2F7"
        for ci, cell in enumerate(row.cells):
            set_cell_bg(cell, bg)
            set_cell_border(cell, color="CBD5E0")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if ci in [0, 2] else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(8.5)
                r.font.color.rgb = RGBColor(0x1A, 0x20, 0x2C)

    # Section 1: Brief Description
    p_sec1 = doc.add_paragraph()
    p_sec1.paragraph_format.space_before = Pt(5)
    p_sec1.paragraph_format.space_after = Pt(1)
    r_sec1 = p_sec1.add_run("Brief Description of the Project")
    r_sec1.bold = True
    r_sec1.font.name = "Times New Roman"
    r_sec1.font.size = Pt(9.5)
    r_sec1.font.color.rgb = RGBColor(0x7B, 0x11, 0x13)

    p_sub1 = doc.add_paragraph()
    p_sub1.paragraph_format.space_before = Pt(0)
    p_sub1.paragraph_format.space_after = Pt(2.5)
    r_sub1 = p_sub1.add_run("Briefly explain the premise of the project, the problem being addressed and the proposed approach. (less than 200 words)")
    r_sub1.italic = True
    r_sub1.font.name = "Times New Roman"
    r_sub1.font.size = Pt(7.5)
    r_sub1.font.color.rgb = RGBColor(0x4A, 0x55, 0x68)

    p_desc = doc.add_paragraph()
    p_desc.paragraph_format.space_before = Pt(0)
    p_desc.paragraph_format.space_after = Pt(3.5)
    r_desc = p_desc.add_run(PROJECT_DESC)
    r_desc.font.name = "Times New Roman"
    r_desc.font.size = Pt(8.2)
    r_desc.font.color.rgb = RGBColor(0x1A, 0x20, 0x2C)

    # Section 2: Progress Achieved
    p_sec2 = doc.add_paragraph()
    p_sec2.paragraph_format.space_before = Pt(4)
    p_sec2.paragraph_format.space_after = Pt(1)
    r_sec2 = p_sec2.add_run("Progress Achieved up to This Review")
    r_sec2.bold = True
    r_sec2.font.name = "Times New Roman"
    r_sec2.font.size = Pt(9.5)
    r_sec2.font.color.rgb = RGBColor(0x7B, 0x11, 0x13)

    p_sub2 = doc.add_paragraph()
    p_sub2.paragraph_format.space_before = Pt(0)
    p_sub2.paragraph_format.space_after = Pt(2.5)
    r_sub2 = p_sub2.add_run("Briefly mention the work completed, implementation/simulation/experimental progress, results obtained and other major milestones achieved up to this review.")
    r_sub2.italic = True
    r_sub2.font.name = "Times New Roman"
    r_sub2.font.size = Pt(7.5)
    r_sub2.font.color.rgb = RGBColor(0x4A, 0x55, 0x68)

    for m in data["milestones"]:
        p_m = doc.add_paragraph(style='List Bullet')
        p_m.paragraph_format.space_before = Pt(0)
        p_m.paragraph_format.space_after = Pt(2)
        p_m.paragraph_format.left_indent = Inches(0.25)
        parts = m.split(":", 1)
        if len(parts) == 2:
            r_bold = p_m.add_run(parts[0] + ":")
            r_bold.bold = True
            r_bold.font.name = "Times New Roman"
            r_bold.font.size = Pt(8)
            r_bold.font.color.rgb = RGBColor(0x1A, 0x20, 0x2C)
            r_text = p_m.add_run(parts[1])
            r_text.font.name = "Times New Roman"
            r_text.font.size = Pt(8)
            r_text.font.color.rgb = RGBColor(0x1A, 0x20, 0x2C)
        else:
            r_text = p_m.add_run(m)
            r_text.font.name = "Times New Roman"
            r_text.font.size = Pt(8)
            r_text.font.color.rgb = RGBColor(0x1A, 0x20, 0x2C)

    # Footer: Guide Signature ONLY
    p_hr2 = doc.add_paragraph()
    p_hr2.paragraph_format.space_before = Pt(6)
    p_hr2.paragraph_format.space_after = Pt(3)
    p_hr2_border = parse_xml(r'<w:pBdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:bottom w:val="single" w:sz="6" w:space="1" w:color="CBD5E0"/></w:pBdr>')
    p_hr2._p.get_or_add_pPr().append(p_hr2_border)

    tbl_sig = doc.add_table(rows=1, cols=2)
    tbl_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_sig.autofit = False
    tbl_sig.rows[0].cells[0].width = Inches(4.5)
    tbl_sig.rows[0].cells[1].width = Inches(2.7)

    p_sig1 = tbl_sig.rows[0].cells[0].paragraphs[0]
    p_sig1.paragraph_format.space_before = Pt(2)
    p_sig1.paragraph_format.space_after = Pt(2)
    r_s1 = p_sig1.add_run("Signature of Project Guide: ___________________________")
    r_s1.bold = True
    r_s1.font.name = "Times New Roman"
    r_s1.font.size = Pt(8.5)
    r_s1.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    p_sig2 = tbl_sig.rows[0].cells[1].paragraphs[0]
    p_sig2.paragraph_format.space_before = Pt(2)
    p_sig2.paragraph_format.space_after = Pt(2)
    r_s2 = p_sig2.add_run(f"Date: ___________________________")
    r_s2.bold = True
    r_s2.font.name = "Times New Roman"
    r_s2.font.size = Pt(8.5)
    r_s2.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    docx_path = f"{data['filename_base']}.docx"
    doc.save(docx_path)
    print(f"  -> Generated {docx_path}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. BUILD ALL REVIEWS (BOTH DOCX & PDF)
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  Generating Capstone Review Progress Records (Word & PDF)")
    print("=" * 60)

    for r_key in ["Review-1", "Review-2", "Review-3"]:
        data = REVIEWS_DATA[r_key]

        # 1. Build Word (.docx)
        create_docx(r_key)

        # 2. Build PDF (.pdf)
        pdf_path = f"{data['filename_base']}.pdf"
        doc_pdf = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=0.45*inch, leftMargin=0.45*inch,
            topMargin=0.4*inch, bottomMargin=0.4*inch
        )
        doc_pdf.build(create_pdf_elements(r_key))
        print(f"  -> Generated {pdf_path}")

    # Also build a clean combined PDF
    doc_combined = SimpleDocTemplate(
        "Capstone_Project_Reviews_1_2_3.pdf",
        pagesize=A4,
        rightMargin=0.45*inch, leftMargin=0.45*inch,
        topMargin=0.4*inch, bottomMargin=0.4*inch
    )
    from reportlab.platypus import PageBreak
    all_flowables = []
    for i, r_key in enumerate(["Review-1", "Review-2", "Review-3"]):
        all_flowables.extend(create_pdf_elements(r_key))
        if i < 2:
            all_flowables.append(PageBreak())
    doc_combined.build(all_flowables)
    print("  -> Generated Capstone_Project_Reviews_1_2_3.pdf (Combined 3-Page PDF)")

    print("=" * 60)
    print("  All Word (.docx) and PDF (.pdf) files generated successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
