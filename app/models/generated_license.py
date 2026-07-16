from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, Index, Enum, text

from app.db.connection import Base

LicenseKeyStatusEnum = Enum("unused", "activated", "expired", name="license_key_status")


class GeneratedLicense(Base):
    __tablename__ = "generated_license"

    id = Column(Integer, primary_key=True)
    license_group_id = Column(Integer, ForeignKey("license_group.id", ondelete="CASCADE"), nullable=False)
    license_key = Column(Text, nullable=False, unique=True)  # signed payload.signature, minted at generation time
    email = Column(String(255), nullable=False)  # target recipient
    validity_days = Column(Integer, nullable=False)
    machine_fingerprint_hash = Column(Text)  # set on first activation
    status = Column(LicenseKeyStatusEnum, nullable=False, server_default="unused")
    activated_at = Column(TIMESTAMP(timezone=True))
    expired_at = Column(TIMESTAMP(timezone=True))  # activated_at + validity_days
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    __table_args__ = (
        # A machine can hold only one key per license group, once bound.
        Index(
            "uq_license_group_machine",
            "license_group_id",
            "machine_fingerprint_hash",
            unique=True,
            postgresql_where=text("machine_fingerprint_hash IS NOT NULL"),
        ),
    )
