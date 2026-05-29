"""순수 비즈니스 로직 헬퍼 함수.

기술/DB 비종속의 순수 함수로, 속성 기반 테스트(PBT)의 주요 대상입니다.
(functional-design/business-logic-model.md의 Testable Properties 참조)
"""
from datetime import datetime
from collections.abc import Iterable

from app.core.config import ORDER_STATUSES


def calc_total(items: Iterable[tuple[int, int]]) -> int:
    """주문 총액을 계산한다 (BR-ORDER-3, 속성 P1).

    Args:
        items: (unit_price, quantity) 튜플의 반복자.
    Returns:
        Σ(unit_price * quantity). 모든 입력이 0 이상이면 결과도 0 이상.
    """
    return sum(unit_price * quantity for unit_price, quantity in items)


def next_order_number(existing_numbers: Iterable[int]) -> int:
    """당일 다음 주문 번호를 산출한다 (BR-ORDER-5, 속성 P2).

    Args:
        existing_numbers: 같은 매장/같은 날짜의 기존 주문 번호 모음.
    Returns:
        기존 번호의 최댓값 + 1. 비어있으면 1. 항상 1 이상.
    """
    numbers = list(existing_numbers)
    if not numbers:
        return 1
    return max(numbers) + 1


def is_valid_status(status: str) -> bool:
    """주문 상태가 허용 집합에 속하는지 검증한다 (BR-ORDER-7, 속성 P5)."""
    return status in ORDER_STATUSES


def serialize_order_to_history(order_payload: dict) -> dict:
    """주문을 OrderHistory payload로 직렬화한다 (BR-TBL-3, 속성 P3).

    items와 total을 보존하는 직렬화. 역직렬화는 deserialize_history_payload.
    """
    return {
        "order_number": order_payload["order_number"],
        "status": order_payload["status"],
        "total_amount": order_payload["total_amount"],
        "items": [
            {
                "menu_name": it["menu_name"],
                "unit_price": it["unit_price"],
                "quantity": it["quantity"],
            }
            for it in order_payload["items"]
        ],
        "created_at": order_payload["created_at"],
    }


def deserialize_history_payload(payload: dict) -> dict:
    """history payload에서 핵심 주문 정보를 복원한다 (속성 P3 round-trip)."""
    return {
        "order_number": payload["order_number"],
        "status": payload["status"],
        "total_amount": payload["total_amount"],
        "items": [
            {
                "menu_name": it["menu_name"],
                "unit_price": it["unit_price"],
                "quantity": it["quantity"],
            }
            for it in payload["items"]
        ],
        "created_at": payload["created_at"],
    }


def to_iso(dt: datetime) -> str:
    """datetime을 ISO 8601 문자열로 변환한다."""
    return dt.isoformat()
