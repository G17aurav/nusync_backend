from pydantic import BaseModel, EmailStr, Field


class AdminRegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class AdminOut(BaseModel):
    id: int
    username: str
    email: str
    mfa_enabled: bool

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class LoginPasswordResponse(BaseModel):
    mfa_token: str
    mfa_enabled: bool
    # Only set when mfa_enabled is False: this login call doubles as MFA setup.
    secret: str | None = None
    provisioning_uri: str | None = None
    qr_code_base64: str | None = None


class MfaCodeRequest(BaseModel):
    mfa_token: str
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class AccessTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str
