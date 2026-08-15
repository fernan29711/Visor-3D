"""Service for managing role-based access control and permissions."""

from enum import Enum
from sqlalchemy.orm import Session
from app.db.models import User, Organization


class Role(str, Enum):
    """User roles in the system."""
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    AGRIMENSOR = "agrimensor"
    TECHNICIAN = "technician"
    CLIENT = "client"


class Permission(str, Enum):
    """Permissions for various actions."""
    # Organization
    ORG_READ = "org:read"
    ORG_CREATE = "org:create"
    ORG_UPDATE = "org:update"
    ORG_DELETE = "org:delete"
    ORG_MANAGE_USERS = "org:manage_users"
    ORG_VIEW_ANALYTICS = "org:view_analytics"

    # Projects
    PROJECT_READ = "project:read"
    PROJECT_CREATE = "project:create"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"
    PROJECT_MANAGE = "project:manage"

    # Quotes
    QUOTE_READ = "quote:read"
    QUOTE_CREATE = "quote:create"
    QUOTE_UPDATE = "quote:update"
    QUOTE_DELETE = "quote:delete"
    QUOTE_SEND = "quote:send"

    # Invoices
    INVOICE_READ = "invoice:read"
    INVOICE_CREATE = "invoice:create"
    INVOICE_UPDATE = "invoice:update"
    INVOICE_DELETE = "invoice:delete"
    INVOICE_MANAGE_PAYMENT = "invoice:manage_payment"

    # Drones
    DRONE_READ = "drone:read"
    DRONE_CREATE = "drone:create"
    DRONE_UPDATE = "drone:update"
    DRONE_DELETE = "drone:delete"

    # Reports & Analytics
    REPORT_READ = "report:read"
    REPORT_EXPORT = "report:export"
    ANALYTICS_READ = "analytics:read"

    # Financial
    FINANCIAL_READ = "financial:read"
    FINANCIAL_MANAGE = "financial:manage"


