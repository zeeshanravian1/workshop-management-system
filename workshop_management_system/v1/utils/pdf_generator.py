"""PDF Generator Module."""

from datetime import datetime  # Add this import

from num2words import num2words
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from ..estimate.model import Estimate

# Assuming these are local models in your project
from ..jobcard.model import JobCard


def generate_jobcard_pdf(
    jobcard: "JobCard",
    inventory_items: list["JobCardInventoryItem"],
    filename: str,
    tax_rate: float = 0.15,
) -> None:
    """Generate PDF for a job card.

    Args:
        jobcard: JobCard object containing job card details
        inventory_items: List of inventory items used
        filename: Output PDF filename
        tax_rate: Tax rate (default 15%)
    """
    doc = SimpleDocTemplate(filename, pagesize=A4, title="Company")
    # Tell type checker that story can contain mixed types
    story: list[Paragraph | Table | Spacer] = []
    styles = getSampleStyleSheet()

    # Custom Styles
    header_style = ParagraphStyle(
        "HeaderStyle",
        parent=styles["Normal"],
        fontSize=14,
        leading=18,
        alignment=1,  # Center alignment
        spaceAfter=12,
    )

    # Company Header
    story.append(Paragraph("Company", header_style))
    story.append(
        Paragraph(
            "Company Address Line 1<br/>Company Address Line 2",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 15))

    # Client and Vehicle Details
    client_data = [
        [
            "Client Name:",
            jobcard.vehicle.customer.name,
            "Date:",
            jobcard.service_date.strftime("%Y-%m-%d"),
        ],
        [
            "Address:",
            jobcard.vehicle.customer.address,
            "Moho:",
            jobcard.vehicle.customer.mobile_number,
        ],
        [
            "Vehicle No:",
            jobcard.vehicle.vehicle_number,
            "CHNo:",
            jobcard.vehicle.chassis_number,
        ],
        [
            "Model:",
            jobcard.vehicle.model,
            "EngNo:",
            jobcard.vehicle.engine_number,
        ],
        ["Colour:", jobcard.vehicle.color, "Mobile No:", ""],
    ]

    client_table = Table(
        client_data, colWidths=[30 * mm, 60 * mm, 20 * mm, 60 * mm]
    )
    client_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("SPAN", (1, 0), (1, 0)),  # Span Client Name
                ("SPAN", (3, 0), (3, 0)),  # Span Date
                ("SPAN", (1, 1), (1, 1)),  # Span Address
                ("SPAN", (3, 1), (3, 1)),  # Span Moho
            ]
        )
    )
    story.append(client_table)
    story.append(Spacer(1, 15))

    # Items Table Header
    items_header = [
        "S.No",
        "Description",
        "Code",
        "Qty",
        "Unit",
        "Rate",
        "Amount",
        "Disc%",
        "Taxable",
        "CGST%",
        "CGST Amt",
        "SGST%",
        "SGST Amt",
        "Net Amt",
    ]

    # Items Table Data
    items_data = []
    subtotal = 0
    for idx, item in enumerate(inventory_items, start=1):
        item_total = item.quantity_used * item.unit_price_at_time
        subtotal += item_total
        items_data.append(
            [
                str(idx),
                item.inventory.item_name,
                "",
                str(item.quantity_used),
                "NOS",
                f"{item.unit_price_at_time:.2f}",
                f"{item_total:.2f}",
                "0.00",
                f"{item_total:.2f}",
                f"{tax_rate * 100:.2f}",
                f"{item_total * tax_rate / 2:.2f}",
                f"{tax_rate * 100:.2f}",
                f"{item_total * tax_rate / 2:.2f}",
                f"{item_total * (1 + tax_rate):.2f}",
            ]
        )

    items_table = Table([items_header] + items_data, repeatRows=1)
    items_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                (
                    "ALIGN",
                    (5, 0),
                    (-1, -1),
                    "RIGHT",
                ),  # Align numeric columns to the right
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    story.append(items_table)
    story.append(Spacer(1, 10))

    # Totals Section
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount
    totals_data = [
        ["Basic Amount:", f"{subtotal:.2f}"],
        ["CGST:", f"{tax_amount / 2:.2f}"],
        ["SGST:", f"{tax_amount / 2:.2f}"],
        ["Other Charge / Disc:", "0.00"],
        ["Round Off:", "0.00"],
        ["Grand Total:", f"{total:.2f}"],
    ]

    totals_table = Table(totals_data, colWidths=[100 * mm, 50 * mm])
    totals_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("SPAN", (0, -1), (1, -1)),  # Span Grand Total row
            ]
        )
    )
    story.append(totals_table)

    # Footer
    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            f"Amount In Words: {num2words(total, to='currency', lang='en_IN').replace('INR', 'Rupees')} Only",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 15))
    story.append(
        Paragraph(
            "Remarks: ENGINE HIT<br/>RUNNING ENGINE VOICE", styles["Normal"]
        )
    )
    story.append(Paragraph("For Company", styles["Normal"]))

    # Build the PDF
    doc.build(story)


