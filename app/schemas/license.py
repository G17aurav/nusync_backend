from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


class CreateLicenseGroupRequest(BaseModel):
    type: str = Field(pattern=r"^(single|lab)$")
    org_name: str = Field(min_length=1, max_length=255)
    max_seats: int = Field(ge=1)


class LicenseGroupOut(BaseModel):
    id: int
    type: str
    org_name: str
    max_seats: int
    bought_at: date | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SeatInput(BaseModel):
    email: EmailStr
    validity_days: int = Field(ge=1)


class GenerateLicensesRequest(BaseModel):
    seats: list[SeatInput] = Field(min_length=1)


class GeneratedSeatOut(BaseModel):
    email: str
    password: str
    license_key: str


class GenerateLicensesResponse(BaseModel):
    license_group_id: int
    seats: list[GeneratedSeatOut]
