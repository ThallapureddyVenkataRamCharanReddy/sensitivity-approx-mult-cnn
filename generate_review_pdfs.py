"""
generate_review_pdfs.py
========================
Generates official, university-styled PDF progress records for:
  - Review 1: 7 August 2026
  - Review 2: 3 October 2026
  - Review 3: 6 November 2026
And a combined document containing all three.
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Color Palette (ECE / University academic theme)
PRIMARY_COLOR   = colors.HexColor("#1A365D")   # Deep Navy
SECONDARY_COLOR = colors.HexColor("#7B1113")   # Maroon / Crimson
TEXT_DARK       = colors.HexColor("#1A202C")   # Near Black
BORDER_COLOR    = colors.HexColor("#CBD5E0")   # Soft Gray
BG_HEADER       = colors.HexColor("#EDF2F7")   # Light Slate
BG_SECTION      = colors.HexColor("#F7FAFC")   # Off-white

STYLES = getSampleStyleSheet()

# Custom Paragraph Styles
STYLE_TITLE = ParagraphStyle(
    "DocTitle",
    parent=STYLES["Normal"],
    fontName="Helvetica-Bold",
    fontSize=13,
    leading=16,
    alignment=1, # Center
    textColor=PRIMARY_COLOR,
    spaceAfter=4,
)

STYLE_SUBTITLE = ParagraphStyle(
    "DocSubtitle",
    parent=STYLES["Normal"],
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=13,
    alignment=1, # Center
    textColor=SECONDARY_COLOR,
    spaceAfter=8,
)

STYLE_HEADER_KEY = ParagraphStyle(
    "HeaderKey",
    parent=STYLES["Normal"],
    fontName="Helvetica-Bold",
    fontSize=8.5,
    leading=11,
    textColor=PRIMARY_COLOR,
)

STYLE_HEADER_VAL = ParagraphStyle(
    "HeaderVal",
    parent=STYLES["Normal"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=11,
    textColor=TEXT_DARK,
)

STYLE_SEC_TITLE = ParagraphStyle(
    "SecTitle",
    parent=STYLES["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9.5,
    leading=12,
    textColor=SECONDARY_COLOR,
    spaceBefore=4,
    spaceAfter=1,
)

STYLE_SEC_SUB = ParagraphStyle(
    "SecSub",
    parent=STYLES["Normal"],
    fontName="Helvetica-Oblique",
    fontSize=7.5,
    leading=9.5,
    textColor=colors.HexColor("#4A5568"),
    spaceAfter=4,
)

STYLE_BODY = ParagraphStyle(
    "Body",
    parent=STYLES["Normal"],
    fontName="Helvetica",
    fontSize=8,
    leading=10.5,
    textColor=TEXT_DARK,
    spaceAfter=3,
)

STYLE_BULLET = ParagraphStyle(
    "Bullet",
    parent=STYLES["Normal"],
    fontName="Helvetica",
    fontSize=7.8,
    leading=10.2,
    textColor=TEXT_DARK,
    leftIndent=10,
    firstLineIndent=-7,
    spaceAfter=2.5,
)

STYLE_TBL_HEAD = ParagraphStyle(
    "TblHead",
    parent=STYLES["Normal"],
    fontName="Helvetica-Bold",
    fontSize=8,
    leading=10,
    alignment=1,
    textColor=colors.white,
)

STYLE_TBL_CELL = ParagraphStyle(
    "TblCell",
    parent=STYLES["Normal"],
    fontName="Helvetica",
    fontSize=8,
    leading=10,
    alignment=1,
    textColor=TEXT_DARK,
)

STUDENTS = [
    ("1", "Velivala Keerthi", "2320040083"),
    ("2", "T. Venkata Ram Charan Reddy", "2320040017"),
    ("3", "Shaik Hanifa", "2320040009"),
    ("4", "K. Dinesh", "2320040095"),
]

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

REVIEW_DATA = {
    "Review-1": {
        "num": "Review–1",
        "date": "7 August 2026",
        "review_status": "<b>[X] Review–1</b> &nbsp;&nbsp;&nbsp;&nbsp; [ ] Review–2 &nbsp;&nbsp;&nbsp;&nbsp; [ ] Review–3",
        "milestones": [
            ("<b>RTL Multiplier Library Design:</b> Designed four parameterizable 8x8 unsigned multiplier architectures "
             "in synthesizable Verilog: exact (full partial-product array), truncated (LSB column drop), compensated "
             "(constant midpoint rounding bias), and OR-based logic."),
            ("<b>Exhaustive 65,536-Pair Simulation:</b> Verified all 256x256 input combinations in Icarus Verilog; "
             "extracted golden arithmetic error distributions (Mean Error, NMED, MRED, Max Absolute Error)."),
            ("<b>Vivado Out-of-Context Synthesis on Zynq-7020:</b> Obtained post-synthesis FPGA utilization targeting "
             "xc7z020clg400-1. Exact: 68 LUTs; Trunc-4: 56 LUTs (-17.6%); Comp-4: 56 LUTs (-17.6%); OR-4: 64 LUTs (-5.9%)."),
            ("<b>Circuit-Level Dominance Discovery:</b> Proved that Compensated strictly dominates Truncated at identical "
             "LUT cost (56 LUTs) with 35% lower error, as the synthesis tool absorbs the +2^(T-1) constant into existing "
             "carry logic at zero extra hardware overhead. OR-based design proved inferior and was discarded."),
            ("<b>Literature Benchmark & Experimental Protocol:</b> Formulated formal evaluation protocol against ALWANN, "
             "TRAM, Sayadi et al., and Kumari & Rao, establishing strict Spearman gate criteria (|rho| >= 0.70) before "
             "committing to physical hardware RTL design.")
        ]
    },
    "Review-2": {
        "num": "Review–2",
        "date": "3 October 2026",
        "review_status": "[ ] Review–1 &nbsp;&nbsp;&nbsp;&nbsp; <b>[X] Review–2</b> &nbsp;&nbsp;&nbsp;&nbsp; [ ] Review–3",
        "milestones": [
            ("<b>Baseline CNN & Affine INT8 Quantization:</b> Trained 4-conv baseline CNN on Fashion-MNIST (84.69% exact "
             "baseline accuracy). Developed post-training INT8 quantization engine (unsigned 8-bit activations [0, 255], "
             "sign-magnitude weights) matching unsigned hardware multipliers."),
            ("<b>Single-Pass Sensitivity Formulation (S1–S5):</b> Formulated candidate sensitivity metrics. Extracted first-order "
             "loss gradients via TensorFlow GradientTape on a 256-sample calibration batch in 0.2s. Proved conv1 is critical "
             "(S=1.000) while conv4 is highly robust (S=0.014)."),
            ("<b>TRUNC=4 Sweep & Noise Floor Discovery:</b> Executed 12-cell validation sweep across 10,000 test images. "
             "Measured accuracy drops fell within ±0.1% to 0.3%, identifying the CNN resilience boundary and revealing an "
             "initial statistical noise floor (formal NO-GO at TRUNC=4)."),
            ("<b>TRUNC=6 Scaling & Signal Amplification:</b> Scaled truncation depth to T=6 (dropping 21 of 64 partial products, "
             "amplifying NMED by 6.6x to 0.001234, saving 32.5% area). Proof-of-concept tests demonstrated sensitivity assignment "
             "achieved 85.27% accuracy, recovering 81.5% of accuracy lost by uniform approximation."),
            ("<b>Spearman Correlation & Formal Gate Clearance:</b> Proposed combined metric S3 achieved Spearman |rho| = 0.80 "
             "on TRUNC=6, clearing the pre-defined |rho| >= 0.70 GO gate and validating the core research hypothesis.")
        ]
    },
    "Review-3": {
        "num": "Review–3",
        "date": "6 November 2026",
        "review_status": "[ ] Review–1 &nbsp;&nbsp;&nbsp;&nbsp; [ ] Review–2 &nbsp;&nbsp;&nbsp;&nbsp; <b>[X] Review–3 (Final)</b>",
        "milestones": [
            ("<b>NSGA-II Multi-Objective Optimization Benchmark:</b> Implemented evolutionary search across all 256 configurations "
             "optimizing Accuracy Loss vs. LUT Cost. Confirmed our sensitivity-guided assignment lands at the Pareto knee in 0.2s, "
             "achieving a >3,000,000x speedup over genetic search (ALWANN: 7.5 CPU-days)."),
            ("<b>Complete Synthesizable Accelerator RTL:</b> Designed full Verilog datapath (axm_8x8.v, mac_unit.v, conv_pe.v, "
             "layer_controller.v, cnn_accelerator_top.v) with 2-bit runtime mode control and AXI4-Stream interfaces. Verified "
             "across 262,144 exhaustive test vectors with 100% pass (0 mismatches)."),
            ("<b>Automated Vivado Block Design:</b> Developed vivado_block_design.tcl automating Zynq-7020 PS/PL integration, "
             "AXI SmartConnect, and AXI DMA engine (MM2S & S2MM channels) clocked at 100 MHz."),
            ("<b>PYNQ-Z2 On-Board Deployment Pipeline:</b> Extracted INT8 quantized weights (weights_int8.npy), built Python on-board "
             "driver (pynq_inference.py), and authored an interactive 7-cell Jupyter notebook (pynq_cnn_demo.ipynb) for hardware telemetry."),
            ("<b>Publication Readiness & Code Release:</b> Generated all 7 IEEE publication figures, drafted 6-page IEEE manuscript, "
             "compiled comprehensive 20-slide presentation deck with embedded speaker notes, and published repository to GitHub.")
        ]
    }
}

def create_review_flowables(r_key):
    data = REVIEW_DATA[r_key]
    elements = []

    # Title Banner
    elements.append(Paragraph("CAPSTONE PROJECT REVIEW PROGRESS RECORD", STYLE_TITLE))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_COLOR, spaceAfter=6, spaceBefore=0))

    # Header Metadata Table
    header_table_data = [
        [
            Paragraph("<b>Review Stage:</b>", STYLE_HEADER_KEY),
            Paragraph(data["review_status"], STYLE_HEADER_VAL),
            Paragraph("<b>Date of Review:</b>", STYLE_HEADER_KEY),
            Paragraph(f"<b>{data['date']}</b>", STYLE_HEADER_VAL),
        ],
        [
            Paragraph("<b>Project Title:</b>", STYLE_HEADER_KEY),
            Paragraph("Sensitivity-Guided Layer-Wise Approximate Multiplier Mapping for FPGA-Based CNN Accelerators", STYLE_HEADER_VAL),
            Paragraph("<b>Cohort:</b>", STYLE_HEADER_KEY),
            Paragraph("2024–2028 (Batch B4)", STYLE_HEADER_VAL),
        ],
        [
            Paragraph("<b>Project Guide:</b>", STYLE_HEADER_KEY),
            Paragraph("Dr. Arun Nimmala, Associate Professor, Dept. of ECE", STYLE_HEADER_VAL),
            Paragraph("<b>Target HW:</b>", STYLE_HEADER_KEY),
            Paragraph("PYNQ-Z2 (Xilinx Zynq-7020)", STYLE_HEADER_VAL),
        ],
    ]
    t_header = Table(header_table_data, colWidths=[1.1*inch, 3.2*inch, 1.1*inch, 1.8*inch])
    t_header.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_SECTION),
        ('BOX', (0,0), (-1,-1), 1.0, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('SPAN', (1,1), (1,1)), # Keep title clean
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_header)
    elements.append(Spacer(1, 6))

    # Student Details Table
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
            Paragraph("", STYLE_TBL_CELL), # Signature line
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
    elements.append(Spacer(1, 6))

    # Section 1: Brief Description of the Project
    elements.append(Paragraph("Brief Description of the Project", STYLE_SEC_TITLE))
    elements.append(Paragraph("Briefly explain the premise of the project, the problem being addressed and the proposed approach. (less than 200 words)", STYLE_SEC_SUB))
    elements.append(Paragraph(PROJECT_DESC, STYLE_BODY))
    elements.append(Spacer(1, 4))

    # Section 2: Progress Achieved up to This Review
    elements.append(Paragraph("Progress Achieved up to This Review", STYLE_SEC_TITLE))
    elements.append(Paragraph("Briefly mention the work completed, implementation/simulation/experimental progress, results obtained and other major milestones achieved up to this review.", STYLE_SEC_SUB))
    for m in data["milestones"]:
        elements.append(Paragraph(f"• {m}", STYLE_BULLET))
    elements.append(Spacer(1, 8))

    # Signatures Footer
    sig_data = [
        [
            Paragraph("<b>Signature of Team Leader:</b> ___________________________", STYLE_HEADER_KEY),
            Paragraph("<b>Signature of Project Guide:</b> ___________________________", STYLE_HEADER_KEY),
        ],
        [
            Paragraph(f"<b>Date:</b> {data['date']}", STYLE_HEADER_VAL),
            Paragraph(f"<b>Date:</b> {data['date']}", STYLE_HEADER_VAL),
        ]
    ]
    t_sig = Table(sig_data, colWidths=[3.6*inch, 3.6*inch])
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

def build_all_pdfs():
    print("Generating Capstone Review Progress Records (PDF)...")

    # 1. Review 1 PDF
    doc1 = SimpleDocTemplate(
        "Review_1_Progress_Record.pdf",
        pagesize=A4,
        rightMargin=0.45*inch, leftMargin=0.45*inch,
        topMargin=0.4*inch, bottomMargin=0.4*inch
    )
    doc1.build(create_review_flowables("Review-1"))
    print("  -> Generated Review_1_Progress_Record.pdf (Date: 7 August 2026)")

    # 2. Review 2 PDF
    doc2 = SimpleDocTemplate(
        "Review_2_Progress_Record.pdf",
        pagesize=A4,
        rightMargin=0.45*inch, leftMargin=0.45*inch,
        topMargin=0.4*inch, bottomMargin=0.4*inch
    )
    doc2.build(create_review_flowables("Review-2"))
    print("  -> Generated Review_2_Progress_Record.pdf (Date: 3 October 2026)")

    # 3. Review 3 PDF
    doc3 = SimpleDocTemplate(
        "Review_3_Progress_Record.pdf",
        pagesize=A4,
        rightMargin=0.45*inch, leftMargin=0.45*inch,
        topMargin=0.4*inch, bottomMargin=0.4*inch
    )
    doc3.build(create_review_flowables("Review-3"))
    print("  -> Generated Review_3_Progress_Record.pdf (Date: 6 November 2026)")

    # 4. Combined 3-Page PDF
    doc_all = SimpleDocTemplate(
        "Capstone_Project_Reviews_1_2_3.pdf",
        pagesize=A4,
        rightMargin=0.45*inch, leftMargin=0.45*inch,
        topMargin=0.4*inch, bottomMargin=0.4*inch
    )
    from reportlab.platypus import PageBreak
    all_elements = []
    for i, r_key in enumerate(["Review-1", "Review-2", "Review-3"]):
        all_elements.extend(create_review_flowables(r_key))
        if i < 2:
            all_elements.append(PageBreak())
    doc_all.build(all_elements)
    print("  -> Generated Capstone_Project_Reviews_1_2_3.pdf (Combined 3-page document)")

if __name__ == "__main__":
    build_all_pdfs()
