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
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# --- DATA DEFINITIONS ---

STUDENTS = [
    ("1", "Velivala Keerthi", "2320040083"),
    ("2", "T. Venkata Ram Charan Reddy", "2320040017"),
    ("3", "Shaik Hanifa", "2320040009"),
    ("4", "K. Dinesh", "2320040095")
]

PROJECT_TITLE = "Sensitivity-Guided Layer-Wise Approximate Multiplier Mapping for FPGA-Based CNN Accelerators"
COHORT = "Dr. V. Vaishnavi"
GUIDE = "Dr. Arun Nimmala"

BRIEF_DESCRIPTION = (
    "Convolutional Neural Network (CNN) edge accelerators are constrained by the high area and "
    "power dissipation of Multiply-Accumulate (MAC) datapaths, where 8x8 exact multipliers dominate silicon "
    "cost (68 LUTs on Xilinx Zynq-7020). While approximate computing trades controlled arithmetic error for "
    "hardware savings, uniform approximation causes severe accuracy degradation or negligible gains. Existing "
    "layer-wise mapping methods rely on computationally prohibitive evolutionary search (ALWANN: 7.5 CPU-days) "
    "or GPU retraining loops (TRAM). This project proposes a lightweight, single-pass sensitivity metric computed "
    "in 0.2 seconds combining static weight variance and dynamic loss gradients via a 256-sample calibration probe "
    "without retraining. Layers are ranked such that error-vulnerable early layers receive exact multipliers while "
    "noise-resilient deep layers receive aggressive approximate multipliers. The heterogeneous design is mapped "
    "onto synthesizable Verilog Processing Elements (PEs) and deployed on a PYNQ-Z2 FPGA board via AXI4-Stream "
    "DMA, achieving up to 32.5% multiplier area reduction while preserving baseline classification accuracy."
)

REVIEWS_DATA = [
    {
        "num": "01",
        "date": "07.08.2026",
        "docx_name": "Review_01_Progress_Record.docx",
        "pdf_name": "Review_01_Progress_Record.pdf",
        "bullets": [
            ("Multiplier RTL Library Design: ", "Designed 4 distinct 8x8 multiplier architectures in synthesizable Verilog (exact_mult8x8, trunc_mult8x8, compensated_mult8x8, and orbased_mult8x8) parameterized by truncation depth T."),
            ("Exhaustive Simulation & Error Characterization: ", "Developed exhaustive 65,536-vector testbenches in Icarus Verilog; extracted exact error metrics (Mean Error, NMED, MRED, Max Error) across all truncation depths (T=2 to T=6)."),
            ("Vivado Synthesis & Circuit Dominance: ", "Synthesized on Xilinx Zynq-7020 (xc7z020). Demonstrated that Compensated strictly dominates Truncated at identical 56 LUTs (-17.6%) with 35% lower error via zero-cost +2^(T-1) carry-in folding; OR-based discarded."),
            ("Theoretical Sensitivity Formulations: ", "Formulated 5 candidate layer-sensitivity metrics (S1 to S5) combining static weight tensor variance with backpropagated loss gradient norms."),
            ("Benchmark Protocols & Decision Gate: ", "Established baseline evaluation criteria on Fashion-MNIST, test protocols, and defined the strict Spearman rank correlation clearance gate (|ρ| >= 0.70) required prior to hardware datapath commitment.")
        ]
    },
    {
        "num": "02",
        "date": "03.10.2026",
        "docx_name": "Review_02_Progress_Record.docx",
        "pdf_name": "Review_02_Progress_Record.pdf",
        "bullets": [
            ("Baseline CNN & INT8 Quantization: ", "Trained a 4-layer CNN on Fashion-MNIST achieving 84.69% baseline test accuracy; implemented symmetric INT8 post-training quantization with negligible accuracy loss."),
            ("Single-Pass Sensitivity Probing: ", "Implemented TF GradientTape probe calculating sensitivity scores across a 256-sample calibration batch in 0.20s without retraining; proved conv1 is most sensitive (S=1.000) while conv4 is noise-resilient (S=0.014)."),
            ("Validation Sweep & Signal Amplification: ", "Discovered mild truncation (T=4) operated within ±0.1% noise floor; scaled to aggressive T=6 (dropping 21 of 64 PPs, 6.6x NMED increase, 32.5% area savings) to expose true layer resilience differences."),
            ("Proof-of-Concept Accuracy Recovery: ", "Selective mapping with T=6 on conv4 recovered 81.5% of accuracy drop (85.27% accuracy) compared to uniform T=6 (84.00%), confirming the layer-wise hypothesis."),
            ("Spearman Correlation Gate Clearance: ", "Proposed metric S3 achieved Spearman rank correlation |ρ| = 0.80 on TRUNC=6, successfully clearing the mandatory |ρ| >= 0.70 GO gate and finalizing layer multiplier assignments.")
        ]
    },
    {
        "num": "03",
        "date": "06.11.2026",
        "docx_name": "Review_03_Progress_Record.docx",
        "pdf_name": "Review_03_Progress_Record.pdf",
        "bullets": [
            ("Pareto Knee Multi-Objective Benchmark: ", "Executed 256-configuration NSGA-II multi-objective exploration; proved the single-pass sensitivity assignment lands on the Pareto knee in 0.2s (>3,000,000x faster than ALWANN evolutionary search)."),
            ("Synthesizable Accelerator Datapath: ", "Implemented complete Verilog RTL (axm_8x8, mac_unit, conv_pe, layer_controller, cnn_accelerator_top) with AXI4-Stream interfaces; verified via 262,144-cycle testbench with 100% vector match."),
            ("Vivado Block Design Integration: ", "Created automated vivado_block_design.tcl synthesizing and packaging custom IP, integrating ARM Cortex-A9 PS, AXI DMA engines (MM2S & S2MM), and interconnect at 100 MHz."),
            ("PYNQ-Z2 Deployment Stack: ", "Exported quantized INT8 weights/biases (weights_int8.npy), developed Python runtime driver (pynq_inference.py), and created interactive demonstration Jupyter notebook (pynq_cnn_demo.ipynb)."),
            ("Academic Dissemination & GitHub: ", "Authored 6-page IEEE conference paper, generated 7 publication-quality figures, created 20-slide presentation with speaker notes, and published full repository to GitHub.")
        ]
    }
]

