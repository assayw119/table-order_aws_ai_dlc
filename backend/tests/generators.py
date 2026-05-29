"""속성 기반 테스트용 도메인 제너레이터 (PBT-07).

도메인 제약을 존중하는 재사용 가능한 Hypothesis 전략을 정의한다.
"""
from hypothesis import strategies as st

from app.core.config import ORDER_STATUSES

# 가격: 0 이상의 현실적 범위 (원)
prices = st.integers(min_value=0, max_value=1_000_000)

# 수량: 1 이상 (BR-ORDER-1)
quantities = st.integers(min_value=1, max_value=100)

# (unit_price, quantity) 항목
order_line_tuples = st.tuples(prices, quantities)

# 주문 항목 목록 (비어있을 수 있음 / 1개 이상 버전)
order_lines = st.lists(order_line_tuples, max_size=20)
non_empty_order_lines = st.lists(order_line_tuples, min_size=1, max_size=20)

# 메뉴명: 비어있지 않은 텍스트
menu_names = st.text(min_size=1, max_size=40)

# 유효한 주문 상태
valid_statuses = st.sampled_from(ORDER_STATUSES)

# 임의 문자열 상태 (유효/무효 혼합 검증용)
any_status_strings = st.text(max_size=10)


@st.composite
def history_payloads(draw):
    """OrderHistory payload 형태의 주문 스냅샷 생성 (round-trip 검증용)."""
    items = draw(st.lists(
        st.fixed_dictionaries({
            "menu_name": menu_names,
            "unit_price": prices,
            "quantity": quantities,
        }),
        min_size=1, max_size=10,
    ))
    total = sum(it["unit_price"] * it["quantity"] for it in items)
    return {
        "order_number": draw(st.integers(min_value=1, max_value=9999)),
        "status": draw(valid_statuses),
        "total_amount": total,
        "items": items,
        "created_at": "2026-05-29T10:00:00",
    }
