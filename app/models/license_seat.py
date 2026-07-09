from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, Index, Enum, text
from sqlalchemy.schema import DDL
from sqlalchemy.event import listen

from app.db.connection import Base

SeatStatusEnum = Enum("created", "activated", "expired", name="seat_status")

# Enforces license_group.max_seats at the DB layer: a seat that isn't already
# 'expired' counts against the cap, checked before every insert.
_ENFORCE_SEAT_LIMIT_FUNCTION = DDL(
    """
    CREATE OR REPLACE FUNCTION enforce_seat_limit() RETURNS TRIGGER AS $$
    DECLARE
        v_max_seats  INTEGER;
        v_used_seats INTEGER;
    BEGIN
        SELECT max_seats INTO v_max_seats FROM license_group WHERE id = NEW.license_group_id;

        SELECT COUNT(*) INTO v_used_seats
        FROM license_seat
        WHERE license_group_id = NEW.license_group_id
          AND status != 'expired';

        IF v_used_seats >= v_max_seats THEN
            RAISE EXCEPTION 'Seat limit (%) reached for license_group_id %', v_max_seats, NEW.license_group_id;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
)

_ENFORCE_SEAT_LIMIT_TRIGGER = DDL(
    """
    CREATE TRIGGER trg_enforce_seat_limit
    BEFORE INSERT ON license_seat
    FOR EACH ROW EXECUTE FUNCTION enforce_seat_limit();
    """
)

_DROP_ENFORCE_SEAT_LIMIT_TRIGGER = DDL("DROP TRIGGER IF EXISTS trg_enforce_seat_limit ON license_seat;")
_DROP_ENFORCE_SEAT_LIMIT_FUNCTION = DDL("DROP FUNCTION IF EXISTS enforce_seat_limit();")


class LicenseSeat(Base):
    __tablename__ = "license_seat"

    id = Column(Integer, primary_key=True)
    license_group_id = Column(Integer, ForeignKey("license_group.id", ondelete="CASCADE"), nullable=False)
    license_key = Column(String(255), nullable=False, unique=True)  # per-seat, renews independently
    machine_fingerprint_hash = Column(Text)
    status = Column(SeatStatusEnum, nullable=False, server_default="created")
    activated_at = Column(TIMESTAMP(timezone=True))
    expired_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    __table_args__ = (
        # A machine can hold only one seat per license group, once bound.
        Index(
            "uq_group_machine",
            "license_group_id",
            "machine_fingerprint_hash",
            unique=True,
            postgresql_where=text("machine_fingerprint_hash IS NOT NULL"),
        ),
    )


listen(LicenseSeat.__table__, "after_create", _ENFORCE_SEAT_LIMIT_FUNCTION)
listen(LicenseSeat.__table__, "after_create", _ENFORCE_SEAT_LIMIT_TRIGGER)
listen(LicenseSeat.__table__, "before_drop", _DROP_ENFORCE_SEAT_LIMIT_TRIGGER)
listen(LicenseSeat.__table__, "before_drop", _DROP_ENFORCE_SEAT_LIMIT_FUNCTION)
