"""Simple PDF Generator for USPTO Patent"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from datetime import datetime

# Read markdown
with open('PROVISIONAL_PATENT_USPTO_READY.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Create PDF
filename = f"Patent_Casey_Schroder_{datetime.now().strftime('%Y%m%d')}.pdf"
doc = SimpleDocTemplate(filename, pagesize=letter, 
                       rightMargin=inch, leftMargin=inch, 
                       topMargin=inch, bottomMargin=inch)

styles = getSampleStyleSheet()
story = []

# Simple conversion - just add paragraphs
for line in content.split('\n'):
    if line.strip():
        if line.startswith('#'):
            line = line.replace('#', '').strip()
        story.append(Paragraph(line.replace('**', '<b>').replace('**', '</b>'), styles['Normal']))
        story.append(Spacer(1, 0.1*inch))

doc.build(story)
print(f"PDF created: {filename}")
