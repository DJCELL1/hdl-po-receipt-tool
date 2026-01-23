"""
Database connection and ORM models for HDL PO Receipt Tool
"""

from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, Boolean, Numeric, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
import config

# Create engine with psycopg3 support
# Convert postgresql:// to postgresql+psycopg:// for psycopg3
database_url = config.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
elif database_url.startswith("postgres://"):
    # Heroku/Render style URLs
    database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)

engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String(100))
    status = Column(String(50), default="pending")

    # Relationships
    extractions = relationship("Extraction", back_populates="upload", cascade="all, delete-orphan")


class Extraction(Base):
    __tablename__ = "extractions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    upload_id = Column(UUID(as_uuid=True), ForeignKey("uploads.id"), nullable=False)
    supplier_name = Column(String(255))
    docket_number = Column(String(100))
    po_reference = Column(String(100))
    delivery_date = Column(Date)
    raw_ocr_text = Column(Text)
    confidence_score = Column(Numeric(5, 2))
    extracted_at = Column(DateTime, default=datetime.utcnow)
    reviewed = Column(Boolean, default=False)
    reviewed_at = Column(DateTime)
    reviewed_by = Column(String(100))

    # Relationships
    upload = relationship("Upload", back_populates="extractions")
    lines = relationship("ExtractionLine", back_populates="extraction", cascade="all, delete-orphan")
    receipts = relationship("Receipt", back_populates="extraction")


class ExtractionLine(Base):
    __tablename__ = "extraction_lines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    extraction_id = Column(UUID(as_uuid=True), ForeignKey("extractions.id"), nullable=False)
    line_number = Column(Integer, nullable=False)
    sku = Column(String(100))
    description = Column(Text)
    quantity_delivered = Column(Numeric(10, 2))
    confidence_score = Column(Numeric(5, 2))
    flags = Column(JSONB, default=[])

    # Relationships
    extraction = relationship("Extraction", back_populates="lines")


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    extraction_id = Column(UUID(as_uuid=True), ForeignKey("extractions.id"), nullable=False)
    cin7_po_id = Column(String(100), nullable=False)
    po_reference = Column(String(100), nullable=False)
    supplier_name = Column(String(255))
    docket_number = Column(String(100))
    receipt_date = Column(Date, nullable=False)
    cin7_response = Column(JSONB)
    cin7_receipt_id = Column(String(100))
    posted_at = Column(DateTime, default=datetime.utcnow)
    posted_by = Column(String(100))
    status = Column(String(50), default="success")
    error_message = Column(Text)

    # Relationships
    extraction = relationship("Extraction", back_populates="receipts")
    lines = relationship("ReceiptLine", back_populates="receipt", cascade="all, delete-orphan")


class ReceiptLine(Base):
    __tablename__ = "receipt_lines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    receipt_id = Column(UUID(as_uuid=True), ForeignKey("receipts.id"), nullable=False)
    extraction_line_id = Column(UUID(as_uuid=True), ForeignKey("extraction_lines.id"))
    cin7_line_id = Column(String(100))
    sku = Column(String(100))
    description = Column(Text)
    quantity_ordered = Column(Numeric(10, 2))
    quantity_received = Column(Numeric(10, 2))
    quantity_remaining = Column(Numeric(10, 2))
    flags = Column(JSONB, default=[])

    # Relationships
    receipt = relationship("Receipt", back_populates="lines")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String(50), nullable=False)
    user_id = Column(String(100))
    changes = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)


def check_duplicate_receipt(db, supplier_name: str, docket_number: str) -> bool:
    """Check if a receipt already exists for this supplier + docket number"""
    existing = db.query(Receipt).filter(
        Receipt.supplier_name == supplier_name,
        Receipt.docket_number == docket_number,
        Receipt.status == "success"
    ).first()
    return existing is not None
