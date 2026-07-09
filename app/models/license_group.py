from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, CheckConstraint, Enum, text

from app.db.connection import Base

LicenseTypeEnum = Enum("single", "lab", name="license_type")


class LicenseGroup(Base):
    __tablename__ = "license_group"

    id = Column(Integer, primary_key=True)
    type = Column(LicenseTypeEnum, nullable=False)
    org_name = Column(String(255), nullable=False)
    user_name = Column(String(255), nullable=False)  # buyer
    email = Column(String(255), nullable=False)  # buyer
    max_seats = Column(Integer, nullable=False, server_default="1")
    bought_at = Column(Date)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    __table_args__ = (
        CheckConstraint(
            "(type = 'single' AND max_seats = 1) OR (type = 'lab' AND max_seats >= 1)",
            name="chk_seat_cap",
        ),
    )
