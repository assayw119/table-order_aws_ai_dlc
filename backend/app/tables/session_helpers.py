"""테이블 세션 라이프사이클 헬퍼 (BR-ORDER-4, BR-TBL-3).

orders/tables 라우터가 공유하는 세션 관련 로직.
"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models import Table, TableSession, Order, OrderHistory
from app.core.logic import to_iso


def ensure_active_session(db: Session, store_id: int, table: Table) -> TableSession:
    """테이블에 active 세션을 보장한다. 없으면 새로 시작 (BR-ORDER-4).

    호출자는 commit 책임을 가진다(여기서는 flush로 id 확보).
    """
    if table.current_session_id is not None:
        session = db.get(TableSession, table.current_session_id)
        if session and session.status == "active":
            return session

    session = TableSession(
        store_id=store_id,
        table_id=table.id,
        status="active",
        started_at=datetime.utcnow(),
    )
    db.add(session)
    db.flush()  # session.id 확보
    table.current_session_id = session.id
    return session


def archive_session(db: Session, table: Table) -> int:
    """active 세션의 주문을 OrderHistory로 이동하고 세션을 종료한다 (BR-TBL-3).

    Returns:
        이동된 주문 수(archived_count). 멱등: active 세션 없으면 0.
    """
    if table.current_session_id is None:
        return 0

    session = db.get(TableSession, table.current_session_id)
    if not session or session.status != "active":
        table.current_session_id = None
        return 0

    orders = db.scalars(
        select(Order).where(Order.session_id == session.id)
    ).all()

    now = datetime.utcnow()
    archived = 0
    for order in orders:
        payload = {
            "order_number": order.order_number,
            "status": order.status,
            "total_amount": order.total_amount,
            "items": [
                {
                    "menu_name": it.menu_name,
                    "unit_price": it.unit_price,
                    "quantity": it.quantity,
                }
                for it in order.items
            ],
            "created_at": to_iso(order.created_at),
        }
        history = OrderHistory(
            store_id=order.store_id,
            table_id=order.table_id,
            session_id=session.id,
            order_number=order.order_number,
            order_payload=payload,
            total_amount=order.total_amount,
            ordered_at=order.created_at,
            completed_at=now,
        )
        db.add(history)
        db.delete(order)  # OrderItem은 cascade 삭제
        archived += 1

    session.status = "closed"
    session.closed_at = now
    table.current_session_id = None  # 현재 주문/총액 리셋 (BR-TBL-3.4)
    return archived


def table_active_orders(db: Session, table: Table) -> list[Order]:
    """테이블의 active 세션 주문 목록을 반환한다 (BR-TBL-2)."""
    if table.current_session_id is None:
        return []
    session = db.get(TableSession, table.current_session_id)
    if not session or session.status != "active":
        return []
    return db.scalars(
        select(Order)
        .where(Order.session_id == session.id)
        .order_by(Order.created_at)
    ).all()
