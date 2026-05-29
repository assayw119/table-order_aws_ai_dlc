# 컴포넌트 메서드 (Component Methods)

각 백엔드 컴포넌트의 메서드 시그니처와 입출력 타입을 정의합니다. 상세 비즈니스 규칙은 Functional Design 단계에서 정의합니다.

> 표기: 메서드는 REST 엔드포인트 핸들러 또는 헬퍼 함수 수준으로 기술합니다. 타입은 Pydantic 스키마(`*Request`, `*Response`)를 가정합니다.

---

## C-BE-1: AuthRouter (인증)

| 메서드 / 엔드포인트 | 목적 | 입력 | 출력 |
|---|---|---|---|
| `POST /api/auth/admin/login` | 관리자 로그인 | `AdminLoginRequest{store_code, username, password}` | `TokenResponse{access_token, expires_at, store}` |
| `POST /api/auth/table/login` | 테이블 태블릿 로그인 | `TableLoginRequest{store_code, table_number, table_password}` | `TableTokenResponse{access_token, table_id, table_number}` |
| `get_current_admin()` (의존성) | JWT 검증 → 관리자 컨텍스트 | `Authorization: Bearer` | `AdminContext{store_id, username}` |
| `get_current_table()` (의존성) | 테이블 토큰 검증 | `Authorization: Bearer` | `TableContext{store_id, table_id}` |
| `_check_login_attempts(key)` (헬퍼) | 로그인 시도 제한 | `key:str` | `bool` |

## C-BE-2: MenuRouter (메뉴)

| 메서드 / 엔드포인트 | 목적 | 입력 | 출력 |
|---|---|---|---|
| `GET /api/menu/categories` | 카테고리 목록 | - | `list[CategoryResponse]` |
| `GET /api/menu/items` | 카테고리별 메뉴 조회 | `category_id?: int` | `list[MenuItemResponse]` |
| `POST /api/admin/menu/items` | 메뉴 등록 | `MenuItemCreateRequest`, admin | `MenuItemResponse` |
| `PUT /api/admin/menu/items/{id}` | 메뉴 수정 | `MenuItemUpdateRequest`, admin | `MenuItemResponse` |
| `DELETE /api/admin/menu/items/{id}` | 메뉴 삭제 | `id:int`, admin | `204` |
| `PUT /api/admin/menu/items/{id}/order` | 노출 순서 조정 | `DisplayOrderRequest`, admin | `MenuItemResponse` |

## C-BE-3: OrderRouter (주문)

| 메서드 / 엔드포인트 | 목적 | 입력 | 출력 |
|---|---|---|---|
| `POST /api/orders` | 주문 생성(고객) | `OrderCreateRequest{items[]}`, table | `OrderResponse{order_number, ...}` |
| `GET /api/orders/current` | 현재 세션 주문 내역(고객) | table ctx, `page?` | `list[OrderResponse]` |
| `GET /api/admin/orders` | 매장 전체 현재 주문(관리자) | admin, `table_number?` | `list[OrderResponse]` |
| `PATCH /api/admin/orders/{id}/status` | 주문 상태 변경 | `OrderStatusRequest{status}`, admin | `OrderResponse` |
| `DELETE /api/admin/orders/{id}` | 주문 삭제(직권) | `id:int`, admin | `204` |
| `_calc_total(items)` (헬퍼) | 총액 계산 | `items` | `Decimal` |
| `_next_order_number(store_id)` (헬퍼) | 일자별 순번 발급 | `store_id` | `int` |

## C-BE-4: TableRouter (테이블/세션)

| 메서드 / 엔드포인트 | 목적 | 입력 | 출력 |
|---|---|---|---|
| `POST /api/admin/tables/setup` | 테이블 초기 설정 | `TableSetupRequest{table_number, table_password}`, admin | `TableResponse` |
| `GET /api/admin/tables` | 테이블별 현재 주문/총액 집계 | admin | `list[TableSummaryResponse]` |
| `POST /api/admin/tables/{id}/checkout` | 이용 완료(세션 종료) | `id:int`, admin | `CheckoutResponse` |
| `GET /api/admin/tables/{id}/history` | 과거 주문 내역 조회 | `id:int`, `date_from?`, `date_to?`, admin | `list[OrderHistoryResponse]` |
| `_ensure_active_session(table_id)` (헬퍼) | 첫 주문 시 세션 시작 보장 | `table_id` | `TableSession` |
| `_archive_session(session_id)` (헬퍼) | 세션 주문 → OrderHistory 이동 | `session_id` | `None` |

## C-BE-5 / C-BE-6: SSERouter & EventBus (실시간)

| 메서드 / 엔드포인트 | 목적 | 입력 | 출력 |
|---|---|---|---|
| `GET /api/admin/stream` | 관리자 매장 전체 이벤트 스트림 | admin(토큰 쿼리/헤더) | `EventSourceResponse` |
| `GET /api/table/stream` | 고객 테이블 세션 이벤트 스트림 | table ctx | `EventSourceResponse` |
| `EventBus.publish(topic, event)` | 이벤트 발행 | `topic:str`, `event:dict` | `None` |
| `EventBus.subscribe(topic)` | 구독(async generator) | `topic:str` | `AsyncIterator[dict]` |
| `EventBus.unsubscribe(topic, q)` | 구독 해제 | `topic`, `queue` | `None` |

토픽 규칙: `store:{store_id}` (관리자), `table:{table_id}` (고객).
이벤트 타입: `order_created`, `order_status_changed`, `order_deleted`, `session_closed`.

## C-BE-7: Database

| 메서드 | 목적 | 입력 | 출력 |
|---|---|---|---|
| `get_session()` (의존성) | DB 세션 제공 | - | `Session` |
| `init_db()` | 스키마 생성 | - | `None` |

ORM 모델: `Store, AdminUser, Table, TableSession, Category, MenuItem, Order, OrderItem, OrderHistory`.

## C-BE-9: Seed

| 메서드 | 목적 | 입력 | 출력 |
|---|---|---|---|
| `run_seed()` | 샘플 데이터 삽입 | - | `None` |

---

## 프론트엔드 공통 모듈 메서드 (요약)

### C-FE-4a: ApiClient
- `get(path, opts)`, `post(path, body)`, `put`, `patch`, `del` — 토큰 자동 첨부, 에러 정규화

### C-FE-4b: SseClient
- `connect(url, onEvent, onError)` — EventSource 연결
- `disconnect()` — 연결 해제
- 자동 재연결(지수 백오프)

### C-FE-4c: AuthStore
- `saveAdminToken(token)`, `getAdminToken()`, `clearAdmin()`
- `saveTableCreds(creds)`, `getTableCreds()` — localStorage

### C-FE-4d: CartStore
- `addItem(menuItem)`, `removeItem(id)`, `setQty(id, qty)`, `clear()`, `getTotal()` — localStorage 동기화
