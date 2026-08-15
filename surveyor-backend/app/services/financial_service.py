"""Financial analytics service."""

from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.models import Invoice, Quote, Client, Project, Organization


class FinancialService:
    """Service for financial analytics and reporting."""

    def __init__(self, db: Session):
        self.db = db

    def get_financial_summary(self, org_id: str) -> dict:
        """Get overall financial summary."""
        invoices = self.db.query(Invoice).filter(
            Invoice.organization_id == org_id
        ).all()

        total_issued = sum(
            inv.total for inv in invoices
            if inv.status in ['sent', 'paid', 'pending', 'overdue']
        )
        total_paid = sum(
            inv.total for inv in invoices
            if inv.status == 'paid'
        )
        total_pending = sum(
            inv.total for inv in invoices
            if inv.status in ['pending', 'overdue']
        )
        total_overdue = sum(
            inv.total for inv in invoices
            if inv.status == 'overdue'
        )

        collection_rate = 0
        if total_issued > 0:
            collection_rate = (total_paid / total_issued) * 100

        return {
            "total_issued": float(total_issued),
            "total_paid": float(total_paid),
            "total_pending": float(total_pending),
            "total_overdue": float(total_overdue),
            "collection_rate": round(collection_rate, 2),
            "average_invoice_value": float(total_issued / len([i for i in invoices if i.status in ['sent', 'paid', 'pending', 'overdue']])) if invoices else 0,
            "total_invoices": len(invoices),
        }

    def get_revenue_by_month(self, org_id: str, months: int = 12) -> list[dict]:
        """Get revenue data grouped by month."""
        invoices = self.db.query(Invoice).filter(
            Invoice.organization_id == org_id,
            Invoice.status.in_(['paid', 'pending', 'overdue'])
        ).all()

        monthly_data = {}
        for i in range(months):
            date = datetime.now() - timedelta(days=30*i)
            month_key = date.strftime("%Y-%m")
            monthly_data[month_key] = {
                "month": date.strftime("%b"),
                "revenue": Decimal(0),
                "count": 0
            }

        for invoice in invoices:
            if invoice.issue_date:
                month_key = invoice.issue_date.strftime("%Y-%m")
                if month_key in monthly_data:
                    monthly_data[month_key]["revenue"] += invoice.total or Decimal(0)
                    monthly_data[month_key]["count"] += 1

        result = []
        for key in sorted(monthly_data.keys(), reverse=True):
            data = monthly_data[key]
            result.append({
                "month": data["month"],
                "revenue": float(data["revenue"]),
                "count": data["count"]
            })

        return result[:months]

    def get_payment_status_distribution(self, org_id: str) -> dict:
        """Get distribution of invoices by payment status."""
        invoices = self.db.query(Invoice).filter(
            Invoice.organization_id == org_id
        ).all()

        distribution = {
            "draft": 0,
            "sent": 0,
            "paid": 0,
            "pending": 0,
            "overdue": 0
        }

        for invoice in invoices:
            if invoice.status in distribution:
                distribution[invoice.status] += 1

        total = sum(distribution.values())
        return {
            "distribution": distribution,
            "total": total,
            "percentages": {
                k: round((v / total * 100), 2) if total > 0 else 0
                for k, v in distribution.items()
            }
        }

    def get_top_clients_by_revenue(self, org_id: str, limit: int = 10) -> list[dict]:
        """Get top clients by revenue."""
        query = self.db.query(
            Client.id,
            Client.name,
            func.sum(Invoice.total).label('total_revenue'),
            func.count(Invoice.id).label('invoice_count')
        ).join(Invoice, Invoice.client_id == Client.id).filter(
            Client.organization_id == org_id,
            Invoice.organization_id == org_id,
            Invoice.status.in_(['sent', 'paid', 'pending', 'overdue'])
        ).group_by(Client.id, Client.name).order_by(
            func.sum(Invoice.total).desc()
        ).limit(limit)

        return [
            {
                "client_id": row[0],
                "client_name": row[1],
                "total_revenue": float(row[2]) if row[2] else 0,
                "invoice_count": row[3]
            }
            for row in query.all()
        ]

    def get_quote_conversion(self, org_id: str) -> dict:
        """Get quote to invoice conversion metrics."""
        quotes = self.db.query(Quote).filter(
            Quote.organization_id == org_id
        ).all()

        sent_quotes = sum(1 for q in quotes if q.status == 'sent')
        accepted_quotes = sum(1 for q in quotes if q.status == 'accepted')
        invoices = self.db.query(Invoice).filter(
            Invoice.organization_id == org_id
        ).count()

        conversion_rate = 0
        if sent_quotes > 0:
            conversion_rate = (accepted_quotes / sent_quotes) * 100

        return {
            "total_quotes": len(quotes),
            "sent_quotes": sent_quotes,
            "accepted_quotes": accepted_quotes,
            "rejected_quotes": sum(1 for q in quotes if q.status == 'rejected'),
            "conversion_rate": round(conversion_rate, 2),
            "quote_to_invoice_ratio": round(invoices / len(quotes), 2) if quotes else 0
        }

    def get_project_profitability(self, org_id: str) -> list[dict]:
        """Get profitability analysis by project."""
        query = self.db.query(
            Project.id,
            Project.name,
            Project.budget,
            func.sum(Invoice.total).label('revenue')
        ).outerjoin(Invoice, Invoice.project_id == Project.id).filter(
            Project.organization_id == org_id
        ).group_by(Project.id, Project.name, Project.budget)

        result = []
        for row in query.all():
            budget = row[3] if row[3] else Decimal(0)
            revenue = row[2] if row[2] else Decimal(0)
            profit = revenue - budget if revenue and budget else Decimal(0)
            margin = 0
            if revenue and revenue > 0:
                margin = (profit / revenue) * 100

            result.append({
                "project_id": row[0],
                "project_name": row[1],
                "budget": float(row[2]) if row[2] else 0,
                "revenue": float(revenue),
                "profit": float(profit),
                "margin": round(margin, 2)
            })

        return sorted(result, key=lambda x: x['revenue'], reverse=True)

    def get_collection_forecast(self, org_id: str, days: int = 30) -> dict:
        """Get forecast of expected collections in next N days."""
        today = datetime.now()
        future_date = today + timedelta(days=days)

        pending_invoices = self.db.query(Invoice).filter(
            Invoice.organization_id == org_id,
            Invoice.status.in_(['pending', 'overdue']),
            Invoice.due_date >= today,
            Invoice.due_date <= future_date
        ).all()

        expected_collection = sum(inv.total for inv in pending_invoices if inv.total)

        overdue_invoices = self.db.query(Invoice).filter(
            Invoice.organization_id == org_id,
            Invoice.status == 'overdue',
            Invoice.due_date < today
        ).all()

        overdue_amount = sum(inv.total for inv in overdue_invoices if inv.total)

        return {
            "forecast_days": days,
            "expected_collection": float(expected_collection),
            "overdue_amount": float(overdue_amount),
            "pending_invoices_count": len(pending_invoices),
            "overdue_invoices_count": len(overdue_invoices),
            "total_at_risk": float(expected_collection + overdue_amount)
        }