# --- DOCX GENERATOR ---

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
        f'  <w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
        f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
        f'  <w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def generate_docx(review_info):
    doc = docx.Document()
    
    # Page setup - A4, exact margins as reference
    section = doc.sections[0]
    section.page_width = Pt(595.3)
    section.page_height = Pt(841.9)
    section.left_margin = Pt(54.0)   # 0.75 in
    section.right_margin = Pt(54.0)  # 0.75 in
    section.top_margin = Pt(36.0)    # 0.5 in
    section.bottom_margin = Pt(36.0) # 0.5 in
    
    # P0: Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(4)
    p_title.paragraph_format.line_spacing = 1.0
    run_title = p_title.add_run("CAPSTONE PROJECT REVIEW PROGRESS RECORD")
    run_title.font.name = "Times New Roman"
    run_title.font.size = Pt(15.0)
    run_title.font.bold = True
    
    # P1: Review & Date
    p_rev = doc.add_paragraph()
    p_rev.paragraph_format.space_before = Pt(0)
    p_rev.paragraph_format.space_after = Pt(2)
    p_rev.paragraph_format.line_spacing = 1.0
    r1 = p_rev.add_run("Review: ")
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(11.0)
    r1.font.bold = True
    r2 = p_rev.add_run(review_info["num"])
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(11.0)
    r3 = p_rev.add_run("\nDate of Review: ")
    r3.font.name = "Times New Roman"
    r3.font.size = Pt(11.0)
    r3.font.bold = True
    r4 = p_rev.add_run(review_info["date"])
    r4.font.name = "Times New Roman"
    r4.font.size = Pt(11.0)
    
    # P2: Project Title
    p_proj = doc.add_paragraph()
    p_proj.paragraph_format.space_before = Pt(0)
    p_proj.paragraph_format.space_after = Pt(2)
    p_proj.paragraph_format.line_spacing = 1.0
    r_pt_l = p_proj.add_run("Project Title: ")
    r_pt_l.font.name = "Times New Roman"
    r_pt_l.font.size = Pt(11.0)
    r_pt_l.font.bold = True
    r_pt_v = p_proj.add_run(PROJECT_TITLE)
    r_pt_v.font.name = "Times New Roman"
    r_pt_v.font.size = Pt(11.0)
    
    # P3: Cohort
    p_coh = doc.add_paragraph()
    p_coh.paragraph_format.space_before = Pt(0)
    p_coh.paragraph_format.space_after = Pt(2)
    p_coh.paragraph_format.line_spacing = 1.0
    r_ch_l = p_coh.add_run("Cohort: ")
    r_ch_l.font.name = "Times New Roman"
    r_ch_l.font.size = Pt(11.0)
    r_ch_l.font.bold = True
    r_ch_v = p_coh.add_run(COHORT)
    r_ch_v.font.name = "Times New Roman"
    r_ch_v.font.size = Pt(11.0)
    
    # P4: Project Guide
    p_gui = doc.add_paragraph()
    p_gui.paragraph_format.space_before = Pt(0)
    p_gui.paragraph_format.space_after = Pt(3)
    p_gui.paragraph_format.line_spacing = 1.0
    r_pg_l = p_gui.add_run("Project Guide: ")
    r_pg_l.font.name = "Times New Roman"
    r_pg_l.font.size = Pt(11.0)
    r_pg_l.font.bold = True
    r_pg_v = p_gui.add_run(GUIDE)
    r_pg_v.font.name = "Times New Roman"
    r_pg_v.font.size = Pt(11.0)
    
    # P5: Student Details Header
    p_sd = doc.add_paragraph()
    p_sd.paragraph_format.space_before = Pt(2)
    p_sd.paragraph_format.space_after = Pt(3)
    p_sd.paragraph_format.line_spacing = 1.0
    r_sd = p_sd.add_run("Student Details:")
    r_sd.font.name = "Times New Roman"
    r_sd.font.size = Pt(11.0)
    r_sd.font.bold = True
    
    # Table: 4 columns
    table = doc.add_table(rows=1 + len(STUDENTS), cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    set_table_borders(table)
    
    col_widths = [Pt(40.0), Pt(210.0), Pt(115.0), Pt(120.0)]
    
    headers = ["S.No.", "Student Name", "Student ID", "Signature"]
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].width = col_widths[i]
        set_cell_margins(hdr_cells[i], top=60, bottom=60, left=100, right=100)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i > 0 else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        run = p.add_run(h)
        run.font.name = "Times New Roman"
        run.font.size = Pt(10.0)
        run.font.bold = True
        
    for r_idx, (sno, name, sid) in enumerate(STUDENTS):
        row_cells = table.rows[r_idx + 1].cells
        for c_idx in range(4):
            row_cells[c_idx].width = col_widths[c_idx]
            set_cell_margins(row_cells[c_idx], top=50, bottom=50, left=100, right=100)
        
        # S.No.
        p0 = row_cells[0].paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        r = p0.add_run(sno)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.0)
        
        # Name
        p1 = row_cells[1].paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        r = p1.add_run(name)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.0)
        
        # ID
        p2 = row_cells[2].paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(0)
        r = p2.add_run(sid)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.0)
        
        # Signature empty
        p3 = row_cells[3].paragraphs[0]
        p3.paragraph_format.space_before = Pt(0)
        p3.paragraph_format.space_after = Pt(0)
        
    # P_desc_h: Brief Description Header
    p_dh = doc.add_paragraph()
    p_dh.paragraph_format.space_before = Pt(4)
    p_dh.paragraph_format.space_after = Pt(2)
    p_dh.paragraph_format.line_spacing = 1.0
    r_dh = p_dh.add_run("Brief Description of the Project")
    r_dh.font.name = "Times New Roman"
    r_dh.font.size = Pt(12.5)
    r_dh.font.bold = True
    
    # P_desc_b: Brief Description Body
    p_db = doc.add_paragraph()
    p_db.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_db.paragraph_format.space_before = Pt(0)
    p_db.paragraph_format.space_after = Pt(3)
    p_db.paragraph_format.line_spacing = 1.0
    r_db = p_db.add_run(BRIEF_DESCRIPTION)
    r_db.font.name = "Times New Roman"
    r_db.font.size = Pt(9.5)
    
    # P_prog_h: Progress Achieved Header
    p_ph = doc.add_paragraph()
    p_ph.paragraph_format.space_before = Pt(3)
    p_ph.paragraph_format.space_after = Pt(2)
    p_ph.paragraph_format.line_spacing = 1.0
    r_ph = p_ph.add_run("Progress Achieved up to This Review")
    r_ph.font.name = "Times New Roman"
    r_ph.font.size = Pt(12.5)
    r_ph.font.bold = True
    
    # Bullets
    for label, text in review_info["bullets"]:
        p_b = doc.add_paragraph()
        p_b.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_b.paragraph_format.space_before = Pt(0)
        p_b.paragraph_format.space_after = Pt(1.5)
        p_b.paragraph_format.line_spacing = 1.0
        
        r_bullet = p_b.add_run("• ")
        r_bullet.font.name = "Times New Roman"
        r_bullet.font.size = Pt(9.5)
        
        r_lbl = p_b.add_run(label)
        r_lbl.font.name = "Times New Roman"
        r_lbl.font.size = Pt(9.5)
        r_lbl.font.bold = True
        
        r_txt = p_b.add_run(text)
        r_txt.font.name = "Times New Roman"
        r_txt.font.size = Pt(9.5)
        
    # Signature line
    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(6)
    p_sig.paragraph_format.space_after = Pt(0)
    p_sig.paragraph_format.line_spacing = 1.0
    
    r_s1 = p_sig.add_run("Signature of Project Guide:")
    r_s1.font.name = "Times New Roman"
    r_s1.font.size = Pt(10.5)
    r_s1.font.bold = True
    
    r_s2 = p_sig.add_run(" ______________________")
    r_s2.font.name = "Times New Roman"
    r_s2.font.size = Pt(10.5)
    
    r_s3 = p_sig.add_run("          ")
    r_s3.font.name = "Times New Roman"
    
    r_s4 = p_sig.add_run("Date:")
    r_s4.font.name = "Times New Roman"
    r_s4.font.size = Pt(10.5)
    r_s4.font.bold = True
    
    r_s5 = p_sig.add_run(" ______________________")
    r_s5.font.name = "Times New Roman"
    r_s5.font.size = Pt(10.5)
    
    doc.save(review_info["docx_name"])
    print(f"Saved DOCX: {review_info['docx_name']}")

