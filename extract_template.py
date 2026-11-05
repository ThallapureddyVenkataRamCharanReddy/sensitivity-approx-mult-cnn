"""Extract styling info from the uploaded PPTX template."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu

pptx_path = r'C:\Users\venka\.gemini\antigravity\brain\fdf2dd0f-da6e-4dcd-ab0c-7c5088961b1a\.user_uploaded\media_1791049363242.pptx'
prs = Presentation(pptx_path)

print("=== SLIDE DIMENSIONS ===")
print(f"Width: {prs.slide_width} EMU = {prs.slide_width/914400:.2f} inches")
print(f"Height: {prs.slide_height} EMU = {prs.slide_height/914400:.2f} inches")

print(f"\n=== SLIDE LAYOUTS ({len(prs.slide_layouts)} layouts) ===")
for i, layout in enumerate(prs.slide_layouts):
    print(f"  Layout {i}: {layout.name}")
    for ph in layout.placeholders:
        print(f"    PH {ph.placeholder_format.idx}: {ph.name} type={ph.placeholder_format.type}")

print(f"\n=== SLIDES ({len(prs.slides)} slides) ===")
for i, slide in enumerate(prs.slides):
    print(f"\n--- Slide {i+1} (layout: {slide.slide_layout.name}) ---")
    for shape in slide.shapes:
        print(f"  Shape: type={shape.shape_type}, name={shape.name}")
        print(f"    Pos: left={shape.left}, top={shape.top}, w={shape.width}, h={shape.height}")
        if hasattr(shape, 'text') and shape.text:
            text_preview = shape.text[:120].replace('\n', ' | ')
            print(f"    Text: [{text_preview}]")
        if shape.has_text_frame:
            for pi, para in enumerate(shape.text_frame.paragraphs):
                align = para.alignment
                for run in para.runs:
                    font = run.font
                    parts = []
                    if font.name:
                        parts.append("font=" + font.name)
                    if font.size:
                        parts.append("size=" + str(font.size.pt) + "pt")
                    if font.bold:
                        parts.append("BOLD")
                    if font.italic:
                        parts.append("ITALIC")
                    if font.color and font.color.type is not None:
                        try:
                            parts.append("color=#" + str(font.color.rgb))
                        except:
                            parts.append("color=theme")
                    if parts:
                        txt = run.text[:80]
                        style_str = " | ".join(parts)
                        print(f"    Run[p{pi}]: {style_str} => [{txt}]")
        # Check for fill/background
        if hasattr(shape, 'fill'):
            fill = shape.fill
            if fill.type is not None:
                print(f"    Fill type: {fill.type}")

# Check slide master theme colors
print("\n=== THEME / MASTER ===")
master = prs.slide_masters[0]
print(f"Master slide shapes: {len(master.shapes)}")
for shape in master.shapes:
    print(f"  Master shape: {shape.name}, type={shape.shape_type}")
    if hasattr(shape, 'text') and shape.text:
        print(f"    Text: [{shape.text[:80]}]")
