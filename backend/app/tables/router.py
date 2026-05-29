"""테이블 라우터: 초기 설정, 현재 주문 집계, 이용 완료, 과거 내역 (US-A3)."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.core.security import get_current_admin, hash_password
from app.core.models import Table, Order, OrderHistory
from app.core.schemas import (
    TableSetupRequest, TableResponse, TableSummaryResponse,
    CheckoutResponse, OrderHistoryResponse, OrderResponse,
)
from app.core.logic import to_iso
from app.tables.session_helpers import archive_session, table_active_orders
from app.realtime.event_bus import event_bus, store_topic, table_topic

router = APIRouter(prefix="/api/admin/tables", tags=["tables"])


@router.post("/setup", response_model=TableResponse, status_code=201)
def setup_table(
    req: TableSetupRequest,
    db: Session = Depends(get_session),
    admin: dict = Depends(get_current_admin),
):
    """테이블 태블릿 초기 설정 (BR-TBL-1). 기존 테이블이면 비밀번호 재설정."""
    table = db.scalar(
        select(Table).where(
            Table.store_id == admin["store_id"], Table.table_number == req.table_number
        )
    )
    if table:
        table.password_hash = hash_password(req.table_password)
    else:
        table = Table(
            store_id=admin["store_id"],
            table_number=req.table_number,
            password_hash=hash_password(req.table_password),
        )
        db.add(table)
    db.commit()
    db.refresh(table)
    return table


@router.get("", response_model=list[TableSummaryResponse])
def list_table_summaries(
    db: Session = Depends(get_session), admin: dict = Depends(get_current_admin)
):
    """테이블별 현재 주문/총액 집계 (US-A2, BR-TBL-2)."""
    tables = db.scalars(
        select(Table).where(Table.store_id == admin["store_id"]).order_by(Table.table_number)
    ).all()
    summaries = []
    for table in tables:
        orders = table_active_orders(db, table)
        total = sum(o.total_amount for o in orders)
        summaries.append(
            TableSummaryResponse(
                table_id=table.id,
                table_number=table.table_number,
                session_active=table.current_session_id is not None,
                total_amount=total,
                orders=[OrderResponse.model_validate(o) for o in orders],
            )
        )
    return summaries


@router.post("/{table_id}/checkout", response_model=CheckoutResponse)
async def checkout_table(
    table_id: int,
    db: Session = Depends(get_session),
    admin: dict = Depends(get_current_admin),
):
    """테이블 이용 완료 처리 (BR-TBL-3). 트랜잭션 (NFR-R2)."""
    table = db.get(Table, table_id)
    if not table or table.store_id != admin["store_id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="테이블을 찾을 수 없습니다.")
    try:
        archived = archive_session(db, table)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="이용 완료 처리 중 오류가 발생했습니다.")

    event = {
        "type": "session_closed",
        "table_id": table.id,
        "order": None,
        "ts": to_iso(datetime.utcnow()),
    }
    await event_bus.publish(store_topic(table.store_id), event)
    await event_bus.publish(table_topic(table.id), event)
    return CheckoutResponse(table_number=table.table_number, archived_count=archived)


@router.get("/{table_id}/history", response_model=list[OrderHistoryResponse])
def table_history(
    table_id: int,
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    db: Session = Depends(get_session),
    admin: dict = Depends(get_current_admin),
):
    """과거 주문 내역 조회 (BR-TBL-5). completed_at 역순, 날짜 필터."""
    table = db.get(Table, table_id)
    if not table or table.store_id != admin["store_id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="테이블을 찾을 수 없습니다.")
    stmt = select(OrderHistory).where(OrderHistory.table_id == table_id)
    if date_from is not None:
        stmt = stmt.where(OrderHistory.completed_at >= date_from)
    if date_to is not None:
        stmt = stmt.where(OrderHistory.completed_at <= date_to)
    stmt = stmt.order_by(OrderHistory.completed_at.desc())
    return db.scalars(stmt).all()
