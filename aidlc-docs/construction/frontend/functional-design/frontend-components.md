# 프론트엔드 컴포넌트 설계 (Frontend Components) - UoW-2

단일 React 앱. 라우팅으로 고객(`/customer`)·관리자(`/admin`) 영역 분리.

## 라우팅 구조
```
/                         → /customer 로 리다이렉트
/customer                 → 자동 로그인 가드 → 메뉴 화면(기본)
/customer/setup           → 테이블 초기 설정(미로그인 시)
/customer/cart            → 장바구니
/customer/orders          → 현재 세션 주문 내역
/admin                    → 로그인 가드 → 대시보드
/admin/login              → 매장 로그인
/admin/dashboard          → 실시간 주문 모니터링(기본)
/admin/tables             → 테이블 관리
/admin/menu               → 메뉴 관리
```

## 공통 모듈

### ApiClient (`src/api/client.js`)
- `request(method, path, {body, token})` → fetch 래퍼, JSON, 에러 정규화
- `get/post/put/patch/del` 단축 메서드
- 401 응답 시 토큰 무효화 콜백

### SseClient (`src/api/sse.js`)
- `connect(path, token, onEvent)` → EventSource (토큰은 쿼리 파라미터로 전달)
- 자동 재연결(지수 백오프), `disconnect()`
- 이벤트 타입별 콜백 분기(order_created/order_status_changed/order_deleted/session_closed)

### AuthStore (`src/store/auth.js`) — localStorage
- 관리자: `saveAdminToken/getAdminToken/clearAdmin`
- 테이블: `saveTableCreds/getTableCreds/clearTable` (store_code, table_number, table_password, token)

### CartStore (`src/store/cart.js`) — localStorage
- `getItems/addItem/removeItem/setQty/clear/getTotal`
- 페이지 새로고침 시 유지 (BR: 클라이언트 로컬 저장)

## 고객 영역 컴포넌트

| 컴포넌트 | props/state | 인터랙션 | API |
|---|---|---|---|
| TableLoginSetup | state: storeCode, tableNumber, password | 입력→로그인→localStorage 저장 | POST /api/auth/table/login |
| CustomerLayout | state: 자동 로그인 여부 | 하단 탭(메뉴/장바구니/주문내역) | - |
| MenuView | state: categories, items, activeCategory | 카테고리 전환, 메뉴 담기 | GET /api/menu/categories, /api/menu/items |
| MenuCard | props: item, onAdd | 추가 버튼 | - |
| CartView | state: cartItems(local) | 수량 증감/삭제/비우기/주문 | (주문은 OrderConfirm) |
| OrderConfirm | state: submitting, result | 주문 확정→성공 시 5초 후 메뉴 리다이렉트 | POST /api/orders |
| OrderHistoryView | state: orders, sse | SSE 실시간 상태 갱신 | GET /api/orders/current, SSE /api/table/stream |

### 고객 주문 플로우
1. MenuView에서 메뉴 담기 → CartStore 저장(로컬, 총액 실시간)
2. CartView에서 수량 조절 → 주문 확정
3. OrderConfirm: POST /api/orders → 성공 시 주문번호 표시, 장바구니 비우기, 5초 후 메뉴로 이동
4. 실패 시 에러 표시, 장바구니 유지

## 관리자 영역 컴포넌트

| 컴포넌트 | props/state | 인터랙션 | API |
|---|---|---|---|
| AdminLogin | state: storeCode, username, password | 로그인→JWT 저장 | POST /api/auth/admin/login |
| AdminLayout | state: 인증 여부 | 사이드 탭(대시보드/테이블/메뉴) | - |
| OrderDashboard | state: tables[], sse, newOrderIds | SSE 실시간, 카드 클릭 상세, 상태 변경 | GET /api/admin/tables, SSE /api/admin/stream, PATCH status |
| TableCard | props: table, onClick | 총액/최신주문 미리보기, 신규 강조 | - |
| OrderDetailModal | props: order, onStatusChange, onDelete | 상태 변경/삭제 | PATCH status, DELETE order |
| TableManagement | state: tables[] | 초기 설정, 이용 완료, 과거 내역 | POST setup, POST checkout, GET history |
| HistoryModal | props: tableId | 날짜 필터, 과거 주문 목록 | GET /api/admin/tables/{id}/history |
| MenuManagement | state: items[], editing | 등록/수정/삭제/순서 | menu admin API |

### 관리자 실시간 플로우
1. 로그인 → 대시보드 진입 → GET /api/admin/tables 초기 로드
2. SSE /api/admin/stream 구독
3. order_created 수신 → 해당 테이블 카드 갱신 + 신규 강조(애니메이션)
4. 상태 변경/삭제 → PATCH/DELETE → 이벤트로 화면 자동 갱신
5. 이용 완료 → POST checkout → session_closed 이벤트 → 카드 리셋

## 폼 검증 규칙
- 로그인: 모든 필드 필수
- 테이블 설정: table_number(양의 정수), password 필수
- 메뉴 등록/수정: name 필수, price >= 0
- 주문: 장바구니 비어있으면 주문 버튼 비활성

## 자동화 친화 (data-testid)
- 주요 인터랙션 요소에 `data-testid` 부여: 예) `table-login-submit`, `menu-card-add-{id}`, `cart-checkout-button`, `admin-login-submit`, `order-status-{status}`, `table-checkout-{id}`
