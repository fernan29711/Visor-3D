"""SQLAlchemy Models for Database"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Enum, Text, DECIMAL, JSONB, BigInteger
from sqlalchemy.dialects.postgresql import UUID, GEOMETRY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
import uuid
from enum import Enum as PyEnum
from datetime import datetime
from app.db.database import Base

# Enums
class UserRole(str, PyEnum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    AGRIMENSOR = "agrimensor"
    TECHNICIAN = "technician"
    CLIENT = "client"

class ProjectStatus(str, PyEnum):
    PENDING = "pending"
    PLANNED = "planned"
    IN_FIELD = "in_field"
    PROCESSING = "processing"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    DELIVERED = "delivered"
    ARCHIVED = "archived"

class ClientType(str, PyEnum):
    PERSON = "person"
    COMPANY = "company"

class EquipmentType(str, PyEnum):
    GNSS = "gnss"
    TOTAL_STATION = "total_station"
    LEVEL = "level"
    DRONE = "drone"
    CAMERA = "camera"

class EquipmentStatus(str, PyEnum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"

class QuoteStatus(str, PyEnum):
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"

class DocumentType(str, PyEnum):
    FIELD = "field"
    GNSS = "gnss"
    TOTAL_STATION = "total_station"
    PHOTOS = "photos"
    PHOTOGRAMMETRY = "photogrammetry"
    CAD = "cad"
    REPORTS = "reports"
    DELIVERABLES = "deliverables"

# Models
class Organization(Base):
    """Organization/Company entity."""
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    rnc = Column(String(20), nullable=True)
    logo_url = Column(Text, nullable=True)
    subscription_plan = Column(String(50), default="free")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    clients = relationship("Client", back_populates="organization", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="organization", cascade="all, delete-orphan")
    equipment = relationship("Equipment", back_populates="organization", cascade="all, delete-orphan")
    quotes = relationship("Quote", back_populates="organization", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="organization", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Organization {self.name}>"

class User(Base):
    """User entity."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.AGRIMENSOR)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization", back_populates="users")
    survey_points = relationship("SurveyPoint", back_populates="created_by")
    documents = relationship("Document", back_populates="created_by")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"

class Client(Base):
    """Client/Customer entity."""
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    client_type = Column(Enum(ClientType), default=ClientType.PERSON)
    cedula_rnc = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    municipality = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization", back_populates="clients")
    projects = relationship("Project", back_populates="client", cascade="all, delete-orphan")
    quotes = relationship("Quote", back_populates="client", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client {self.name}>"

class Project(Base):
    """Project entity."""
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    code = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PENDING, index=True)
    location = Column(Geometry("POINT", srid=4326), nullable=True)
    municipality = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)
    budget = Column(DECIMAL(15, 2), nullable=True)
    spent = Column(DECIMAL(15, 2), default=0)
    responsible_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    project_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization", back_populates="projects")
    client = relationship("Client", back_populates="projects")
    responsible_user = relationship("User")
    survey_points = relationship("SurveyPoint", back_populates="project", cascade="all, delete-orphan")
    geometries = relationship("Geometry", back_populates="project", cascade="all, delete-orphan")
    surfaces = relationship("Surface", back_populates="project", cascade="all, delete-orphan")
    parcels = relationship("Parcel", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="project")

    def __repr__(self):
        return f"<Project {self.code}>"

class SurveyPoint(Base):
    """Survey/Topographic point entity."""
    __tablename__ = "survey_points"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    point_number = Column(String(50), nullable=False)
    east = Column(DECIMAL(15, 8), nullable=False)
    north = Column(DECIMAL(15, 8), nullable=False)
    elevation = Column(DECIMAL(10, 3), nullable=True)
    code = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    geometry = Column(Geometry("POINT", srid=4326), nullable=True)
    precision_horizontal = Column(DECIMAL(6, 3), nullable=True)
    precision_vertical = Column(DECIMAL(6, 3), nullable=True)
    gnss_status = Column(String(50), nullable=True)
    pdop = Column(DECIMAL(5, 2), nullable=True)
    satellites = Column(Integer, nullable=True)
    observations = Column(Text, nullable=True)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    project = relationship("Project", back_populates="survey_points")
    created_by = relationship("User", back_populates="survey_points")

    def __repr__(self):
        return f"<SurveyPoint {self.point_number}>"

