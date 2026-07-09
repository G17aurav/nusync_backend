from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.crud import admin as admin_crud
from app.db.connection import get_db
from app.schemas.admin import (
    AccessTokenResponse,
    AdminOut,
    AdminRegisterRequest,
    LoginPasswordResponse,
    LoginRequest,
    MfaCodeRequest,
    RefreshRequest,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/register", response_model=AdminOut, status_code=status.HTTP_201_CREATED)
async def register(payload: AdminRegisterRequest, db: AsyncSession = Depends(get_db)):
    if await admin_crud.admin_exists(db):
        raise HTTPException(status.HTTP_409_CONFLICT, "An admin account already exists")

    try:
        admin = await admin_crud.create_admin(
            db,
            username=payload.username,
            email=payload.email,
            password_hash=security.hash_password(payload.password),
        )
    except IntegrityError:
        raise HTTPException(status.HTTP_409_CONFLICT, "An admin account already exists")

    return admin


@router.post("/login", response_model=LoginPasswordResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    admin = await admin_crud.get_admin_by_email(db, payload.email)
    if admin is None or not security.verify_password(payload.password, admin.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")

    mfa_token = security.create_mfa_pending_token(admin.id)

    if admin.mfa_enabled:
        return LoginPasswordResponse(mfa_token=mfa_token, mfa_enabled=True)

    # MFA not set up yet: this login doubles as setup, handing back a fresh secret + QR.
    secret = security.generate_mfa_secret()
    await admin_crud.set_mfa_secret(db, admin, secret)

    return LoginPasswordResponse(
        mfa_token=mfa_token,
        mfa_enabled=False,
        secret=secret,
        provisioning_uri=security.build_provisioning_uri(secret, admin.email),
        qr_code_base64=security.build_qr_code_base64(secret, admin.email),
    )


@router.post("/mfa/enable", response_model=AccessTokenResponse)
async def enable_mfa(payload: MfaCodeRequest, db: AsyncSession = Depends(get_db)):
    admin_id = security.decode_mfa_pending_token(payload.mfa_token)

    admin = await admin_crud.get_admin_by_id(db, admin_id)
    if admin is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Admin not found")
    if admin.mfa_enabled:
        raise HTTPException(status.HTTP_409_CONFLICT, "MFA is already enabled for this account")
    if not admin.mfa_secret:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Call /admin/login first to get a secret")
    if not security.verify_totp_code(admin.mfa_secret, payload.code):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid MFA code")

    await admin_crud.enable_mfa(db, admin)
    return AccessTokenResponse(
        access_token=security.create_access_token(admin.id),
        refresh_token=security.create_refresh_token(admin.id),
    )


@router.post("/mfa/verify", response_model=AccessTokenResponse)
async def verify_mfa(payload: MfaCodeRequest, db: AsyncSession = Depends(get_db)):
    admin_id = security.decode_mfa_pending_token(payload.mfa_token)

    admin = await admin_crud.get_admin_by_id(db, admin_id)
    if admin is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Admin not found")
    if not admin.mfa_enabled or not admin.mfa_secret:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "MFA is not enabled for this account")
    if not security.verify_totp_code(admin.mfa_secret, payload.code):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid MFA code")

    return AccessTokenResponse(
        access_token=security.create_access_token(admin.id),
        refresh_token=security.create_refresh_token(admin.id),
    )


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    admin_id = security.decode_refresh_token(payload.refresh_token)

    admin = await admin_crud.get_admin_by_id(db, admin_id)
    if admin is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Admin not found")

    return AccessTokenResponse(
        access_token=security.create_access_token(admin.id),
        refresh_token=security.create_refresh_token(admin.id),
    )
