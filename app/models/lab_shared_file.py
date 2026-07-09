from sqlalchemy import Column, Integer, BigInteger, String, Text, ForeignKey, TIMESTAMP, Index, text

from app.db.connection import Base


class LabSharedFile(Base):
    __tablename__ = "lab_shared_file"

    id = Column(Integer, primary_key=True)
    license_group_id = Column(Integer, ForeignKey("license_group.id", ondelete="CASCADE"), nullable=False)
    uploaded_by_seat_id = Column(Integer, ForeignKey("license_seat.id", ondelete="SET NULL"))
    file_name = Column(String(500), nullable=False)
    storage_path = Column(Text, nullable=False)  # S3 key / blob path, not the file itself
    checksum = Column(String(128))  # for integrity + dedupe/change detection
    file_size_bytes = Column(BigInteger)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    __table_args__ = (
        Index("idx_lab_shared_file_group", "license_group_id"),
    )
