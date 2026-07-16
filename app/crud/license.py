import secrets
import string
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.generated_license import GeneratedLicense
from app.models.license_group import LicenseGroup
from app.models.user import User
from app.schemas.license import SeatInput

_LICENSE_TYPE_CODE = {"single": "01", "lab": "02"}
_KEY_ALPHABET = string.ascii_uppercase + string.digits
_PASSWORD_ALPHABET = string.ascii_letters + string.digits


def _generate_license_key(license_type: str) -> str:
    code = _LICENSE_TYPE_CODE[license_type]
    random_part = "".join(secrets.choice(_KEY_ALPHABET) for _ in range(10))
    return f"NUVOAI-{code}-{random_part}"


def _generate_password() -> str:
    return "".join(secrets.choice(_PASSWORD_ALPHABET) for _ in range(12))


async def create_license_group(db: AsyncSession, *, type: str, org_name: str, max_seats: int) -> LicenseGroup:
    group = LicenseGroup(type=type, org_name=org_name, max_seats=max_seats, bought_at=date.today())
    db.add(group)
    await db.flush()
    await db.refresh(group)
    return group


async def get_license_group_by_id(db: AsyncSession, license_group_id: int) -> LicenseGroup | None:
    result = await db.execute(select(LicenseGroup).where(LicenseGroup.id == license_group_id))
    return result.scalar_one_or_none()


async def generate_licenses_for_group(
    db: AsyncSession, *, group: LicenseGroup, seats: list[SeatInput]
) -> list[dict]:
    results = []
    for seat in seats:
        license_key = _generate_license_key(group.type)
        generated_license = GeneratedLicense(
            license_group_id=group.id,
            license_key=license_key,
            email=seat.email,
            validity_days=seat.validity_days,
        )
        db.add(generated_license)
        await db.flush()

        password = _generate_password()
        user = User(
            generated_license_id=generated_license.id,
            email=seat.email,
            password_hash=hash_password(password),
        )
        db.add(user)
        await db.flush()

        results.append({"email": seat.email, "password": password, "license_key": license_key})

    return results
