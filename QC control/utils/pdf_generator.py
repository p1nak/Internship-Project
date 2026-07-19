"""
PDF Report Generator for Digital QC System.
Generates professional quality control inspection reports using ReportLab.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, Image as RLImage, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os
from datetime import datetime
from config import Config


# ── Color Palette ──────────────────────────────────────────────────────────────
PRIMARY_DARK = HexColor('#2b2b2b')
RUST = HexColor('#a44e3b')
GREEN = HexColor('#10b981')
RED = HexColor('#ef4444')
AMBER = HexColor('#f59e0b')
LIGHT_GRAY = HexColor('#f8fafc')
WHITE = HexColor('#ffffff')
MEDIUM_GRAY = HexColor('#e2e8f0')
TEXT_GRAY = HexColor('#64748b')


def _get_styles():
    """Build custom paragraph styles for the report."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='CompanyName',
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=PRIMARY_DARK,
        alignment=TA_CENTER,
        spaceAfter=2 * mm,
    ))

    styles.add(ParagraphStyle(
        name='ReportTitle',
        fontName='Helvetica',
        fontSize=12,
        textColor=RUST,
        alignment=TA_CENTER,
        spaceAfter=4 * mm,
    ))

    styles.add(ParagraphStyle(
        name='ReportMeta',
        fontName='Helvetica',
        fontSize=9,
        textColor=TEXT_GRAY,
        alignment=TA_RIGHT,
        spaceAfter=2 * mm,
    ))

    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=PRIMARY_DARK,
        spaceBefore=6 * mm,
        spaceAfter=3 * mm,
    ))

    styles.add(ParagraphStyle(
        name='BodyText_Custom',
        fontName='Helvetica',
        fontSize=9,
        textColor=PRIMARY_DARK,
        spaceAfter=2 * mm,
        leading=13,
    ))

    styles.add(ParagraphStyle(
        name='ResultPass',
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=GREEN,
        alignment=TA_CENTER,
        spaceBefore=8 * mm,
        spaceAfter=8 * mm,
    ))

    styles.add(ParagraphStyle(
        name='ResultFail',
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=RED,
        alignment=TA_CENTER,
        spaceBefore=8 * mm,
        spaceAfter=8 * mm,
    ))

    styles.add(ParagraphStyle(
        name='ResultPending',
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=AMBER,
        alignment=TA_CENTER,
        spaceBefore=8 * mm,
        spaceAfter=8 * mm,
    ))

    styles.add(ParagraphStyle(
        name='FooterNote',
        fontName='Helvetica',
        fontSize=7,
        textColor=TEXT_GRAY,
        alignment=TA_CENTER,
        spaceBefore=10 * mm,
    ))

    styles.add(ParagraphStyle(
        name='CellText',
        fontName='Helvetica',
        fontSize=9,
        textColor=PRIMARY_DARK,
        leading=12,
    ))

    styles.add(ParagraphStyle(
        name='CellHeader',
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=WHITE,
        leading=12,
    ))

    return styles


def _build_detail_table(data_rows, col_widths):
    """Build a styled two-column or multi-column table with alternating rows."""
    table = Table(data_rows, colWidths=col_widths)

    style_commands = [
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), RUST),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),

        # Body rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),

        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, MEDIUM_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]

    # Alternating row colors
    for i in range(1, len(data_rows)):
        bg = LIGHT_GRAY if i % 2 == 0 else WHITE
        style_commands.append(('BACKGROUND', (0, i), (-1, i), bg))

    table.setStyle(TableStyle(style_commands))
    return table


