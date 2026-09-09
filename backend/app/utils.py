from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas
import datetime

class BorderCanvas(pdfcanvas.Canvas):
    def showPage(self):
        self._draw_border()
        super().showPage()

    def save(self):
        super().save()

    def _draw_border(self):
        self.setStrokeColor(colors.HexColor("#1C3FAA"))
        self.setLineWidth(2)
        self.rect(15 * mm, 15 * mm, A4[0] - 30 * mm, A4[1] - 30 * mm)
        self.setLineWidth(0.5)
        self.setStrokeColor(colors.HexColor("#7B9FE8"))
        self.rect(17 * mm, 17 * mm, A4[0] - 34 * mm, A4[1] - 34 * mm)


def generate_bill_pdf(path, bill_data):
    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        leftMargin=22 * mm,
        rightMargin=22 * mm,
    )
    elements = []

    NAVY   = colors.HexColor("#1C3FAA")
    BLUE   = colors.HexColor("#3B5FCC")
    GREY   = colors.HexColor("#6B7280")
    DGREY  = colors.HexColor("#374151")
    WHITE  = colors.white
    STRIPE = colors.HexColor("#F5F7FF")

    PAGE_W = A4[0] - 44 * mm

    # ── Styles ───────────────────────────────────────────────────────────────
    brand_style = ParagraphStyle(
        name="Brand", fontSize=30, textColor=WHITE,
        fontName="Helvetica-Bold", alignment=1,
    )
    bill_title_style = ParagraphStyle(
        name="BillTitle", fontSize=13, textColor=NAVY,
        fontName="Helvetica-Bold", alignment=1, spaceBefore=8, spaceAfter=2,
    )
    label_style  = ParagraphStyle(name="Label", fontSize=9,  textColor=GREY,  fontName="Helvetica")
    value_style  = ParagraphStyle(name="Value", fontSize=10, textColor=DGREY, fontName="Helvetica-Bold")
    footer_style = ParagraphStyle(name="Footer", fontSize=9, textColor=GREY,  fontName="Helvetica", alignment=1)
    footer_bold  = ParagraphStyle(name="FooterBold", fontSize=10, textColor=NAVY, fontName="Helvetica-Bold", alignment=1)

    # ════════════════════════════════════════════════════════════════════════
    # HEADER BANNER — fixed height so text is never clipped
    # ════════════════════════════════════════════════════════════════════════
    banner = Table(
        [[Paragraph("<b>BIZmate</b>", brand_style)]],
        colWidths=[PAGE_W],
        rowHeights=[24 * mm],   # ✅ explicit height — prevents clipping
    )
    banner.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), NAVY),
        ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
        ('TOPPADDING',    (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(banner)
    elements.append(Spacer(1, 6))

    # ── TAX INVOICE ──────────────────────────────────────────────────────────
    elements.append(Paragraph("TAX INVOICE", bill_title_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=NAVY, spaceAfter=8))

    # ════════════════════════════════════════════════════════════════════════
    # BILL INFO
    # ════════════════════════════════════════════════════════════════════════
    col = PAGE_W / 2 - 4

    left_info = Table([
        [Paragraph("Bill No",  label_style), Paragraph(f"<b>{bill_data['bill_no']}</b>", value_style)],
        [Paragraph("Date",     label_style), Paragraph(f"<b>{bill_data.get('created_at', '—')}</b>", value_style)],
        [Paragraph("Payment",  label_style), Paragraph(f"<b>{bill_data.get('payment_method', '—')}</b>", value_style)],
    ], colWidths=[col * 0.38, col * 0.62])
    left_info.setStyle(TableStyle([
        ('TOPPADDING',    (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
    ]))

    right_info = Table([
        [Paragraph("Customer", label_style), Paragraph(f"<b>{bill_data.get('customer', 'Walk-in')}</b>", value_style)],
        [Paragraph("Phone",    label_style), Paragraph(f"<b>{bill_data.get('phone', '—')}</b>", value_style)],
    ], colWidths=[col * 0.38, col * 0.62])
    right_info.setStyle(TableStyle([
        ('TOPPADDING',    (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
    ]))

    info_table = Table([[left_info, right_info]], colWidths=[col, col])
    info_table.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
        ('TOPPADDING',    (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#D1D5DB"), spaceAfter=8))

    # ════════════════════════════════════════════════════════════════════════
    # ITEMS TABLE
    # ════════════════════════════════════════════════════════════════════════
    th  = ParagraphStyle(name="TH",  fontSize=9,  textColor=WHITE, fontName="Helvetica-Bold", alignment=1)
    td  = ParagraphStyle(name="TD",  fontSize=10, textColor=DGREY, fontName="Helvetica",      alignment=0)
    tdr = ParagraphStyle(name="TDR", fontSize=10, textColor=DGREY, fontName="Helvetica",      alignment=2)
    tdc = ParagraphStyle(name="TDC", fontSize=10, textColor=DGREY, fontName="Helvetica",      alignment=1)

    col_w = [PAGE_W * 0.42, PAGE_W * 0.13, PAGE_W * 0.20, PAGE_W * 0.25]

    rows = [[
        Paragraph("Product",    th),
        Paragraph("Qty",        th),
        Paragraph("Unit Price", th),
        Paragraph("Amount",     th),
    ]]

    for i, item in enumerate(bill_data["items"]):
        amount = float(item["qty"]) * float(item["price"])
        bg = STRIPE if i % 2 == 0 else WHITE
        rows.append([
            Paragraph(str(item["name"]), td),
            Paragraph(str(item["qty"]),  tdc),
            Paragraph(f"Rs. {float(item['price']):.2f}", tdr),
            Paragraph(f"Rs. {amount:.2f}", tdr),
            bg,
        ])

    style_cmds = [
        ('BACKGROUND',    (0, 0), (-1, 0),  BLUE),
        ('GRID',          (0, 0), (-1, -1), 0.4, colors.HexColor("#E5E7EB")),
        ('LINEBELOW',     (0, 0), (-1, 0),  1,   NAVY),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
    ]
    for i, row in enumerate(rows[1:], start=1):
        bg = row.pop() if len(row) == 5 else WHITE
        style_cmds.append(('BACKGROUND', (0, i), (-1, i), bg))

    items_table = Table(rows, colWidths=col_w)
    items_table.setStyle(TableStyle(style_cmds))
    elements.append(items_table)
    elements.append(Spacer(1, 8))

    # ════════════════════════════════════════════════════════════════════════
    # TOTALS
    # ════════════════════════════════════════════════════════════════════════
    sub   = float(bill_data.get('subtotal') or 0)
    tax   = float(bill_data.get('tax')      or 0)
    disc  = float(bill_data.get('discount') or 0)
    total = float(bill_data.get('total')    or 0)

    lbl = ParagraphStyle(name="SL", fontSize=10, textColor=DGREY, fontName="Helvetica",      alignment=0)
    val = ParagraphStyle(name="SV", fontSize=10, textColor=DGREY, fontName="Helvetica-Bold", alignment=2)

    totals_table = Table(
        [
            ['', '', Paragraph("Subtotal", lbl), Paragraph(f"Rs. {sub:.2f}",    val)],
            ['', '', Paragraph("Tax (5%)", lbl), Paragraph(f"Rs. {tax:.2f}",    val)],
            ['', '', Paragraph("Discount", lbl), Paragraph(f"- Rs. {disc:.2f}", val)],
        ],
        colWidths=[PAGE_W * 0.20, PAGE_W * 0.15, PAGE_W * 0.35, PAGE_W * 0.30],
    )
    totals_table.setStyle(TableStyle([
        ('TOPPADDING',    (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING',   (0, 0), (-1, -1), 4),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 4),
        ('LINEBELOW',     (2, 2), (3, 2),   0.5, colors.HexColor("#D1D5DB")),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 6))

    # ── Grand Total Banner ───────────────────────────────────────────────────
    tl = ParagraphStyle(name="TL", fontSize=12, textColor=WHITE, fontName="Helvetica-Bold", alignment=0)
    tv = ParagraphStyle(name="TV", fontSize=14, textColor=WHITE, fontName="Helvetica-Bold", alignment=2)

    total_banner = Table(
        [[Paragraph("<b>Total Amount</b>", tl), Paragraph(f"<b>Rs. {total:.2f}</b>", tv)]],
        colWidths=[PAGE_W * 0.5, PAGE_W * 0.5],
    )
    total_banner.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), NAVY),
        ('TOPPADDING',    (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING',   (0, 0), (-1, -1), 16),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 16),
    ]))
    elements.append(total_banner)
    elements.append(Spacer(1, 12))

    # ════════════════════════════════════════════════════════════════════════
    # FOOTER
    # ════════════════════════════════════════════════════════════════════════
    elements.append(KeepTogether([
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#D1D5DB"), spaceAfter=6),
        Paragraph("<b>Thank you for shopping with BIZmate!</b>", footer_bold),
        Spacer(1, 3),
        Paragraph("This is a computer-generated invoice. No signature required.", footer_style),
        Spacer(1, 3),
        Paragraph("For support: bizmate.support@email.com", footer_style),
    ]))

    doc.build(elements, canvasmaker=BorderCanvas)