import base64
import io
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
import pyotp
import qrcode
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

bearer_scheme = HTTPBearer()


# ---- passwords ----


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


# ---- JWT ----


def _create_token(subject: int, token_type: str, expires_minutes: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "type": token_type,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_mfa_pending_token(admin_id: int) -> str:
    return _create_token(admin_id, "mfa_pending", settings.mfa_pending_token_expire_minutes)


def create_access_token(admin_id: int) -> str:
    return _create_token(admin_id, "access", settings.access_token_expire_minutes)


def create_refresh_token(admin_id: int) -> str:
    return _create_token(admin_id, "refresh", settings.refresh_token_expire_minutes)


def _decode_token_of_type(token: str, expected_type: str) -> int:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")

    if payload.get("type") != expected_type:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")

    return int(payload["sub"])


def decode_mfa_pending_token(token: str) -> int:
    return _decode_token_of_type(token, "mfa_pending")


def decode_refresh_token(token: str) -> int:
    return _decode_token_of_type(token, "refresh")


def get_current_admin_id(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> int:
    """For future endpoints that require a fully logged-in admin (Authorize with access_token)."""
    return _decode_token_of_type(credentials.credentials, "access")


# ---- TOTP / MFA ----


def generate_mfa_secret() -> str:
    return pyotp.random_base32()


def verify_totp_code(secret: str, code: str) -> bool:
    return pyotp.TOTP(secret).verify(code, valid_window=1)


def build_provisioning_uri(secret: str, account_email: str) -> str:
    return pyotp.TOTP(secret).provisioning_uri(name=account_email, issuer_name=settings.mfa_issuer)


def build_qr_code_base64(secret: str, account_email: str) -> str:
    uri = build_provisioning_uri(secret, account_email)
    image = qrcode.make(uri)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()