def generate_pdf(inspection_data, output_path):
    """
    Generate a professional PDF quality control report.

    Args:
        inspection_data (dict): Dictionary with keys:
            - inspection (dict): Inspection record fields
            - checklist (list): List of checklist item dicts
            - images (list): List of image filename strings
        output_path (str): Full file path for the output PDF
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm
    )

    styles = _get_styles()
    story = []
    inspection = inspection_data['inspection']
    checklist = inspection_data.get('checklist', [])
    images = inspection_data.get('images', [])

    # ── 1. Header ──────────────────────────────────────────────────────────────
    story.append(Paragraph('RHINO MACHINES PVT. LTD.', styles['CompanyName']))
    story.append(Paragraph('Digital Quality Control Report', styles['ReportTitle']))
    story.append(HRFlowable(
        width='100%',
        thickness=1,
        color=RUST,
        spaceAfter=4 * mm,
        spaceBefore=2 * mm
    ))

    # ── 2. Report Meta ─────────────────────────────────────────────────────────
    report_id = inspection.get('id', 'N/A')
    report_date = inspection.get('inspection_date', datetime.now().strftime('%Y-%m-%d'))
    inspector_name = inspection.get('inspector_name', inspection.get('inspector', 'N/A'))

    meta_text = (
        f'Report # {report_id} &nbsp;&nbsp;|&nbsp;&nbsp; '
        f'Date: {report_date} &nbsp;&nbsp;|&nbsp;&nbsp; '
        f'Inspector: {inspector_name}'
    )
    story.append(Paragraph(meta_text, styles['ReportMeta']))
    story.append(Spacer(1, 4 * mm))

    # ── 3. Panel Details ───────────────────────────────────────────────────────
    story.append(Paragraph('PANEL DETAILS', styles['SectionHeader']))

    page_width = A4[0] - 40 * mm  # Account for margins
    label_width = page_width * 0.35
    value_width = page_width * 0.65

    panel_data = [
        [Paragraph('Parameter', styles['CellHeader']),
         Paragraph('Value', styles['CellHeader'])],
        ['Panel ID', inspection.get('panel_code', 'N/A')],
        ['Panel Name', inspection.get('panel_name', 'N/A')],
        ['Customer', inspection.get('customer_name', inspection.get('customer', 'N/A'))],
        ['Project', inspection.get('project_name', inspection.get('project', 'N/A'))],
        ['Panel Type', inspection.get('panel_type', 'N/A')],
        ['Drawing No', inspection.get('drawing_no', 'N/A')],
        ['Serial No', inspection.get('serial_no', 'N/A')],
        ['Inspection Date', report_date],
    ]

    story.append(_build_detail_table(panel_data, [label_width, value_width]))
    story.append(Spacer(1, 6 * mm))

    # ── 4. QC Checklist ────────────────────────────────────────────────────────
    if checklist:
        story.append(Paragraph('QC CHECKLIST', styles['SectionHeader']))

        num_width = page_width * 0.08
        item_width = page_width * 0.62
        result_width = page_width * 0.30

        checklist_data = [
            [Paragraph('#', styles['CellHeader']),
             Paragraph('Item', styles['CellHeader']),
             Paragraph('Result', styles['CellHeader'])]
        ]

        for idx, item in enumerate(checklist, 1):
            item_name = item.get('item_name', item.get('name', ''))
            result = item.get('result', item.get('status', 'pending')).lower()

            if result == 'pass':
                result_text = Paragraph(
                    '<font color="#10b981"><b>✓ PASS</b></font>',
                    styles['CellText']
                )
            elif result == 'fail':
                result_text = Paragraph(
                    '<font color="#ef4444"><b>✗ FAIL</b></font>',
                    styles['CellText']
                )
            else:
                result_text = Paragraph(
                    '<font color="#f59e0b"><b>— PENDING</b></font>',
                    styles['CellText']
                )

            checklist_data.append([str(idx), item_name, result_text])

        story.append(_build_detail_table(
            checklist_data,
            [num_width, item_width, result_width]
        ))
        story.append(Spacer(1, 4 * mm))

    # ── 5. Remarks ─────────────────────────────────────────────────────────────
    story.append(Paragraph('REMARKS', styles['SectionHeader']))
    remarks = inspection.get('remarks', '').strip()
    if remarks:
        story.append(Paragraph(remarks, styles['BodyText_Custom']))
    else:
        story.append(Paragraph(
            '<i>No remarks provided.</i>',
            styles['BodyText_Custom']
        ))

    # ── 6. Defect Photos ───────────────────────────────────────────────────────
    if images:
        story.append(Paragraph('DEFECT PHOTOS', styles['SectionHeader']))

        for img_filename in images:
            # Support both dict and string image entries
            if isinstance(img_filename, dict):
                img_path = os.path.join(
                    Config.UPLOAD_FOLDER,
                    img_filename.get('filename', img_filename.get('image_path', ''))
                )
                caption = img_filename.get('caption', img_filename.get('description', ''))
            else:
                img_path = os.path.join(Config.UPLOAD_FOLDER, img_filename)
                caption = ''

            if os.path.exists(img_path):
                try:
                    max_width = 150 * mm
                    img = RLImage(img_path)

                    # Maintain aspect ratio
                    aspect = img.imageHeight / img.imageWidth
                    if img.imageWidth > max_width:
                        img.drawWidth = max_width
                        img.drawHeight = max_width * aspect
                    else:
                        img.drawWidth = img.imageWidth
                        img.drawHeight = img.imageHeight

                    # Cap height at 100mm
                    max_height = 100 * mm
                    if img.drawHeight > max_height:
                        img.drawHeight = max_height
                        img.drawWidth = max_height / aspect

                    story.append(img)
                    if caption:
                        story.append(Paragraph(
                            f'<i>{caption}</i>',
                            styles['BodyText_Custom']
                        ))
                    story.append(Spacer(1, 3 * mm))
                except Exception:
                    # Skip images that can't be loaded
                    pass

    # ── 7. Overall Result ──────────────────────────────────────────────────────
    overall_status = inspection.get('overall_result',
                                    inspection.get('status', 'pending')).lower()

    if overall_status == 'pass':
        story.append(Paragraph('OVERALL RESULT: PASSED', styles['ResultPass']))
    elif overall_status == 'fail':
        story.append(Paragraph('OVERALL RESULT: FAILED', styles['ResultFail']))
    else:
        story.append(Paragraph('OVERALL RESULT: PENDING', styles['ResultPending']))

    # ── 8. Signature Lines ─────────────────────────────────────────────────────
    story.append(Spacer(1, 10 * mm))

    sig_style = ParagraphStyle(
        name='SignatureLabel',
        fontName='Helvetica',
        fontSize=9,
        textColor=PRIMARY_DARK,
        alignment=TA_CENTER,
    )

    sig_line_style = ParagraphStyle(
        name='SignatureLine',
        fontName='Helvetica',
        fontSize=9,
        textColor=MEDIUM_GRAY,
        alignment=TA_CENTER,
        spaceAfter=2 * mm,
    )

    sig_data = [
        [
            Paragraph('_' * 35, sig_line_style),
            Paragraph('', sig_line_style),
            Paragraph('_' * 35, sig_line_style),
        ],
        [
            Paragraph('QC Inspector', sig_style),
            Paragraph('', sig_style),
            Paragraph('QC Manager', sig_style),
        ]
    ]

    sig_table = Table(sig_data, colWidths=[page_width * 0.4, page_width * 0.2, page_width * 0.4])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(sig_table)

    # ── 9. Footer ──────────────────────────────────────────────────────────────
    footer_text = (
        f'Generated by Digital QC System — Rhino Machines Pvt. Ltd. | '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    )
    story.append(Paragraph(footer_text, styles['FooterNote']))

    # ── Build PDF ──────────────────────────────────────────────────────────────
    doc.build(story)
    return output_path