def generate_estimate_pdf(
    estimate: "Estimate",
    inventory_items: list["InventoryEstimate"],
    filename: str,
    tax_rate: float = 0.18,
) -> None:
    """Generate PDF for an estimate.

    Args:
        estimate: Estimate object containing estimate details
        inventory_items: List of inventory items used
        filename: Output PDF filename
        tax_rate: Tax rate (default 18%)
    """
    doc = SimpleDocTemplate(filename, pagesize=A4, title="Company")
    story = []
    styles = getSampleStyleSheet()

    # Custom Styles
    header_style = ParagraphStyle(
        "HeaderStyle",
        parent=styles["Normal"],
        fontSize=14,
        leading=18,
        alignment=1,  # Center alignment
        spaceAfter=12,
    )

    # Company Header
    story.append(Paragraph("Company", header_style))
    story.append(
        Paragraph(
            "Company Address Line 1<br/>Company Address Line 2",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 15))

    # Estimate Details
    estimate_data = [
        ["Estimate ID:", str(estimate.id)],
        ["Estimate Date:", estimate.estimate_date.strftime("%Y-%m-%d")],
        ["Status:", estimate.status],
        ["Description:", estimate.description or ""],
        ["Valid Until:", estimate.valid_until.strftime("%Y-%m-%d")],
    ]

    estimate_table = Table(estimate_data, colWidths=[120, 300])
    estimate_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ]
        )
    )
    story.append(estimate_table)
    story.append(Spacer(1, 20))

    # Inventory Items
    story.append(Paragraph("Items Used:", header_style))

    # Table header
    items_data = [["Item", "Quantity", "Unit Price", "Total"]]

    # Add items and calculate totals
    subtotal = 0
    for item in inventory_items:
        item_total = item.quantity_used * item.unit_price_at_time
        subtotal += item_total
        items_data.append(
            [
                item.inventory.item_name,
                str(item.quantity_used),
                f"${item.unit_price_at_time:.2f}",
                f"${item_total:.2f}",
            ]
        )

    # Calculate tax and total
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount

    # Add totals to table
    items_data.extend(
        [
            ["", "", "Subtotal:", f"${subtotal:.2f}"],
            ["", "", f"Tax ({tax_rate * 100:.0f}%):", f"${tax_amount:.2f}"],
            ["", "", "Total:", f"${total:.2f}"],
        ]
    )

    # Create and style the items table
    items_table = Table(items_data, colWidths=[200, 100, 100, 100])
    items_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -2), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, -3), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (-2, -3), (-1, -1), "RIGHT"),
                ("LINEBELOW", (0, -4), (-1, -4), 1, colors.black),
            ]
        )
    )
    story.append(items_table)

    # Add footer
    story.append(Spacer(1, 30))
    story.append(
        Paragraph(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles["Normal"],
        )
    )

    # Generate PDF
    doc.build(story)