# --- PDF GENERATOR (REPORTLAB) ---

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
            print(f"SUCCESS: PDF has exactly {self.page_count} page.")
        super().save()

def generate_pdf(review_info):
    pdf_filename = review_info["pdf_name"]
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=45,
        rightMargin=45,
        topMargin=32,
        bottomMargin=32
    )
    
    printable_width = A4[0] - 90  # 595.27 - 90 = 505.27 pt
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=14.5,
        leading=16.5,
        alignment=1, # Center
        spaceAfter=5
    )
    
    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10.5,
        leading=13,
        spaceAfter=1.5
    )
    
    sd_header_style = ParagraphStyle(
        'SDHeaderStyle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=10.5,
        leading=13,
        spaceBefore=2,
        spaceAfter=2
    )
    
    section_h_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        leading=14,
        spaceBefore=4,
        spaceAfter=2
    )
    
    desc_style = ParagraphStyle(
        'DescStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9,
        leading=11.2,
        alignment=4, # Justify
        spaceAfter=2
    )
    
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9,
        leading=11.2,
        alignment=4, # Justify
        spaceAfter=1.5,
        leftIndent=10
    )
    
    tbl_hdr_style = ParagraphStyle(
        'TblHdr',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=9.5,
        leading=11,
        alignment=1 # Center
    )
    
    tbl_cell_style = ParagraphStyle(
        'TblCell',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9.5,
        leading=11,
        alignment=0 # Left
    )
    
    sig_style = ParagraphStyle(
        'SigStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        leading=13,
        spaceBefore=6
    )
    
    story = []
    
    # 1. Title
    story.append(Paragraph("CAPSTONE PROJECT REVIEW PROGRESS RECORD", title_style))
    story.append(Spacer(1, 2))
    
    # 2. Review and Date
    rev_text = f"<b>Review:</b> {review_info['num']}<br/><b>Date of Review:</b>  {review_info['date']}"
    story.append(Paragraph(rev_text, meta_style))
    
    # 3. Project Title
    proj_text = f"<b>Project Title:</b> {PROJECT_TITLE}"
    story.append(Paragraph(proj_text, meta_style))
    
    # 4. Cohort
    cohort_text = f"<b>Cohort:</b> {COHORT}"
    story.append(Paragraph(cohort_text, meta_style))
    
    # 5. Project Guide
    guide_text = f"<b>Project Guide:</b> {GUIDE}"
    story.append(Paragraph(guide_text, meta_style))
    
    # 6. Student Details Header
    story.append(Paragraph("Student Details:", sd_header_style))
    
    # 7. Table
    # Widths sum to 505 pt
    col_w = [38, 222, 125, 120]
    tbl_data = [
        [
            Paragraph("<b>S.No.</b>", tbl_hdr_style),
            Paragraph("<b>Student Name</b>", tbl_hdr_style),
            Paragraph("<b>Student ID</b>", tbl_hdr_style),
            Paragraph("<b>Signature</b>", tbl_hdr_style)
        ]
    ]
    for sno, name, sid in STUDENTS:
        tbl_data.append([
            Paragraph(sno, tbl_hdr_style),
            Paragraph(name, tbl_cell_style),
            Paragraph(sid, tbl_hdr_style),
            Paragraph("", tbl_cell_style)
        ])
        
    tbl = Table(tbl_data, colWidths=col_w)
    tbl.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 2))
    
    # 8. Brief Description Header & Body
    story.append(Paragraph("Brief Description of the Project", section_h_style))
    story.append(Paragraph(BRIEF_DESCRIPTION, desc_style))
    story.append(Spacer(1, 2))
    
    # 9. Progress Achieved Header & Bullets
    story.append(Paragraph("Progress Achieved up to This Review", section_h_style))
    for label, text in review_info["bullets"]:
        b_html = f"&bull; <b>{label}</b>{text}"
        story.append(Paragraph(b_html, bullet_style))
    
    story.append(Spacer(1, 4))
    
    # 10. Signature Line
    sig_html = "<b>Signature of Project Guide:</b> ______________________ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Date:</b> ______________________"
    story.append(Paragraph(sig_html, sig_style))
    
    doc.build(story, canvasmaker=SinglePageCanvas)
    print(f"Saved PDF: {pdf_filename}")

# --- MAIN RUNNER ---

if __name__ == "__main__":
    for r in REVIEWS_DATA:
        print(f"\n--- Generating Review {r['num']} ---")
        generate_docx(r)
        generate_pdf(r)
    print("\nAll 3 Reviews successfully generated in DOCX and PDF!")
