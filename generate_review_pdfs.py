"""
generate_review_pdfs.py
=======================
Generates official, high-quality academic PDF documents for:
  - Review-1 Progress Record (Review_1_Progress_Record.pdf)
  - Review-2 Progress Record (Review_2_Progress_Record.pdf)
  - Review-3 Progress Record (Review_3_Progress_Record.pdf)
  - All-in-One Combined Record (Capstone_Project_Review_Records_All.pdf)

Department of Electronics and Communication Engineering, K L University
Project: Sensitivity-Guided Layer-Wise Approximate Multiplier Mapping
         for FPGA-Based CNN Accelerators
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# ── Color Palette ─────────────────────────────────────────────────────────────
PRIMARY     = colors.HexColor("#1A2B4C")  # Deep Navy
SECONDARY   = colors.HexColor("#9B2D1F")  # Academic Crimson
ACCENT      = colors.HexColor("#D34817")  # Warm Rust
TEXT_DARK   = colors.HexColor("#1A1A1A")  # Off-black
BG_LIGHT    = colors.HexColor("#F8F9FA")  # Subtle gray
BORDER_CLR  = colors.HexColor("#D0D5DD")  # Border gray
LINE_CLR    = colors.HexColor("#CBD5E1")

# ── Styles ────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

style_header_univ = ParagraphStyle(
    "UnivHeader",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=13,
    alignment=1,  # Center
    textColor=SECONDARY,
    spaceAfter=2,
)

style_header_title = ParagraphStyle(
    "MainTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=14,
    leading=18,
    alignment=1,  # Center
    textColor=PRIMARY,
    spaceAfter=6,
)

style_meta_label = ParagraphStyle(
    "MetaLabel",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9,
    leading=12,
    textColor=PRIMARY,
)

style_meta_val = ParagraphStyle(
    "MetaVal",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    textColor=TEXT_DARK,
)

style_th = ParagraphStyle(
    "TH",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=8.5,
    leading=11,
    alignment=1,
    textColor=colors.white,
)

style_td = ParagraphStyle(
    "TD",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=11,
    textColor=TEXT_DARK,
)

style_td_center = ParagraphStyle(
    "TDCenter",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=11,
    alignment=1,
    textColor=TEXT_DARK,
)

style_sec_heading = ParagraphStyle(
    "SecHeading",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=10.5,
    leading=14,
    textColor=PRIMARY,
    spaceBefore=6,
    spaceAfter=2,
)

style_sec_sub = ParagraphStyle(
    "SecSub",
    parent=styles["Normal"],
    fontName="Helvetica-Oblique",
    fontSize=7.5,
    leading=10,
    textColor=colors.HexColor("#475569"),
    spaceAfter=4,
)

style_body = ParagraphStyle(
    "Body",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=11.5,
    textColor=TEXT_DARK,
    alignment=4,  # Justified
    spaceAfter=4,
)

style_bullet_item = ParagraphStyle(
    "BulletItem",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=11.5,
    textColor=TEXT_DARK,
    alignment=4,  # Justified
    spaceAfter=3,
    leftIndent=12,
)

style_sign_label = ParagraphStyle(
    "SignLabel",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9,
    leading=12,
    textColor=PRIMARY,
)

# ── Shared Common Data ────────────────────────────────────────────────────────
PROJECT_TITLE = "Sensitivity-Guided Layer-Wise Approximate Multiplier Mapping for FPGA-Based CNN Accelerators"
COHORT        = "2024 – 2028 (Batch B4)"
SUPERVISOR    = "Dr. Arun Nimmala, Associate Professor, Dept. of ECE"

STUDENTS = [
    ("1", "Velivala Keerthi", "2320040083"),
    ("2", "T. Venkata Ram Charan Reddy", "2320040017"),
    ("3", "Shaik Hanifa", "2320040009"),
    ("4", "K. Dinesh", "2320040095"),
]

BRIEF_DESCRIPTION = (
    "Deep Convolutional Neural Network (CNN) inference on resource-constrained edge hardware is "
    "dominated by Multiply-Accumulate (MAC) units, where 8×8 multipliers consume substantial silicon "
    "area and power (68 LUTs on Xilinx Zynq-7020). Approximate computing offers significant energy and "
    "area reduction by relaxing arithmetic precision. However, uniform approximation across an entire network "
    "causes severe accuracy degradation or yields negligible hardware savings. Existing layer-wise mapping "
    "techniques require multi-day genetic search (e.g., ALWANN requires 7.5 CPU-days) or costly GPU retraining loops.\n\n"
    "This project develops a lightweight, single-pass sensitivity scoring metric computed in just 0.2 seconds "
    "without retraining or iterative search. By coupling static weight variance with dynamic first-order loss gradients "
    "extracted across 256 calibration images, our framework accurately quantifies layer-wise error resilience. "
    "Error-critical early layers (conv1) are allocated exact multipliers, intermediate layers receive compensated designs, "
    "and noise-resilient deep layers (conv4, accounting for 48.5% of total MACs) are assigned aggressive truncated multipliers. "
    "The heterogeneous datapath is realized as a synthesizable AXI4-Stream accelerator IP core for physical deployment "
    "on the Xilinx Zynq-7020 (PYNQ-Z2) FPGA SoC, maximizing silicon efficiency while preserving baseline classification accuracy."
)

# ── Review Specific Data ──────────────────────────────────────────────────────
REVIEWS = {
    1: {
        "review_name": "Review–1",
        "date": "03 / 10 / 2026",
        "progress_points": [
            ("RTL Multiplier Library Design & Characterization: ",
             "Designed synthesizable Verilog modules for four 8×8 unsigned multiplier architectures (Exact, Truncated-4, "
             "Compensated-4, and OR-based) using explicit partial-product arrays. Conducted exhaustive behavioral simulation of all "
             "65,536 input vectors in Icarus Verilog, extracting Mean Error (ME), MAE, NMED, and maximum error bounds."),
            ("Circuit-Level Dominance Proof: ",
             "Synthesized the multiplier library in Xilinx Vivado targeting the Zynq-7020 FPGA. Proved that Compensated multipliers "
             "strictly dominate Truncated designs—both consume identical silicon resources (56 LUTs, −17.6% area vs. 68 LUTs exact) "
             "because the synthesis engine folds the +2^(T-1) (+8) rounding constant into existing carry-in logic at zero extra LUT cost, "
             "while cutting arithmetic error by ~35% (ME = −4.25 vs −12.25)."),
            ("Baseline CNN Architecture & INT8 Quantization: ",
             "Trained a 4-convolutional layer CNN on Fashion-MNIST in TensorFlow/Keras, establishing an exact 32-bit floating-point "
             "baseline test accuracy of 84.69%. Designed an affine INT8 quantization pipeline featuring unsigned 8-bit activations [0, 255] "
             "and signed-magnitude weights matching the unsigned hardware multiplier datapath."),
            ("Sensitivity Metric Formulation (S1–S5): ",
             "Formulated candidate sensitivity metrics. Implemented a single-pass automatic differentiation probe using TensorFlow "
             "GradientTape across 256 calibration images (0.2s runtime). Revealed that conv1 is overwhelmingly sensitive (S=1.000) "
             "due to primitive edge extraction, whereas conv4 is resilient (S=0.014)."),
            ("Preliminary Sweep & Noise Floor Diagnosis: ",
             "Executed the 12-cell layer-by-layer validation sweep using TRUNC=4. Discovered that the CNN's inherent resilience "
             "absorbed the mild TRUNC=4 noise (NMED = 0.000188), producing accuracy drops within ±0.1% to 0.3% (statistical noise floor) "
             "and yielding an initial NO-GO correlation (|ρ| < 0.40). Formulated the plan to scale to TRUNC=6 for signal amplification.")
        ]
    },
    2: {
        "review_name": "Review–2",
        "date": "20 / 10 / 2026",
        "progress_points": [
            ("Noise-Floor Diagnosis & Signal Amplification (TRUNC=6): ",
             "Mathematically analyzed the TRUNC=4 sweep failure, identifying that testing against the binomial noise floor invalidated "
             "ranking correlation. Scaled the approximate multiplier library to TRUNC=6 (discarding columns 0 to 5; 21 of 64 partial products), "
             "amplifying NMED by 6.6× (0.001234) and achieving 32.5% technology-independent gate reduction (247 gates vs 366 exact)."),
            ("Formal Research Gate Clearance (GO Decision): ",
             "Re-ran the 12-cell layer-wise sweep with TRUNC=6. A clear damage contrast emerged: conv1 suffered a heavy 1.85% drop "
             "while conv4 dropped only 0.41%. Our proposed combined metric (S3) achieved a Spearman rank correlation of |ρ| = 0.80, "
             "comfortably exceeding the pre-agreed |ρ| ≥ 0.70 threshold to officially clear the research GO gate."),
            ("The conv4 Computational Asymmetry Discovery: ",
             "Calculated network-wide computational density, proving that conv4 executes 1,806,336 MACs—representing 48.5% of all multiplications "
             "in the entire network—yet possesses near-zero sensitivity (S=0.014). Assigned Truncated-6 to conv4, enabling 32.5% area reduction "
             "across half the entire network's compute engine while preserving 84%+ baseline accuracy."),
            ("NSGA-II Multi-Objective Optimization Baseline: ",
             "Implemented an evolutionary multi-objective search algorithm (DEAP library) across all 256 layer-multiplier combinations "
             "(4 layers × 4 multipliers), optimizing Accuracy Loss vs. MAC-Weighted LUT Cost. Generated the ground-truth Pareto front."),
            ("3,000,000× Search Speedup Demonstration: ",
             "Proved that our proposed single-pass sensitivity assignment (conv1=Exact, conv2/3=Comp-6, conv4=Trunc-6) lands directly at "
             "the Pareto-optimal knee (84.02% accuracy, 57.2 LUTs) in 0.2 seconds. Benchmarked against ALWANN (7.5 CPU-days, 10,800 min) "
             "and localized NSGA-II (~30 min), demonstrating a >3,000,000× reduction in search latency with zero Pareto quality loss.")
        ]
    },
    3: {
        "review_name": "Review–3",
        "date": "06 / 11 / 2026",
        "progress_points": [
            ("Complete Synthesizable Accelerator RTL Microarchitecture: ",
             "Engineered a fully parameterizable CNN accelerator IP in synthesizable Verilog (`cnn_accelerator_top.v`). Implemented a "
             "2-bit dynamic mode controller (`layer_controller.v`), a signed MAC unit with sign-magnitude math (`mac_unit.v`), a 3×3×Cin "
             "Processing Element with finite-state control (`conv_pe.v`), and the unified multi-mode multiplier (`axm_8x8.v`)."),
            ("Exhaustive 262,144-Vector RTL Verification (100% Pass): ",
             "Developed an automated verification suite (`verify_rtl_logic.py`) exhaustively simulating all 4 multiplier modes across all "
             "65,536 input combinations. Verified 262,144/262,144 vectors with zero functional mismatches against golden mathematical models."),
            ("Vivado SoC Integration & Bitstream Automation: ",
             "Authored complete Vivado automation scripts (`vivado_synth.tcl` and `vivado_block_design.tcl`). Partitioned the system into "
             "Processing System (dual ARM Cortex-A9) and Programmable Logic (accelerator IP clocked at 100 MHz), interfaced via AXI DMA "
             "using high-performance HP0 ports for streaming 17-bit packed beats ({w_sign, w_mag, act_in})."),
            ("PYNQ-Z2 On-Board Deployment & Jupyter Driver: ",
             "Developed the physical hardware driver (`pynq_inference.py`) and an interactive 7-cell Jupyter notebook (`pynq_cnn_demo.ipynb`). "
             "Pre-extracted INT8 quantized weights (`weights_int8.npy`) for direct DDR3 memory DMA transfers and real-time on-board latency/FPS measurement."),
            ("Publication-Ready Deliverables & GitHub Repository: ",
             "Generated all 7 publication-grade figures (`fig1`–`fig7`) for the IEEE manuscript, authored a complete 20-slide technical "
             "presentation with embedded figures and full speaker notes, and established a fully documented, open-source GitHub repository "
             "with MIT License.")
        ]
    }
}

def build_pdf(review_num, filename, is_combined=False, doc=None, story=None):
    """Builds a single review progress record PDF or appends to a combined document."""
    rev_data = REVIEWS[review_num]
    local_story = [] if story is None else story

    # ── Header ────────────────────────────────────────────────────────────────
    local_story.append(Paragraph("K L UNIVERSITY", style_header_univ))
    local_story.append(Paragraph("Department of Electronics and Communication Engineering", style_header_univ))
    local_story.append(Paragraph("CAPSTONE PROJECT REVIEW PROGRESS RECORD", style_header_title))
    local_story.append(HRFlowable(width="100%", thickness=1.5, color=SECONDARY, spaceBefore=1, spaceAfter=6))

    # ── Metadata Table ────────────────────────────────────────────────────────
    meta_table_data = [
        [
            Paragraph(f"<b>Review Stage:</b> <font color='{SECONDARY.hexval()}'>{rev_data['review_name']}</font>", style_meta_label),
            Paragraph(f"<b>Date of Review:</b> {rev_data['date']}", style_meta_label)
        ],
        [
            Paragraph("<b>Project Title:</b>", style_meta_label),
            Paragraph(PROJECT_TITLE, style_meta_val)
        ],
        [
            Paragraph("<b>Cohort / Batch:</b>", style_meta_label),
            Paragraph(COHORT, style_meta_val)
        ],
        [
            Paragraph("<b>Project Guide:</b>", style_meta_label),
            Paragraph(SUPERVISOR, style_meta_val)
        ]
    ]

    t_meta = Table(meta_table_data, colWidths=[1.4 * inch, 5.7 * inch])
    t_meta.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (0, 0), (-1, -1), BG_LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.75, BORDER_CLR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_CLR),
    ]))
    local_story.append(t_meta)
    local_story.append(Spacer(1, 6))

    # ── Student Details Table ─────────────────────────────────────────────────
    stud_headers = ["S. No.", "Student Name", "Student ID", "Signature"]
    stud_rows = [[
        Paragraph(s[0], style_td_center),
        Paragraph(f"<b>{s[1]}</b>", style_td),
        Paragraph(s[2], style_td_center),
        Paragraph("", style_td)  # Blank for physical signature
    ] for s in STUDENTS]

    t_stud = Table([[Paragraph(h, style_th) for h in stud_headers]] + stud_rows,
                   colWidths=[0.6 * inch, 3.2 * inch, 1.6 * inch, 1.7 * inch])
    t_stud.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.75, BORDER_CLR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_CLR),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
    ]))
    local_story.append(t_stud)
    local_story.append(Spacer(1, 6))

    # ── Section 1: Brief Description ──────────────────────────────────────────
    local_story.append(Paragraph("Brief Description of the Project", style_sec_heading))
    local_story.append(Paragraph("Briefly explain the premise of the project, the problem being addressed and the proposed approach. (less than 200 words)", style_sec_sub))
    local_story.append(Paragraph(BRIEF_DESCRIPTION, style_body))
    local_story.append(Spacer(1, 4))

    # ── Section 2: Progress Achieved ──────────────────────────────────────────
    local_story.append(Paragraph("Progress Achieved up to This Review", style_sec_heading))
    local_story.append(Paragraph("Briefly mention the work completed, implementation/simulation/experimental progress, results obtained and other major milestones achieved up to this review.", style_sec_sub))

    for idx, (head, body) in enumerate(rev_data["progress_points"], 1):
        txt = f"<b>{idx}. {head}</b>{body}"
        local_story.append(Paragraph(txt, style_bullet_item))

    local_story.append(Spacer(1, 10))

    # ── Signatures ────────────────────────────────────────────────────────────
    sign_table_data = [
        [
            Paragraph("<b>Signature of Project Guide:</b> ___________________________", style_sign_label),
            Paragraph(f"<b>Date:</b> {rev_data['date']}", style_sign_label)
        ]
    ]
    t_sign = Table(sign_table_data, colWidths=[4.6 * inch, 2.5 * inch])
    t_sign.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    local_story.append(KeepTogether([t_sign]))

    # If standalone document, build it
    if not is_combined:
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=32,
            bottomMargin=32
        )
        doc.build(local_story)
        print(f"Generated standalone: {filename}")


def main():
    out_dir = r"C:\Users\venka\Downloads\reasearch"

    # 1. Generate individual review PDFs
    for r in [1, 2, 3]:
        fname = os.path.join(out_dir, f"Review_{r}_Progress_Record.pdf")
        build_pdf(r, fname, is_combined=False)

    # 2. Generate all-in-one combined PDF
    combined_fname = os.path.join(out_dir, "Capstone_Project_Review_Records_All.pdf")
    combined_doc = SimpleDocTemplate(
        combined_fname,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=32,
        bottomMargin=32
    )
    combined_story = []
    for r in [1, 2, 3]:
        build_pdf(r, None, is_combined=True, doc=combined_doc, story=combined_story)
        if r < 3:
            combined_story.append(PageBreak())

    combined_doc.build(combined_story)
    print(f"Generated combined document: {combined_fname}")
    print("=" * 60)
    print("ALL 4 REVIEW PROGRESS RECORD PDFS GENERATED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    main()
