"""Ultra-Simple PDF Generator - No HTML parsing"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import re

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

# Process each line carefully
for line in content.split('\n'):
    if not line.strip():
        continue
    
    # Remove markdown headers
    if line.startswith('#'):
        line = line.lstrip('#').strip()
    
    # Remove bold markers completely (safer than trying to convert)
    line = line.replace('**', '')
    
    # Escape special characters for reportlab
    line = line.replace('&', '&amp;')
    line = line.replace('<', '&lt;')
    line = line.replace('>', '&gt;')
    
    # Add paragraph
    try:
        story.append(Paragraph(line, styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    except:
        # If paragraph fails, skip it
        pass

# Build PDF
doc.build(story)
print(f"✅ PDF created successfully: {filename}")
print(f"Location: C:\\Users\\schro\\OneDrive\\Desktop\\BugBountyScanner\\workspace\\{filename}")
