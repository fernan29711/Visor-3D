"""Role-Based Access Control (RBAC) utilities."""

from enum import Enum
from typing import List
from app.db.models import UserRole

class Permission(str, Enum):
    """Application permissions."""
    # Organization permissions
    MANAGE_ORGANIZATION = "manage_organization"
    VIEW_ORGANIZATION = "view_organization"

    # User permissions
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"

    # Client permissions
    MANAGE_CLIENTS = "manage_clients"
    VIEW_CLIENTS = "view_clients"

    # Project permissions
    MANAGE_PROJECTS = "manage_projects"
    VIEW_PROJECTS = "view_projects"
    DELETE_PROJECTS = "delete_projects"

    # Survey permissions
    MANAGE_SURVEY_POINTS = "manage_survey_points"
    VIEW_SURVEY_POINTS = "view_survey_points"
    IMPORT_SURVEY_DATA = "import_survey_data"
    EXPORT_SURVEY_DATA = "export_survey_data"

    # Equipment permissions
    MANAGE_EQUIPMENT = "manage_equipment"
    VIEW_EQUIPMENT = "view_equipment"

    # Quote/Invoice permissions
    MANAGE_QUOTES = "manage_quotes"
    VIEW_QUOTES = "view_quotes"
    MANAGE_INVOICES = "manage_invoices"
    VIEW_INVOICES = "view_invoices"

    # Report permissions
    GENERATE_REPORTS = "generate_reports"
    VIEW_REPORTS = "view_reports"

    # Admin permissions
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_ROLES = "manage_roles"

# Role-to-permissions mapping
ROLE_PERMISSIONS = {
    UserRole.SUPERADMIN: [
        Permission.MANAGE_ORGANIZATION,
        Permission.MANAGE_USERS,
        Permission.MANAGE_CLIENTS,
        Permission.MANAGE_PROJECTS,
        Permission.MANAGE_SURVEY_POINTS,
        Permission.MANAGE_EQUIPMENT,
        Permission.MANAGE_QUOTES,
        Permission.MANAGE_INVOICES,
        Permission.GENERATE_REPORTS,
        Permission.VIEW_AUDIT_LOGS,
        Permission.MANAGE_ROLES,
        # All permissions
    ] + [p for p in Permission],

    UserRole.ADMIN: [
        Permission.MANAGE_ORGANIZATION,
        Permission.MANAGE_USERS,
        Permission.MANAGE_CLIENTS,
        Permission.MANAGE_PROJECTS,
        Permission.MANAGE_SURVEY_POINTS,
        Permission.MANAGE_EQUIPMENT,
        Permission.MANAGE_QUOTES,
        Permission.MANAGE_INVOICES,
        Permission.GENERATE_REPORTS,
        Permission.VIEW_AUDIT_LOGS,
    ],

    UserRole.AGRIMENSOR: [
        Permission.VIEW_ORGANIZATION,
        Permission.VIEW_USERS,
        Permission.VIEW_CLIENTS,
        Permission.MANAGE_PROJECTS,
        Permission.VIEW_PROJECTS,
        Permission.MANAGE_SURVEY_POINTS,
        Permission.VIEW_SURVEY_POINTS,
        Permission.IMPORT_SURVEY_DATA,
        Permission.EXPORT_SURVEY_DATA,
        Permission.VIEW_EQUIPMENT,
        Permission.VIEW_QUOTES,
        Permission.VIEW_INVOICES,
        Permission.GENERATE_REPORTS,
        Permission.VIEW_REPORTS,
    ],

    UserRole.TECHNICIAN: [
        Permission.VIEW_PROJECTS,
        Permission.MANAGE_SURVEY_POINTS,
        Permission.VIEW_SURVEY_POINTS,
        Permission.IMPORT_SURVEY_DATA,
        Permission.EXPORT_SURVEY_DATA,
        Permission.VIEW_EQUIPMENT,
    ],

    UserRole.CLIENT: [
        Permission.VIEW_PROJECTS,
        Permission.VIEW_SURVEY_POINTS,
        Permission.VIEW_REPORTS,
        Permission.VIEW_QUOTES,
        Permission.VIEW_INVOICES,
    ],
}

def get_permissions_for_role(role: UserRole) -> List[Permission]:
    """Get list of permissions for a role."""
    return ROLE_PERMISSIONS.get(role, [])

def has_permission(role: UserRole, permission: Permission) -> bool:
    """Check if a role has a specific permission."""
    permissions = get_permissions_for_role(role)
    return permission in permissions

def has_any_permission(role: UserRole, permissions: List[Permission]) -> bool:
    """Check if a role has any of the given permissions."""
    role_perms = get_permissions_for_role(role)
    return any(p in role_perms for p in permissions)

def has_all_permissions(role: UserRole, permissions: List[Permission]) -> bool:
    """Check if a role has all the given permissions."""
    role_perms = get_permissions_for_role(role)
    return all(p in role_perms for p in permissions)