class Geometry(Base):
    """Geometric entities (lines, polygons, etc)."""
    __tablename__ = "geometries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    geometry_type = Column(String(50), nullable=False)  # point, line, polygon, etc
    geom = Column(Geometry(srid=4326), nullable=False)
    properties = Column(JSONB, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project", back_populates="geometries")

    def __repr__(self):
        return f"<Geometry {self.geometry_type}>"

class Surface(Base):
    """Topographic surface (TIN, MDT, MDS)."""
    __tablename__ = "surfaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    surface_type = Column(String(50), nullable=False)  # tin, mdt, mds
    point_count = Column(Integer, nullable=True)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project", back_populates="surfaces")

    def __repr__(self):
        return f"<Surface {self.name}>"

class Parcel(Base):
    """Parcel/Land plot entity."""
    __tablename__ = "parcels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    parcel_number = Column(String(50), nullable=False)
    cadastral_id = Column(String(100), nullable=True)
    owner_name = Column(String(255), nullable=True)
    area = Column(DECIMAL(15, 2), nullable=True)
    geometry = Column(Geometry("POLYGON", srid=4326), nullable=True)
    municipality = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)
    observations = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project", back_populates="parcels")

    def __repr__(self):
        return f"<Parcel {self.parcel_number}>"

class Equipment(Base):
    """Surveying equipment inventory."""
    __tablename__ = "equipment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    equipment_type = Column(Enum(EquipmentType), nullable=False)
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    serial_number = Column(String(100), nullable=True)
    status = Column(Enum(EquipmentStatus), default=EquipmentStatus.ACTIVE)
    responsible_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    purchase_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    organization = relationship("Organization", back_populates="equipment")

    def __repr__(self):
        return f"<Equipment {self.brand} {self.model}>"

class Quote(Base):
    """Quote/Quotation entity."""
    __tablename__ = "quotes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    code = Column(String(50), nullable=False, unique=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    status = Column(Enum(QuoteStatus), default=QuoteStatus.DRAFT)
    total = Column(DECIMAL(15, 2), nullable=False)
    tax = Column(DECIMAL(15, 2), nullable=True)
    valid_until = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    organization = relationship("Organization", back_populates="quotes")
    client = relationship("Client", back_populates="quotes")

    def __repr__(self):
        return f"<Quote {self.code}>"

class Invoice(Base):
    """Invoice entity."""
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    ncf = Column(String(50), nullable=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    status = Column(String(50), default="draft")
    total = Column(DECIMAL(15, 2), nullable=False)
    tax = Column(DECIMAL(15, 2), nullable=True)
    issue_date = Column(DateTime, nullable=False, server_default=func.now())
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    organization = relationship("Organization", back_populates="invoices")
    project = relationship("Project", back_populates="invoices")
    client = relationship("Client", back_populates="invoices")

    def __repr__(self):
        return f"<Invoice {self.ncf}>"

class Document(Base):
    """Project documents and files."""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    document_type = Column(Enum(DocumentType), nullable=False)
    file_url = Column(Text, nullable=False)
    file_size = Column(BigInteger, nullable=True)
    file_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    project = relationship("Project", back_populates="documents")
    created_by = relationship("User", back_populates="documents")

    def __repr__(self):
        return f"<Document {self.file_name}>"

class AuditLog(Base):
    """Audit logs for tracking changes."""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(255), nullable=False)
    table_name = Column(String(100), nullable=False)
    record_id = Column(UUID(as_uuid=True), nullable=True)
    changes = Column(JSONB, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    organization = relationship("Organization", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.action}>"
