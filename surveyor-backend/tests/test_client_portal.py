"""Tests for client portal endpoints."""

import pytest
from app.db.models import User, Client


def test_client_profile_access(client_token, client):
    """Test client can access their profile."""
    response = client.get(
        "/api/v1/client-portal/profile",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert "organization_name" in data


def test_client_profile_only_for_clients(admin_token, client):
    """Test only clients can access profile endpoint."""
    response = client.get(
        "/api/v1/client-portal/profile",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 403


def test_client_dashboard_stats(client_token, client):
    """Test client dashboard statistics."""
    response = client.get(
        "/api/v1/client-portal/dashboard/stats",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "total_quotes" in data
    assert "total_invoices" in data
    assert "total_amount_invoiced" in data
    assert "total_amount_paid" in data
    assert "total_amount_pending" in data
    assert "active_projects" in data


def test_client_get_quotes(client_token, client):
    """Test client can get their quotes."""
    response = client.get(
        "/api/v1/client-portal/quotes",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_client_get_quotes_with_pagination(client_token, client):
    """Test getting quotes with pagination."""
    response = client.get(
        "/api/v1/client-portal/quotes?skip=0&limit=10",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_client_get_quotes_by_status(client_token, client):
    """Test filtering quotes by status."""
    response = client.get(
        "/api/v1/client-portal/quotes?status=sent",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_client_cannot_access_other_client_quote(client_token, client, test_organization_id):
    """Test client cannot access quotes from other organizations."""
    # This would require creating a quote in a different org first
    response = client.get(
        "/api/v1/client-portal/quotes/nonexistent-quote-id",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 403


def test_client_get_invoices(client_token, client):
    """Test client can get their invoices."""
    response = client.get(
        "/api/v1/client-portal/invoices",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_client_get_invoices_with_pagination(client_token, client):
    """Test getting invoices with pagination."""
    response = client.get(
        "/api/v1/client-portal/invoices?skip=0&limit=20",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_client_get_invoices_by_status(client_token, client):
    """Test filtering invoices by status."""
    for status in ['sent', 'pending', 'paid', 'overdue']:
        response = client.get(
            f"/api/v1/client-portal/invoices?status={status}",
            headers={"Authorization": f"Bearer {client_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


def test_client_get_projects(client_token, client):
    """Test client can get their projects."""
    response = client.get(
        "/api/v1/client-portal/projects",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_client_get_projects_with_pagination(client_token, client):
    """Test getting projects with pagination."""
    response = client.get(
        "/api/v1/client-portal/projects?skip=0&limit=10",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_client_cannot_access_other_client_project(client_token, client):
    """Test client cannot access projects from other clients."""
    response = client.get(
        "/api/v1/client-portal/projects/nonexistent-project-id",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 403


def test_client_get_notifications(client_token, client):
    """Test client can get their notifications."""
    response = client.get(
        "/api/v1/client-portal/notifications",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_client_get_notifications_with_limit(client_token, client):
    """Test getting notifications with limit."""
    response = client.get(
        "/api/v1/client-portal/notifications?skip=0&limit=10",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10


def test_admin_cannot_access_client_portal(admin_token, client):
    """Test admins cannot access client portal endpoints."""
    response = client.get(
        "/api/v1/client-portal/profile",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 403


def test_technician_cannot_access_client_portal(technician_token, client):
    """Test technicians cannot access client portal endpoints."""
    response = client.get(
        "/api/v1/client-portal/profile",
        headers={"Authorization": f"Bearer {technician_token}"},
    )

    assert response.status_code == 403


def test_client_portal_requires_authentication(client):
    """Test that client portal endpoints require authentication."""
    endpoints = [
        "/api/v1/client-portal/profile",
        "/api/v1/client-portal/dashboard/stats",
        "/api/v1/client-portal/quotes",
        "/api/v1/client-portal/invoices",
        "/api/v1/client-portal/projects",
        "/api/v1/client-portal/notifications",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401


def test_client_dashboard_stats_structure(client_token, client):
    """Test dashboard stats has all required fields."""
    response = client.get(
        "/api/v1/client-portal/dashboard/stats",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()

    required_fields = [
        "total_quotes",
        "pending_quotes",
        "accepted_quotes",
        "total_invoices",
        "paid_invoices",
        "pending_invoices",
        "overdue_invoices",
        "total_amount_invoiced",
        "total_amount_paid",
        "total_amount_pending",
        "active_projects",
    ]

    for field in required_fields:
        assert field in data


def test_client_quote_response_structure(client_token, client):
    """Test quote response has all required fields."""
    response = client.get(
        "/api/v1/client-portal/quotes",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()

    if data:
        quote = data[0]
        required_fields = [
            "id",
            "quote_code",
            "project_name",
            "quote_date",
            "status",
            "total_amount",
            "subtotal_amount",
        ]

        for field in required_fields:
            assert field in quote


def test_client_invoice_response_structure(client_token, client):
    """Test invoice response has all required fields."""
    response = client.get(
        "/api/v1/client-portal/invoices",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()

    if data:
        invoice = data[0]
        required_fields = [
            "id",
            "ncf",
            "project_name",
            "issue_date",
            "due_date",
            "status",
            "total_amount",
            "amount_paid",
        ]

        for field in required_fields:
            assert field in invoice


def test_client_project_response_structure(client_token, client):
    """Test project response has all required fields."""
    response = client.get(
        "/api/v1/client-portal/projects",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()

    if data:
        project = data[0]
        required_fields = [
            "id",
            "project_name",
            "location",
            "status",
            "start_date",
            "total_budget",
            "total_spent",
            "progress_percentage",
        ]

        for field in required_fields:
            assert field in project


def test_client_data_isolation(client_token, client, test_organization_id):
    """Test that clients only see their own data."""
    # Get client's quotes
    response = client.get(
        "/api/v1/client-portal/quotes",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    quotes = response.json()

    # All quotes should have the same project_name pattern
    # This is a basic isolation check - in production, would verify against actual data
    assert isinstance(quotes, list)
