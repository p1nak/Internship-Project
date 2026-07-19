import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def generate_machine_report(machine, output_path):
    """Generate a comprehensive machine report PDF using ReportLab."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            topMargin=30 * mm, bottomMargin=20 * mm,
                            leftMargin=20 * mm, rightMargin=20 * mm)
    styles = getSampleStyleSheet()
    elements = []

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontSize=24, spaceAfter=6, textColor=colors.HexColor('#1a1a2e'),
        alignment=TA_CENTER
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle', parent=styles['Normal'],
        fontSize=14, spaceAfter=12, textColor=colors.HexColor('#4a4a6a'),
        alignment=TA_CENTER
    )
    section_style = ParagraphStyle(
        'SectionHeader', parent=styles['Heading2'],
        fontSize=14, spaceBefore=20, spaceAfter=10,
        textColor=colors.HexColor('#1a1a2e'), borderPadding=(0, 0, 4, 0)
    )
    normal_style = styles['Normal']

    # ---- Title Page ----
    elements.append(Spacer(1, 60))
    elements.append(Paragraph(f"{machine.machine_name}", title_style))
    elements.append(Paragraph(f"Machine ID: {machine.machine_id}", subtitle_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="80%", thickness=2, color=colors.HexColor('#1a1a2e'),
                                spaceBefore=10, spaceAfter=20, hAlign='CENTER'))
    elements.append(Paragraph("Comprehensive Machine Report", subtitle_style))
    elements.append(Spacer(1, 40))

    # ---- Machine Details Section ----
    elements.append(Paragraph("Machine Details", section_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc'),
                                spaceBefore=2, spaceAfter=10))

    details_data = [
        ["Machine ID", machine.machine_id or "N/A"],
        ["Machine Name", machine.machine_name or "N/A"],
        ["Department", machine.department or "N/A"],
        ["Manufacturer", machine.manufacturer or "N/A"],
        ["Model", machine.model or "N/A"],
        ["Serial Number", machine.serial_number or "N/A"],
        ["Capacity", machine.capacity or "N/A"],
        ["Location", machine.location or "N/A"],
        ["Installation Date", str(machine.installation_date) if machine.installation_date else "N/A"],
        ["Status", (machine.status or "N/A").replace('_', ' ').title()],
    ]

    details_table = Table(details_data, colWidths=[150, 350])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f5')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a1a2e')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(details_table)

    # ---- Maintenance History Section ----
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Maintenance History", section_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc'),
                                spaceBefore=2, spaceAfter=10))

    if machine.maintenance_records:
        maint_data = [["Date", "Engineer", "Work Done", "Type"]]
        for record in machine.maintenance_records:
            maint_data.append([
                str(record.service_date) if record.service_date else "N/A",
                record.engineer or "N/A",
                Paragraph(record.work_done or "N/A", normal_style),
                (record.work_type or "N/A").title(),
            ])
        maint_table = Table(maint_data, colWidths=[80, 100, 230, 80])
        maint_table.setStyle(_get_table_style(len(maint_data)))
        elements.append(maint_table)
    else:
        elements.append(Paragraph("No maintenance records found.", normal_style))

    # ---- Breakdown History Section ----
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Breakdown History", section_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc'),
                                spaceBefore=2, spaceAfter=10))

    if machine.breakdown_records:
        bd_data = [["Date", "Problem", "Root Cause", "Solution", "Downtime (min)"]]
        for record in machine.breakdown_records:
            bd_data.append([
                str(record.date) if record.date else "N/A",
                Paragraph(record.problem or "N/A", normal_style),
                Paragraph(record.root_cause or "N/A", normal_style),
                Paragraph(record.solution or "N/A", normal_style),
                str(record.downtime_minutes or 0),
            ])
        bd_table = Table(bd_data, colWidths=[70, 120, 110, 110, 70])
        bd_table.setStyle(_get_table_style(len(bd_data)))
        elements.append(bd_table)
    else:
        elements.append(Paragraph("No breakdown records found.", normal_style))

    # ---- Spare Parts Section ----
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Spare Parts Inventory", section_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc'),
                                spaceBefore=2, spaceAfter=10))

    if machine.spare_parts:
        sp_data = [["Part Name", "Part Number", "Qty", "Unit Cost", "Supplier"]]
        for part in machine.spare_parts:
            sp_data.append([
                part.part_name or "N/A",
                part.part_number or "N/A",
                str(part.quantity or 0),
                f"₹{part.unit_cost:,.2f}" if part.unit_cost else "N/A",
                part.supplier or "N/A",
            ])
        sp_table = Table(sp_data, colWidths=[130, 100, 50, 80, 130])
        sp_table.setStyle(_get_table_style(len(sp_data)))
        elements.append(sp_table)
    else:
        elements.append(Paragraph("No spare parts recorded.", normal_style))

    # ---- Preventive Schedule Section ----
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Preventive Maintenance Schedule", section_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc'),
                                spaceBefore=2, spaceAfter=10))

    if machine.schedules:
        sched_data = [["Task", "Frequency", "Last Completed", "Next Due", "Assigned To"]]
        for sched in machine.schedules:
            sched_data.append([
                Paragraph(sched.task_description or "N/A", normal_style),
                (sched.frequency or "N/A").title(),
                str(sched.last_completed) if sched.last_completed else "N/A",
                str(sched.next_due) if sched.next_due else "N/A",
                sched.assigned_to or "N/A",
            ])
        sched_table = Table(sched_data, colWidths=[140, 70, 90, 90, 100])
        sched_table.setStyle(_get_table_style(len(sched_data)))
        elements.append(sched_table)
    else:
        elements.append(Paragraph("No preventive schedules configured.", normal_style))

    # Build PDF
    doc.build(elements)
    return output_path


def _get_table_style(num_rows):
    """Return a professional table style for data tables."""
    style = TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('PADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
    ])
    # Alternate row colors for data rows
    for i in range(1, num_rows):
        if i % 2 == 0:
            style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8f8fc'))
    return style
