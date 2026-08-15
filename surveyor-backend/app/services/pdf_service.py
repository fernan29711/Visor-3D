"""PDF generation service for quotes and invoices."""

from io import BytesIO
from decimal import Decimal
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


class PDFService:
    """Service for generating PDF documents."""

    @staticmethod
    def generate_quote_pdf(quote_data: dict) -> BytesIO:
        """Generate PDF for a quote."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()

        # Header
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=6,
            alignment=TA_CENTER
        )
        elements.append(Paragraph("COTIZACIÓN", header_style))
        elements.append(Spacer(1, 0.2*inch))

        # Quote info
        info_style = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=3
        )
        elements.append(Paragraph(f"<b>Código:</b> {quote_data.get('code', 'N/A')}", info_style))
        elements.append(Paragraph(f"<b>Cliente:</b> {quote_data.get('client_name', 'N/A')}", info_style))
        elements.append(Paragraph(f"<b>Email:</b> {quote_data.get('client_email', 'N/A')}", info_style))
        elements.append(Paragraph(f"<b>Fecha:</b> {quote_data.get('created_at', 'N/A')}", info_style))
        elements.append(Paragraph(f"<b>Estado:</b> {quote_data.get('status', 'N/A').upper()}", info_style))
        elements.append(Paragraph(f"<b>Válida hasta:</b> {quote_data.get('valid_until', 'N/A')}", info_style))
        elements.append(Spacer(1, 0.2*inch))

        # Line items table
        table_data = [['Descripción', 'Cantidad', 'Precio Unit.', 'Subtotal']]
        for item in quote_data.get('line_items', []):
            table_data.append([
                item.get('description', ''),
                str(item.get('quantity', 0)),
                f"RD$ {Decimal(str(item.get('unit_price', 0))):.2f}",
                f"RD$ {Decimal(str(item.get('subtotal', 0))):.2f}"
            ])

        table = Table(table_data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))

        # Totals
        totals_data = [
            ['Subtotal', f"RD$ {Decimal(str(quote_data.get('subtotal', 0))):.2f}"],
            ['Descuento', f"RD$ {Decimal(str(quote_data.get('discount', 0))):.2f}"],
            ['Impuesto (18%)', f"RD$ {Decimal(str(quote_data.get('tax', 0))):.2f}"],
            ['TOTAL', f"RD$ {Decimal(str(quote_data.get('total', 0))):.2f}"],
        ]
        totals_table = Table(totals_data, colWidths=[4.5*inch, 1.2*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 3), (-1, 3), 12),
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 3), (-1, 3), colors.whitesmoke),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
        ]))
        elements.append(totals_table)

        if quote_data.get('notes'):
            elements.append(Spacer(1, 0.2*inch))
            notes_style = ParagraphStyle(
                'Notes',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.grey
            )
            elements.append(Paragraph(f"<b>Notas:</b> {quote_data.get('notes', '')}", notes_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_invoice_pdf(invoice_data: dict) -> BytesIO:
        """Generate PDF for an invoice."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()

        # Header
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=6,
            alignment=TA_CENTER
        )
        elements.append(Paragraph("FACTURA", header_style))
        elements.append(Spacer(1, 0.2*inch))

        # Invoice info
        info_style = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=3
        )
        ncf = invoice_data.get('ncf', 'SIN NCF')
        elements.append(Paragraph(f"<b>NCF:</b> {ncf}", info_style))
        elements.append(Paragraph(f"<b>Cliente:</b> {invoice_data.get('client_name', 'N/A')}", info_style))
        elements.append(Paragraph(f"<b>Email:</b> {invoice_data.get('client_email', 'N/A')}", info_style))

        if invoice_data.get('project_name'):
            elements.append(Paragraph(f"<b>Proyecto:</b> {invoice_data.get('project_name')}", info_style))

        elements.append(Paragraph(f"<b>Fecha Emisión:</b> {invoice_data.get('issue_date', 'N/A')}", info_style))
        elements.append(Paragraph(f"<b>Fecha Vencimiento:</b> {invoice_data.get('due_date', 'N/A')}", info_style))
        elements.append(Paragraph(f"<b>Estado:</b> {invoice_data.get('status', 'N/A').upper()}", info_style))
        elements.append(Spacer(1, 0.2*inch))

        # Invoice details table (simplified for direct invoice model)
        table_data = [['Descripción', 'Monto']]
        table_data.append(['Servicio de Levantamiento Topográfico', f"RD$ {Decimal(str(invoice_data.get('subtotal', invoice_data.get('total', 0)))):.2f}"])

        table = Table(table_data, colWidths=[4.5*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))

        # Totals
        totals_data = [
            ['Subtotal', f"RD$ {Decimal(str(invoice_data.get('subtotal', invoice_data.get('total', 0)))):.2f}"],
            ['Impuesto (ISR)', f"RD$ {Decimal(str(invoice_data.get('tax', 0))):.2f}"],
            ['TOTAL', f"RD$ {Decimal(str(invoice_data.get('total', 0))):.2f}"],
        ]
        totals_table = Table(totals_data, colWidths=[4.5*inch, 1.2*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 2), (-1, 2), 12),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 2), (-1, 2), colors.whitesmoke),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
        ]))
        elements.append(totals_table)
        elements.append(Spacer(1, 0.2*inch))

        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        elements.append(Paragraph("Gracias por su negocio", footer_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer
