"""
USPTO Provisional Patent Application PDF Generator
Converts PROVISIONAL_PATENT_USPTO_READY.md to professional PDF format
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
import re
from datetime import datetime

def create_patent_pdf():
    """Generate USPTO-compliant PDF from markdown file"""
    
    # Read the markdown file
    with open('PROVISIONAL_PATENT_USPTO_READY.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Output PDF filename
    output_filename = f"USPTO_Provisional_Patent_Casey_Schroder_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    # Create PDF document with USPTO-compliant margins (1 inch all sides)
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        rightMargin=1*inch,
        leftMargin=1*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName='Times-Bold'
    )
    
    # Heading 2 style
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=12,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=10,
        spaceBefore=12,
        fontName='Times-Bold'
    )
    
    # Heading 3 style
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=11,
        leading=13,
        alignment=TA_LEFT,
        spaceAfter=8,
        spaceBefore=10,
        fontName='Times-Bold'
    )
    
    # Normal body text (USPTO requires double-spacing equivalent)
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=22,  # Double spacing
        alignment=TA_JUSTIFY,
        fontName='Times-Roman'
    )
    
    # Claim style (numbered)
    claim_style = ParagraphStyle(
        'ClaimStyle',
        parent=styles['Normal'],
        fontSize=11,
        leading=22,
        alignment=TA_JUSTIFY,
        fontName='Times-Roman',
        leftIndent=0.5*inch,
        firstLineIndent=-0.5*inch
    )
    
    # Build document content
    story = []
    
    # Split content into sections
    lines = content.split('\n')
    
    in_claims_section = False
    skip_line = False
    
    for i, line in enumerate(lines):
        # Skip markdown horizontal rules
        if line.strip().startswith('---'):
            story.append(Spacer(1, 0.2*inch))
            continue
        
        # Skip empty lines (we'll add spacing manually)
        if not line.strip():
            continue
        
        # Main title (# PROVISIONAL PATENT APPLICATION)
        if line.startswith('# ') and 'PROVISIONAL PATENT APPLICATION' in line:
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("PROVISIONAL PATENT APPLICATION", title_style))
            story.append(Spacer(1, 0.3*inch))
            continue
        
        # Section headers (##)
        if line.startswith('## '):
            text = line.replace('## ', '').strip()
            if text == "CLAIMS":
                in_claims_section = True
                story.append(PageBreak())
            story.append(Paragraph(text, heading2_style))
            continue
        
        # Subsection headers (###)
        if line.startswith('### '):
            text = line.replace('### ', '').strip()
            story.append(Paragraph(text, heading3_style))
            continue
        
        # Subsubsection headers (####)
        if line.startswith('#### '):
            text = line.replace('#### ', '').strip()
            story.append(Paragraph(f"<b>{text}</b>", body_style))
            continue
        
        # Handle claims with special formatting
        if in_claims_section and line.startswith('**Claim'):
            # Extract claim number and text
            claim_match = re.match(r'\*\*Claim (\d+):\*\* (.+)', line)
            if claim_match:
                claim_num = claim_match.group(1)
                claim_text = claim_match.group(2)
                # Format as numbered claim
                story.append(Paragraph(f"<b>{claim_num}.</b> {claim_text}", claim_style))
                continue
        
        # Bold text in markdown (**text**)
        if '**' in line:
            # Convert markdown bold to HTML bold
            line = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
        
        # Bullet points
        if line.strip().startswith('- '):
            text = line.strip()[2:]
            story.append(Paragraph(f"• {text}", body_style))
            continue
        
        # Numbered lists with letters
        if re.match(r'^\s+[a-z]\)', line):
            text = line.strip()
            story.append(Paragraph(f"    {text}", body_style))
            continue
        
        # Regular paragraphs
        if line.strip():
            story.append(Paragraph(line.strip(), body_style))
            story.append(Spacer(1, 0.1*inch))
    
    # Add signature block at end
    story.append(PageBreak())
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("_________________________________", body_style))
    story.append(Paragraph("Signature", body_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", body_style))
    
    # Build PDF
    print(f"Generating USPTO-compliant PDF: {output_filename}")
    doc.build(story)
    print(f"✅ SUCCESS! PDF created: {output_filename}")
    print(f"\nFile location: {output_filename}")
    print("\nNext steps:")
    print("1. Open the PDF and verify all content is correct")
    print("2. Print the signature page, sign it, and scan it")
    print("3. Upload to USPTO Patent Center at: https://patentcenter.uspto.gov")
    print("4. Select 'Provisional Application for Patent'")
    print("5. Pay filing fee: $130 (small entity) or $260 (regular)")
    
    return output_filename

if __name__ == "__main__":
    try:
        create_patent_pdf()
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\nMake sure you have reportlab installed:")
        print("pip install reportlab")
