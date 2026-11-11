import os
from pptx import Presentation
from pptx.util import Inches

# Initialize presentation
prs = Presentation()

# Loop through files and add them as slides
with open("list", "r") as file:
    for line in file:
            clean_line = line.strip()
            print(clean_line)
            slide = prs.slides.add_slide(prs.slide_layouts[6]) # Use a blank layout
            # Insert image to fill the slide (adjust dimensions as needed)
            slide.shapes.add_picture(clean_line, Inches(0), Inches(0), width=prs.slide_width)
prs.save("output_presentation.pptx")