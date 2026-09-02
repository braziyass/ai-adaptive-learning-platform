from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.presentation.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, LogoutRequest
from app.core.database import get_db
from app.infrastructure.auth.service import AuthService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    auth = AuthService(db)
    user = await auth.authenticate(payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access, refresh = await auth.create_tokens_for_user(user.id, extra_claims={"role": user.role})
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    auth = AuthService(db)
    try:
        access, new_refresh = await auth.rotate_refresh_token(payload.refresh_token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return TokenResponse(access_token=access, refresh_token=new_refresh)


@router.post("/logout")
async def logout(payload: LogoutRequest, db: AsyncSession = Depends(get_db)):
    auth = AuthService(db)
    await auth.revoke_refresh(payload.refresh_token)
    return {"detail": "Logged out"}
