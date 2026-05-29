"""주문 라우터: 생성/조회/상태변경/삭제 + 실시간 이벤트 발행.

스토리: US-C4(주문 생성), US-C5(현재 세션 조회), US-A2(매장 주문/상태변경).
"""
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.core.security import get_current_admin, get_current_table
from app.core.models import Table, MenuItem, Order, OrderItem
from app.core.schemas import (
    OrderCreateRequest, OrderResponse, OrderStatusRequest,
)
from app.core.logic import calc_total, next_order_number, is_valid_status, to_iso
from app.tables.session_helpers import ensure_active_session, table_active_orders
from app.realtime.event_bus import event_bus, store_topic, table_topic

router = APIRouter(tags=["orders"])


def _order_event(event_type: str, order: Order) -> dict:
    """SSE 이벤트 payload 생성."""
    return {
        "type": event_type,
        "table_id": order.table_id,
        "order": {
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "total_amount": order.total_amount,
            "items": [
                {"menu_name": it.menu_name, "unit_price": it.unit_price, "quantity": it.quantity}
                for it in order.items
            ],
            "created_at": to_iso(order.created_at),
        },
        "ts": to_iso(datetime.utcnow()),
    }


async def _publish(store_id: int, table_id: int, event: dict) -> None:
    """store/table 토픽 양쪽으로 이벤트 발행 (BR-ORDER-9, BR-RT-1)."""
    await event_bus.publish(store_topic(store_id), event)
    await event_bus.publish(table_topic(table_id), event)


@router.post("/api/orders", response_model=OrderResponse, status_code=201)
async def create_order(
    req: OrderCreateRequest,
    db: Session = Depends(get_session),
    table_ctx: dict = Depends(get_current_table),
):
    """주문 생성 (BR-ORDER-1~6). 트랜잭션으로 처리 (NFR-R1)."""
    store_id = table_ctx["store_id"]
    table = db.get(Table, table_ctx["table_id"])
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="테이블을 찾을 수 없습니다.")

    # 메뉴 조회 및 스냅샷 구성 (BR-ORDER-2)
    snapshot_items: list[tuple[MenuItem, int]] = []
    for line in req.items:
        menu = db.get(MenuItem, line.menu_item_id)
        if not menu or menu.store_id != store_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"메뉴(id={line.menu_item_id})를 찾을 수 없습니다.",
            )
        snapshot_items.append((menu, line.quantity))

    try:
        # 세션 보장 (BR-ORDER-4)
        session = ensure_active_session(db, store_id, table)

        # 당일 주문번호 발급 (BR-ORDER-5)
        today = date.today()
        existing = db.scalars(
            select(Order.order_number).where(
                Order.store_id == store_id, Order.order_date == today
            )
        ).all()
        order_no = next_order_number(existing)

        # 총액 계산 (BR-ORDER-3)
        total = calc_total((m.price, q) for m, q in snapshot_items)

        order = Order(
            store_id=store_id,
            table_id=table.id,
            session_id=session.id,
            order_number=order_no,
            order_date=today,
            status="대기중",
            total_amount=total,
            created_at=datetime.utcnow(),
        )
        for menu, qty in snapshot_items:
            order.items.append(
                OrderItem(
                    menu_item_id=menu.id,
                    menu_name=menu.name,
                    unit_price=menu.price,
                    quantity=qty,
                )
            )
        db.add(order)
        db.commit()
        db.refresh(order)
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="주문 처리 중 오류가 발생했습니다.")

    await _publish(store_id, table.id, _order_event("order_created", order))
    return order


@router.get("/api/orders/current", response_model=list[OrderResponse])
def list_current_session_orders(
    db: Session = Depends(get_session),
    table_ctx: dict = Depends(get_current_table),
):
    """현재 세션 주문 내역 조회 (US-C5, BR-TBL-2)."""
    table = db.get(Table, table_ctx["table_id"])
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="테이블을 찾을 수 없습니다.")
    return table_active_orders(db, table)


@router.get("/api/admin/orders", response_model=list[OrderResponse])
def admin_list_orders(
    table_number: int | None = None,
    db: Session = Depends(get_session),
    admin: dict = Depends(get_current_admin),
):
    """매장 전체 현재 주문 조회 (US-A2). table_number로 필터 가능."""
    stmt = select(Order).where(Order.store_id == admin["store_id"])
    if table_number is not None:
        table = db.scalar(
            select(Table).where(
                Table.store_id == admin["store_id"], Table.table_number == table_number
            )
        )
        if not table:
            return []
        stmt = stmt.where(Order.table_id == table.id)
    stmt = stmt.order_by(Order.created_at.desc())
    return db.scalars(stmt).all()


@router.patch("/api/admin/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    req: OrderStatusRequest,
    db: Session = Depends(get_session),
    admin: dict = Depends(get_current_admin),
):
    """주문 상태 변경 (BR-ORDER-7)."""
    order = db.get(Order, order_id)
    if not order or order.store_id != admin["store_id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="주문을 찾을 수 없습니다.")
    if not is_valid_status(req.status):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="허용되지 않는 주문 상태입니다.")
    order.status = req.status
    db.commit()
    db.refresh(order)
    await _publish(order.store_id, order.table_id, _order_event("order_status_changed", order))
    return order


@router.delete("/api/admin/orders/{order_id}", status_code=204)
async def delete_order(
    order_id: int,
    db: Session = Depends(get_session),
    admin: dict = Depends(get_current_admin),
):
    """주문 삭제(직권 수정) (BR-ORDER-8)."""
    order = db.get(Order, order_id)
    if not order or order.store_id != admin["store_id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="주문을 찾을 수 없습니다.")
    store_id, table_id = order.store_id, order.table_id
    event = _order_event("order_deleted", order)
    db.delete(order)
    db.commit()
    await _publish(store_id, table_id, event)
    return None