class PermissionService:
    """Service for managing permissions and role-based access control."""

    # Role to permissions mapping
    ROLE_PERMISSIONS = {
        Role.SUPERADMIN: [
            # Superadmin has all permissions
            Permission.ORG_READ, Permission.ORG_CREATE, Permission.ORG_UPDATE, Permission.ORG_DELETE,
            Permission.ORG_MANAGE_USERS, Permission.ORG_VIEW_ANALYTICS,
            Permission.PROJECT_READ, Permission.PROJECT_CREATE, Permission.PROJECT_UPDATE, Permission.PROJECT_DELETE,
            Permission.PROJECT_MANAGE,
            Permission.QUOTE_READ, Permission.QUOTE_CREATE, Permission.QUOTE_UPDATE, Permission.QUOTE_DELETE,
            Permission.QUOTE_SEND,
            Permission.INVOICE_READ, Permission.INVOICE_CREATE, Permission.INVOICE_UPDATE, Permission.INVOICE_DELETE,
            Permission.INVOICE_MANAGE_PAYMENT,
            Permission.DRONE_READ, Permission.DRONE_CREATE, Permission.DRONE_UPDATE, Permission.DRONE_DELETE,
            Permission.REPORT_READ, Permission.REPORT_EXPORT,
            Permission.ANALYTICS_READ,
            Permission.FINANCIAL_READ, Permission.FINANCIAL_MANAGE,
        ],
        Role.ADMIN: [
            # Admin manages organization
            Permission.ORG_READ, Permission.ORG_UPDATE, Permission.ORG_MANAGE_USERS, Permission.ORG_VIEW_ANALYTICS,
            Permission.PROJECT_READ, Permission.PROJECT_CREATE, Permission.PROJECT_UPDATE, Permission.PROJECT_DELETE,
            Permission.PROJECT_MANAGE,
            Permission.QUOTE_READ, Permission.QUOTE_CREATE, Permission.QUOTE_UPDATE, Permission.QUOTE_DELETE,
            Permission.QUOTE_SEND,
            Permission.INVOICE_READ, Permission.INVOICE_CREATE, Permission.INVOICE_UPDATE, Permission.INVOICE_DELETE,
            Permission.INVOICE_MANAGE_PAYMENT,
            Permission.DRONE_READ, Permission.DRONE_CREATE, Permission.DRONE_UPDATE, Permission.DRONE_DELETE,
            Permission.REPORT_READ, Permission.REPORT_EXPORT,
            Permission.ANALYTICS_READ,
            Permission.FINANCIAL_READ, Permission.FINANCIAL_MANAGE,
        ],
        Role.AGRIMENSOR: [
            # Agrimensor (surveyor) performs surveys and creates projects
            Permission.ORG_READ,
            Permission.PROJECT_READ, Permission.PROJECT_CREATE, Permission.PROJECT_UPDATE,
            Permission.QUOTE_READ, Permission.QUOTE_CREATE, Permission.QUOTE_UPDATE,
            Permission.INVOICE_READ, Permission.INVOICE_UPDATE,
            Permission.DRONE_READ, Permission.DRONE_CREATE, Permission.DRONE_UPDATE,
            Permission.REPORT_READ,
            Permission.ANALYTICS_READ,
            Permission.FINANCIAL_READ,
        ],
        Role.TECHNICIAN: [
            # Technician supports drones and data processing
            Permission.ORG_READ,
            Permission.PROJECT_READ,
            Permission.QUOTE_READ,
            Permission.INVOICE_READ,
            Permission.DRONE_READ, Permission.DRONE_CREATE, Permission.DRONE_UPDATE,
            Permission.REPORT_READ,
            Permission.ANALYTICS_READ,
        ],
        Role.CLIENT: [
            # Client sees only their own data
            Permission.PROJECT_READ,
            Permission.QUOTE_READ,
            Permission.INVOICE_READ,
            Permission.REPORT_READ,
        ],
    }

    def __init__(self, db: Session):
        self.db = db

    def get_user_permissions(self, user: User) -> list[Permission]:
        """Get all permissions for a user based on their role."""
        role = Role(user.role) if isinstance(user.role, str) else user.role
        return self.ROLE_PERMISSIONS.get(role, [])

    def has_permission(self, user: User, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        permissions = self.get_user_permissions(user)
        return permission in permissions

    def has_any_permission(self, user: User, permissions: list[Permission]) -> bool:
        """Check if user has any of the specified permissions."""
        user_permissions = self.get_user_permissions(user)
        return any(perm in user_permissions for perm in permissions)

    def has_all_permissions(self, user: User, permissions: list[Permission]) -> bool:
        """Check if user has all specified permissions."""
        user_permissions = self.get_user_permissions(user)
        return all(perm in user_permissions for perm in permissions)

    def can_access_organization(self, user: User, org_id: str) -> bool:
        """Check if user can access a specific organization."""
        if str(user.organization_id) == org_id:
            return True
        # Superadmin can access any organization
        if user.role == Role.SUPERADMIN.value:
            return True
        return False

    def can_access_resource(self, user: User, resource_org_id: str) -> bool:
        """Check if user can access a resource in a specific organization."""
        return self.can_access_organization(user, resource_org_id)

    def get_accessible_organizations(self, user: User) -> list[str]:
        """Get list of organization IDs user can access."""
        if user.role == Role.SUPERADMIN.value:
            # Superadmin can access all organizations
            orgs = self.db.query(Organization).all()
            return [org.id for org in orgs]
        else:
            # Regular users can only access their own organization
            return [str(user.organization_id)]

    def can_create_quote(self, user: User) -> bool:
        """Check if user can create quotes."""
        return self.has_permission(user, Permission.QUOTE_CREATE)

    def can_manage_quote(self, user: User, quote_org_id: str) -> bool:
        """Check if user can manage a specific quote."""
        return (self.has_permission(user, Permission.QUOTE_UPDATE) and
                self.can_access_resource(user, quote_org_id))

    def can_create_invoice(self, user: User) -> bool:
        """Check if user can create invoices."""
        return self.has_permission(user, Permission.INVOICE_CREATE)

    def can_manage_invoice(self, user: User, invoice_org_id: str) -> bool:
        """Check if user can manage a specific invoice."""
        return (self.has_permission(user, Permission.INVOICE_UPDATE) and
                self.can_access_resource(user, invoice_org_id))

    def can_create_project(self, user: User) -> bool:
        """Check if user can create projects."""
        return self.has_permission(user, Permission.PROJECT_CREATE)

    def can_manage_project(self, user: User, project_org_id: str) -> bool:
        """Check if user can manage a specific project."""
        return (self.has_permission(user, Permission.PROJECT_UPDATE) and
                self.can_access_resource(user, project_org_id))

    def can_create_drone_flight(self, user: User) -> bool:
        """Check if user can create drone flights."""
        return self.has_permission(user, Permission.DRONE_CREATE)

    def can_view_analytics(self, user: User) -> bool:
        """Check if user can view analytics."""
        return self.has_permission(user, Permission.ANALYTICS_READ)

    def can_export_reports(self, user: User) -> bool:
        """Check if user can export reports."""
        return self.has_permission(user, Permission.REPORT_EXPORT)

    def can_manage_organization(self, user: User) -> bool:
        """Check if user can manage organization settings."""
        return self.has_permission(user, Permission.ORG_UPDATE)

    def can_manage_users(self, user: User) -> bool:
        """Check if user can manage other users."""
        return self.has_permission(user, Permission.ORG_MANAGE_USERS)

    def get_user_role_display_name(self, role: str) -> str:
        """Get display name for a role."""
        role_names = {
            Role.SUPERADMIN.value: "Super Administrador",
            Role.ADMIN.value: "Administrador",
            Role.AGRIMENSOR.value: "Agrimensor",
            Role.TECHNICIAN.value: "Técnico",
            Role.CLIENT.value: "Cliente",
        }
        return role_names.get(role, "Desconocido")
