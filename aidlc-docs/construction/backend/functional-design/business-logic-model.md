# 비즈니스 로직 모델 (Business Logic Model) - UoW-1 Backend

## 핵심 워크플로우

### 1. 주문 생성 (POST /api/orders)
```
입력: 테이블 토큰(컨텍스트), items[{menu_item_id, quantity}]
1. 항목 유효성 검증(BR-ORDER-1): 비어있지 않음, quantity>=1
2. 각 menu_item 조회 → menu_name/price 스냅샷(BR-ORDER-2)
3. active 세션 보장(BR-ORDER-4): 없으면 새 세션 생성
4. 당일 주문번호 계산(BR-ORDER-5): max(order_number) WHERE store_id, order_date=today + 1
5. total_amount 계산(BR-ORDER-3) = Σ(unit_price*qty)
6. Order + OrderItem 트랜잭션 저장(BR-ERR-4)
7. order_created 이벤트 발행 → store:{id}, table:{id} (BR-ORDER-9)
8. 응답: {order_number, status, total_amount, items, created_at}
```

### 2. 주문 상태 변경 (PATCH /api/admin/orders/{id}/status)
```
입력: 관리자, status ∈ {대기중,준비중,완료}
1. 주문 조회(404 시 BR-ERR-2)
2. status 허용 값 검증(BR-ORDER-7)
3. UPDATE status
4. order_status_changed 이벤트 발행(store, table)
5. 응답: OrderResponse
```

### 3. 주문 삭제 (DELETE /api/admin/orders/{id})
```
입력: 관리자
1. 주문 조회(404)
2. 삭제(OrderItem cascade)
3. 테이블 총액 재계산(BR-ORDER-8) - active 세션 집계
4. order_deleted 이벤트 발행
5. 204
```

### 4. 테이블 이용 완료 (POST /api/admin/tables/{id}/checkout)
```
입력: 관리자
1. 테이블 + active 세션 조회 (없으면 멱등 처리: 이미 종료된 상태면 변화 없음)
2. active 세션의 Order 목록 조회
3. 각 Order를 OrderHistory로 스냅샷 직렬화 이동(BR-TBL-3): order_payload=items, completed_at=now
4. Order/OrderItem 삭제
5. 세션 status='closed', closed_at=now
6. 테이블 current_session_id=null
7. session_closed 이벤트 발행
8. 응답: {archived_count, table_number}
```

### 5. 테이블 현재 주문 집계 (GET /api/admin/tables)
```
1. 매장 모든 테이블 조회
2. 각 테이블의 active 세션 Order 집계(BR-TBL-2): 주문 목록, Σtotal
3. 응답: [{table_number, session_active, total_amount, orders[]}]
```

### 6. 과거 내역 조회 (GET /api/admin/tables/{id}/history)
```
입력: date_from?, date_to?
1. OrderHistory WHERE table_id [AND completed_at BETWEEN ...]
2. completed_at 역순 정렬(BR-TBL-5)
3. 응답: [OrderHistoryResponse]
```

### 7. 현재 세션 주문 내역 (GET /api/orders/current)
```
입력: 테이블 토큰
1. 테이블 active 세션 확인(없으면 빈 목록)
2. 세션의 Order 조회, created_at 정렬, 페이지네이션
3. 응답: [OrderResponse]
```

## 순수 함수 / 헬퍼 (PBT 대상 식별 - PBT-01)

| 함수 | 설명 | PBT 속성 카테고리 |
|---|---|---|
| `calc_total(items)` | Σ(unit_price×qty) | Invariant (비음수, 항목 합과 일치), Oracle(단순 합산 참조) |
| `next_order_number(existing, today)` | 당일 순번 산출 | Invariant (항상 max+1, 1 이상) |
| `serialize_order_to_history(order)` | Order→OrderHistory payload 직렬화 | Round-trip (payload→복원 시 항목/총액 보존) |
| `validate_status_transition(status)` | 상태 값 허용 검증 | Invariant (허용 집합 내) |
| JWT `encode/decode` | 토큰 직렬화 | Round-trip (decode(encode(claims))=claims) |

## 테스트 가능한 속성 (Testable Properties) - PBT-01

> PBT Partial 모드: PBT-02(round-trip), PBT-03(invariant), PBT-07(generator), PBT-08(shrinking), PBT-09(framework) 강제.

- **P1 (Invariant, BR-ORDER-3)**: 임의의 항목 목록에 대해 `calc_total >= 0`이며, 모든 unit_price·qty가 0 이상이면 결과는 각 항목 소계의 합과 정확히 일치.
- **P2 (Invariant, BR-ORDER-5)**: `next_order_number`는 기존 번호 집합의 max+1(없으면 1)이며 항상 >= 1.
- **P3 (Round-trip, BR-TBL-3)**: 주문을 history payload로 직렬화 후 역직렬화하면 항목 목록과 total_amount가 보존됨.
- **P4 (Round-trip, BR-AUTH-2)**: JWT `decode(encode(claims)) == claims`(만료 미경과 시).
- **P5 (Invariant, BR-ORDER-7)**: `validate_status_transition` 결과는 입력이 허용 집합에 속할 때만 True.

각 속성은 도메인 특화 제너레이터(PBT-07: 양수 가격/수량, 유효 상태 문자열)를 사용하고, Hypothesis(PBT-09)로 shrinking/seed 재현(PBT-08)을 보장합니다.

## 컴포넌트(모듈) 간 상호작용
- `orders` → `tables`(세션 보장 헬퍼), `realtime`(이벤트 발행), `core`(모델/DB)
- `tables` → `realtime`(이벤트), `core`
- `realtime` → (독립) EventBus 인메모리
- `auth`/`menu` → `core`
