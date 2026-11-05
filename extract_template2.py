"""Extract theme colors from the PPTX template XML directly."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
import zipfile
import xml.etree.ElementTree as ET

pptx_path = r'C:\Users\venka\.gemini\antigravity\brain\fdf2dd0f-da6e-4dcd-ab0c-7c5088961b1a\.user_uploaded\media_1791049363242.pptx'

# Read theme XML directly from the zip
with zipfile.ZipFile(pptx_path) as z:
    # Find theme file
    theme_files = [f for f in z.namelist() if 'theme' in f.lower() and f.endswith('.xml')]
    print("Theme files:", theme_files)
    
    for tf in theme_files:
        print(f"\n=== {tf} ===")
        xml_content = z.read(tf)
        root = ET.fromstring(xml_content)
        
        # Strip namespaces for easier parsing
        ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
        
        # Color scheme
        for cs in root.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}clrScheme'):
            print(f"Color Scheme: {cs.get('name', '')}")
            for child in cs:
                tag = child.tag.split('}')[-1]
                for sub in child:
                    subtag = sub.tag.split('}')[-1]
                    val = sub.get('val', sub.get('lastClr', ''))
                    print(f"  {tag}: {subtag}={val}")
        
        # Font scheme
        for fs in root.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}fontScheme'):
            print(f"\nFont Scheme: {fs.get('name', '')}")
            for mj in fs.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}majorFont'):
                for lat in mj.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}latin'):
                    print(f"  Major (headings): {lat.get('typeface')}")
            for mn in fs.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}minorFont'):
                for lat in mn.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}latin'):
                    print(f"  Minor (body): {lat.get('typeface')}")

# Now extract table styling from slide 1
prs = Presentation(pptx_path)

print("\n=== SLIDE 1 TABLE ===")
slide1 = prs.slides[0]
for shape in slide1.shapes:
    if shape.has_table:
        table = shape.table
        print(f"Rows: {len(table.rows)}, Cols: {len(table.columns)}")
        for ri, row in enumerate(table.rows):
            for ci, cell in enumerate(row.cells):
                text = cell.text.strip()[:60]
                print(f"  [{ri},{ci}]: [{text}]")
                for para in cell.text_frame.paragraphs:
                    for run in para.runs:
                        f = run.font
                        parts = []
                        if f.name: parts.append(f.name)
                        if f.size: parts.append(str(f.size.pt) + "pt")
                        if f.bold: parts.append("BOLD")
                        try:
                            if f.color and f.color.rgb: parts.append("#" + str(f.color.rgb))
                        except:
                            pass
                        if parts:
                            print(f"          style: {', '.join(parts)}")

# Title slide - title styling
print("\n=== TITLE SLIDE STYLING ===")
for shape in slide1.shapes:
    if shape.has_text_frame and 'Title' in shape.name:
        for para in shape.text_frame.paragraphs:
            print(f"  Alignment: {para.alignment}")
            for run in para.runs:
                f = run.font
                parts = []
                if f.name: parts.append("font=" + f.name)
                if f.size: parts.append("size=" + str(f.size.pt) + "pt")
                if f.bold: parts.append("BOLD")
                try:
                    if f.color and f.color.rgb: parts.append("color=#" + str(f.color.rgb))
                except:
                    parts.append("color=theme-inherited")
                print(f"  Title run: {', '.join(parts)} => [{run.text}]")

# Content slides - check slide 2 for content styling
print("\n=== SLIDE 2 CONTENT STYLING ===")
slide2 = prs.slides[1]
for shape in slide2.shapes:
    if shape.has_text_frame:
        print(f"Shape: {shape.name}")
        for para in shape.text_frame.paragraphs:
            print(f"  Alignment: {para.alignment}, Level: {para.level}")
            for run in para.runs:
                f = run.font
                parts = []
                if f.name: parts.append("font=" + f.name)
                if f.size: parts.append("size=" + str(f.size.pt) + "pt")
                if f.bold: parts.append("BOLD")
                try:
                    if f.color and f.color.rgb: parts.append("color=#" + str(f.color.rgb))
                except:
                    pass
                if parts:
                    print(f"    Run: {', '.join(parts)} => [{run.text[:50]}]")
