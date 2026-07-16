from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.crud import license as license_crud
from app.db.connection import get_db
from app.schemas.license import (
    CreateLicenseGroupRequest,
    GenerateLicensesRequest,
    GenerateLicensesResponse,
    GeneratedSeatOut,
    LicenseGroupOut,
)

router = APIRouter(prefix="/license", tags=["license"])


@router.post("/groups", response_model=LicenseGroupOut, status_code=status.HTTP_201_CREATED)
async def create_license_group(
    payload: CreateLicenseGroupRequest,
    db: AsyncSession = Depends(get_db),
    admin_id: int = Depends(security.get_current_admin_id),
):
    if payload.type == "single" and payload.max_seats != 1:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "A single license must have max_seats = 1")

    return await license_crud.create_license_group(
        db, type=payload.type, org_name=payload.org_name, max_seats=payload.max_seats
    )


@router.post("/groups/{license_group_id}/generate", response_model=GenerateLicensesResponse)
async def generate_licenses(
    license_group_id: int,
    payload: GenerateLicensesRequest,
    db: AsyncSession = Depends(get_db),
    admin_id: int = Depends(security.get_current_admin_id),
):
    group = await license_crud.get_license_group_by_id(db, license_group_id)
    if group is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "License group not found")

    if len(payload.seats) != group.max_seats:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Expected exactly {group.max_seats} seat(s), got {len(payload.seats)}",
        )

    try:
        seats = await license_crud.generate_licenses_for_group(db, group=group, seats=payload.seats)
    except IntegrityError:
        raise HTTPException(status.HTTP_409_CONFLICT, "One or more emails are already in use")

    return GenerateLicensesResponse(
        license_group_id=group.id,
        seats=[GeneratedSeatOut(**seat) for seat in seats],
    )
