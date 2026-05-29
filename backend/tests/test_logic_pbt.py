"""순수 로직 헬퍼에 대한 속성 기반 테스트 (PBT).

적용 규칙(PBT Partial): PBT-02(round-trip), PBT-03(invariant),
PBT-07(generator), PBT-08(shrinking/seed).
shrinking은 Hypothesis 기본값으로 활성, seed는 실패 시 자동 출력된다.
"""
from hypothesis import given, strategies as st

from app.core.logic import (
    calc_total, next_order_number, is_valid_status,
    serialize_order_to_history, deserialize_history_payload,
)
from app.core.security import create_token, decode_token
from tests.generators import (
    order_lines, non_empty_order_lines, valid_statuses, any_status_strings,
    history_payloads,
)
from app.core.config import ORDER_STATUSES

# 재사용 전략
order_numbers_lists = st.lists(st.integers(min_value=1, max_value=9999), max_size=50)
ids = st.integers(min_value=1, max_value=10000)


# ---------- P1: calc_total 불변식 (PBT-03) ----------
@given(items=order_lines)
def test_calc_total_non_negative(items):
    """모든 가격/수량이 0 이상이면 총액은 0 이상 (P1)."""
    assert calc_total(items) >= 0


@given(items=non_empty_order_lines)
def test_calc_total_matches_sum(items):
    """총액은 각 항목 소계의 합과 정확히 일치 (P1, oracle)."""
    expected = sum(p * q for p, q in items)
    assert calc_total(items) == expected


@given(items=order_lines)
def test_calc_total_additive(items):
    """항목 하나를 추가하면 총액은 그 항목 소계만큼 증가 (구조적 귀납)."""
    base = calc_total(items)
    extra = (500, 2)
    assert calc_total(list(items) + [extra]) == base + 500 * 2


# ---------- P2: next_order_number 불변식 (PBT-03) ----------
@given(nums=order_numbers_lists)
def test_next_order_number_invariant(nums):
    """다음 번호는 항상 1 이상이며, 기존 집합보다 큼 (P2)."""
    result = next_order_number(nums)
    assert result >= 1
    if nums:
        assert result == max(nums) + 1
        assert result not in nums
    else:
        assert result == 1


# ---------- P3: history 직렬화 round-trip (PBT-02) ----------
@given(payload=history_payloads())
def test_history_serialize_roundtrip(payload):
    """직렬화 후 역직렬화하면 항목과 총액이 보존됨 (P3)."""
    serialized = serialize_order_to_history(payload)
    restored = deserialize_history_payload(serialized)
    assert restored["total_amount"] == payload["total_amount"]
    assert restored["items"] == payload["items"]
    assert restored["order_number"] == payload["order_number"]


# ---------- P4: JWT round-trip (PBT-02) ----------
@given(store_id=ids, table_id=ids)
def test_jwt_roundtrip(store_id, table_id):
    """decode(encode(claims)) == claims (만료 미경과 시) (P4)."""
    claims = {"store_id": store_id, "table_id": table_id, "role": "table"}
    token = create_token(claims, ttl_seconds=3600)
    decoded = decode_token(token)
    assert decoded["store_id"] == store_id
    assert decoded["table_id"] == table_id
    assert decoded["role"] == "table"


# ---------- P5: status 검증 불변식 (PBT-03) ----------
@given(status=valid_statuses)
def test_valid_status_accepts_allowed(status):
    """허용 집합의 상태는 항상 valid (P5)."""
    assert is_valid_status(status) is True


@given(status=any_status_strings)
def test_valid_status_only_for_allowed(status):
    """is_valid_status는 입력이 허용 집합에 속할 때만 True (P5)."""
    assert is_valid_status(status) == (status in ORDER_STATUSES)
