#!/usr/bin/env python3
"""
SICE Monthly Security Report Generator
Generates a professional PDF monthly security summary with SICE branding
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import os

# SICE Color Scheme
SICE_BLUE = HexColor('#456BAA')
SICE_BLUE_LIGHT = HexColor('#6B8FCC')
SICE_BLUE_DARK = HexColor('#2F4A7A')
WHITE = HexColor('#FFFFFF')
DARK_GRAY = HexColor('#333333')
LIGHT_GRAY = HexColor('#F5F5F5')
ACCENT_GREEN = HexColor('#4CAF50')

def create_monthly_report(filename, month, year, data=None):
    """
    Create a monthly security report PDF
    
    Args:
        filename: Output PDF filename
        month: Month (1-12)
        year: Year
        data: Dictionary with report data
    """
    
    # Default data if not provided
    if data is None:
        data = {
            'total_incidents': 500,
            'security_alerts': 6,
            'gate_checks': 200,
            'cctv_issues': 200,
            'alarm_tests': 4,
            'patrol_hours': 480,
            'personnel_trained': 8,
            'areas_covered': ['Sinoville', 'Montana', 'Pretoria North'],
            'summary': 'All systems operational. Perimeter secured. No critical incidents reported.'
        }
    
    # Setup document
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    
    # Custom styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=SICE_BLUE,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        letterSpacing=1
    )
    
    company_style = ParagraphStyle(
        'CompanyName',
        parent=styles['Normal'],
        fontSize=14,
        textColor=SICE_BLUE_DARK,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=3
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=SICE_BLUE,
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        borderColor=SICE_BLUE,
        borderWidth=2,
        borderPadding=8
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=DARK_GRAY,
        spaceAfter=10,
        alignment=TA_JUSTIFY
    )
    
    # ========== HEADER ==========
    story.append(Spacer(1, 0.2*inch))
    
    # Logo + Company Name
    header_table = Table([
        [Paragraph('<b>S</b>', ParagraphStyle('Logo', parent=styles['Normal'], fontSize=28, textColor=WHITE, alignment=TA_CENTER)), 
         Paragraph('SOFT-ICE CATERING EQUIPMENT<br/><font size=10 color="#666666">SICE Security Operations</font>', company_style)]
    ], colWidths=[0.6*inch, 4.5*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), SICE_BLUE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (0, 0), 12),
        ('RIGHTPADDING', (0, 0), (0, 0), 12),
        ('TOPPADDING', (0, 0), (0, 0), 8),
        ('BOTTOMPADDING', (0, 0), (0, 0), 8),
    ]))
    story.append(header_table)
    
    story.append(Spacer(1, 0.15*inch))
    
    # Title
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    month_name = month_names[month - 1]
    
    story.append(Paragraph(f'MONTHLY SECURITY REPORT — {month_name.upper()} {year}', title_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Report metadata
    meta_data = [
        [f'Report Date: {datetime.now().strftime("%d %B %Y")}', f'Period: {month_name} 1 – {month_name} 30, {year}', 'Prepared By: P DORFLING'],
    ]
    meta_table = Table(meta_data, colWidths=[2*inch, 2*inch, 2*inch])
    meta_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), DARK_GRAY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, 0), 1, SICE_BLUE),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.3*inch))
    
    # ========== EXECUTIVE SUMMARY ==========
    story.append(Paragraph('EXECUTIVE SUMMARY', section_style))
    
    summary_text = data.get('summary', 'All systems operational.')
    story.append(Paragraph(summary_text, normal_style))
    story.append(Spacer(1, 0.15*inch))
    
    # ========== KEY METRICS ==========
    story.append(Paragraph('KEY METRICS', section_style))
    
    metrics_data = [
        ['Metric', 'Value', 'Status'],
        ['Total Incidents', str(data.get('total_incidents', 0)), 'Green' if data.get('total_incidents', 0) == 0 else 'Amber'],
        ['Security Alerts', str(data.get('security_alerts', 0)), 'Green'],
        ['Gate Access Checks', str(data.get('gate_checks', 0)), 'Green'],
        ['CCTV System Issues', str(data.get('cctv_issues', 0)), 'Green'],
        ['Alarm System Tests', str(data.get('alarm_tests', 0)), 'Green'],
        ['Patrol Hours (Total)', str(data.get('patrol_hours', 0)), 'Green'],
        ['Personnel Trained', str(data.get('personnel_trained', 0)), 'Green'],
    ]
    
    metrics_table = Table(metrics_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SICE_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), LIGHT_GRAY),
        ('GRID', (0, 0), (-1, -1), 1, DARK_GRAY),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 0.2*inch))
    
    # ========== AREAS COVERED ==========
    story.append(Paragraph('COVERAGE AREAS', section_style))
    areas_text = ', '.join(data.get('areas_covered', ['Sinoville', 'Montana', 'Pretoria North']))
    story.append(Paragraph(f'<b>Coverage Zones:</b> {areas_text}', normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # ========== OBSERVATIONS ==========
    story.append(Paragraph('SECURITY OBSERVATIONS', section_style))
    
    observations = [
        '✅ All perimeter gates and doors secured throughout the month',
        '✅ Alarm system armed and tested monthly — all systems functional',
        '✅ CCTV coverage active across all monitored zones',
        '✅ No unauthorized access incidents reported',
        '✅ All personnel completed mandatory security briefings',
        '✅ Emergency response procedures tested and verified',
    ]
    
    for obs in observations:
        story.append(Paragraph(obs, normal_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # ========== RECOMMENDATIONS ==========
    story.append(Paragraph('RECOMMENDATIONS', section_style))
    
    recommendations = [
        '1. Continue monthly security system audits and testing protocols',
        '2. Schedule quarterly refresher training for all personnel',
        '3. Maintain current patrol schedules and coverage rotation',
        '4. Review and update access control procedures as needed',
        '5. Document all incidents and near-misses for trend analysis',
    ]
    
    for rec in recommendations:
        story.append(Paragraph(rec, normal_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # ========== FOOTER & SIGNATURE ==========
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=DARK_GRAY,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph('_' * 60, footer_style))
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph('<b>Head of Security</b><br/>P DORFLING', footer_style))
    story.append(Spacer(1, 0.05*inch))
    story.append(Paragraph('Soft-Ice Catering Equipment Security Operations Centre (SOC)', footer_style))
    
    # Build PDF
    doc.build(story)
    print(f"✅ PDF generated: {filename}")

if __name__ == '__main__':
    # Example usage
    import sys
    from datetime import datetime
    
    if len(sys.argv) > 1:
        month = int(sys.argv[1])
        year = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().year
    else:
        now = datetime.now()
        month = now.month
        year = now.year
    
    filename = f'/mnt/user-data/outputs/SICE_Monthly_Report_{year}_{month:02d}.pdf'
    
    # Sample data (replace with actual data from your SOC system)
    sample_data = {
        'total_incidents': 0,
        'security_alerts': 5,
        'gate_checks': 156,
        'cctv_issues': 0,
        'alarm_tests': 4,
        'patrol_hours': 480,
        'personnel_trained': 8,
        'areas_covered': ['Sinoville', 'Montana', 'Pretoria North'],
        'summary': 'Soft-Ice Catering Equipment premises maintained optimal security posture throughout July 2026. All perimeter controls activated, CCTV systems operational, and alarm systems tested and verified. Zero critical security incidents reported. Personnel rotation maintained across three operational zones with 480 combined patrol hours. All staff completed mandatory security briefings. Recommend continued adherence to current security protocols.'
    }
    
    create_monthly_report(filename, month, year, sample_data)
