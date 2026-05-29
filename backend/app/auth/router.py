"""인증 라우터: 관리자 로그인, 테이블 로그인 (US-A1, US-C1, US-T2)."""
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.core import config, security
from app.core.models import Store, AdminUser, Table
from app.core.schemas import (
    AdminLoginRequest, TableLoginRequest, TokenResponse, TableTokenResponse, StoreInfo,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/admin/login", response_model=TokenResponse)
def admin_login(req: AdminLoginRequest, db: Session = Depends(get_session)):
    """관리자 로그인 (BR-AUTH-1, 2, 5)."""
    throttle_key = f"admin:{req.store_code}:{req.username}"
    if not security.check_login_allowed(throttle_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="로그인 시도가 너무 많습니다. 잠시 후 다시 시도해주세요.",
        )

    store = db.scalar(select(Store).where(Store.store_code == req.store_code))
    admin = None
    if store:
        admin = db.scalar(
            select(AdminUser).where(
                AdminUser.store_id == store.id, AdminUser.username == req.username
            )
        )

    if not store or not admin or not security.verify_password(req.password, admin.password_hash):
        security.record_login_failure(throttle_key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="매장 식별자, 사용자명 또는 비밀번호가 올바르지 않습니다.",
        )

    security.reset_login_attempts(throttle_key)
    token = security.create_token(
        {"sub": admin.username, "store_id": store.id, "role": "admin"},
        config.ADMIN_TOKEN_TTL_SECONDS,
    )
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=config.ADMIN_TOKEN_TTL_SECONDS)
    return TokenResponse(
        access_token=token,
        expires_at=expires_at,
        store=StoreInfo.model_validate(store),
    )


@router.post("/table/login", response_model=TableTokenResponse)
def table_login(req: TableLoginRequest, db: Session = Depends(get_session)):
    """테이블 태블릿 로그인 (BR-AUTH-3)."""
    throttle_key = f"table:{req.store_code}:{req.table_number}"
    if not security.check_login_allowed(throttle_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="로그인 시도가 너무 많습니다. 잠시 후 다시 시도해주세요.",
        )

    store = db.scalar(select(Store).where(Store.store_code == req.store_code))
    table = None
    if store:
        table = db.scalar(
            select(Table).where(
                Table.store_id == store.id, Table.table_number == req.table_number
            )
        )

    if (
        not store
        or not table
        or not table.password_hash
        or not security.verify_password(req.table_password, table.password_hash)
    ):
        security.record_login_failure(throttle_key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="테이블 정보 또는 비밀번호가 올바르지 않습니다.",
        )

    security.reset_login_attempts(throttle_key)
    token = security.create_token(
        {"store_id": store.id, "table_id": table.id, "role": "table"},
        config.TABLE_TOKEN_TTL_SECONDS,
    )
    return TableTokenResponse(
        access_token=token,
        table_id=table.id,
        table_number=table.table_number,
        store_name=store.name,
    )
