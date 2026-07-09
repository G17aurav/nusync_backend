from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin


async def admin_exists(db: AsyncSession) -> bool:
    result = await db.execute(select(Admin.id).limit(1))
    return result.scalar_one_or_none() is not None


async def get_admin_by_email(db: AsyncSession, email: str) -> Admin | None:
    result = await db.execute(select(Admin).where(Admin.email == email))
    return result.scalar_one_or_none()


async def get_admin_by_id(db: AsyncSession, admin_id: int) -> Admin | None:
    result = await db.execute(select(Admin).where(Admin.id == admin_id))
    return result.scalar_one_or_none()


async def create_admin(db: AsyncSession, *, username: str, email: str, password_hash: str) -> Admin:
    admin = Admin(username=username, email=email, password_hash=password_hash)
    db.add(admin)
    await db.flush()
    await db.refresh(admin)
    return admin


async def set_mfa_secret(db: AsyncSession, admin: Admin, secret: str) -> Admin:
    admin.mfa_secret = secret
    await db.flush()
    await db.refresh(admin)
    return admin


async def enable_mfa(db: AsyncSession, admin: Admin) -> Admin:
    admin.mfa_enabled = True
    await db.flush()
    await db.refresh(admin)
    return admin
