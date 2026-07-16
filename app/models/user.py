from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, text

from app.db.connection import Base


class User(Base):
    """Owner of a generated_license: created with a sales-generated password once a key is assigned."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    generated_license_id = Column(
        Integer, ForeignKey("generated_license.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)  # sales-generated
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
