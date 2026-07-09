from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP, Index, text

from app.db.connection import Base


class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    mfa_secret = Column(Text)
    mfa_enabled = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    __table_args__ = (
        # Enforces a single admin row. Expression indexes aren't tracked well
        # by autogenerate, so changes to this line need a hand-written migration.
        Index("one_admin_only", text("(true)"), unique=True),
    )
