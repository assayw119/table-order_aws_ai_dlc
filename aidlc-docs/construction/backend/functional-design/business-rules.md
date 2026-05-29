# 비즈니스 규칙 (Business Rules) - UoW-1 Backend

## 인증 규칙 (Auth)
- **BR-AUTH-1**: 관리자 로그인은 (store_code, username, password) 일치 + bcrypt 검증 성공 시에만 허용.
- **BR-AUTH-2**: 관리자 JWT는 발급 후 16시간(57600초) 유효. 만료 토큰은 401 거부.
- **BR-AUTH-3**: 테이블 로그인은 (store_code, table_number, table_password) 검증. 테이블 비밀번호 미설정 시 로그인 불가.
- **BR-AUTH-4**: 비밀번호는 평문 저장 금지. bcrypt 해시만 저장.
- **BR-AUTH-5**: 로그인 시도 제한 — 동일 키(store_code+username 또는 IP) 기준 5회 연속 실패 시 일정 시간(예: 5분) 차단.
- **BR-AUTH-6**: 인증이 필요한 모든 관리자/테이블 API는 유효 토큰 없이 접근 시 401.

## 메뉴 규칙 (Menu)
- **BR-MENU-1**: 메뉴 등록/수정 시 name 필수, price는 0 이상 정수.
- **BR-MENU-2**: 메뉴는 category에 속해야 함(category_id 유효성 검증).
- **BR-MENU-3**: 고객용 조회는 is_available=true 메뉴만 노출. 관리자 조회는 전체.
- **BR-MENU-4**: 메뉴/카테고리는 display_order 오름차순 정렬.
- **BR-MENU-5**: 메뉴 삭제 시 기존 주문 항목의 스냅샷(menu_name, unit_price)은 보존(OrderItem은 영향 없음).

## 주문 규칙 (Order)
- **BR-ORDER-1**: 주문 생성 시 최소 1개 이상의 항목 필요. 각 항목 quantity >= 1.
- **BR-ORDER-2**: 주문 항목의 unit_price/menu_name은 주문 시점 메뉴 값으로 스냅샷 저장.
- **BR-ORDER-3**: total_amount = Σ(unit_price × quantity). 음수 불가.
- **BR-ORDER-4 (세션 보장)**: 주문 생성 시 테이블에 active 세션이 없으면 새 세션을 시작(started_at=now, status=active)하고 테이블 current_session_id 설정. active 세션이 있으면 재사용.
- **BR-ORDER-5 (주문번호)**: order_number는 매장 단위 + 당일(order_date) 기준 1부터 증가. 자정 경과(다른 order_date) 시 1로 리셋.
- **BR-ORDER-6**: 신규 주문 상태 초기값은 '대기중'.
- **BR-ORDER-7 (상태 전이)**: 상태는 '대기중' → '준비중' → '완료' 순으로 진행. 관리자는 임의 단계로 변경 가능하나 허용 값은 3개로 제한.
- **BR-ORDER-8 (주문 삭제)**: 관리자 직권 삭제 시 해당 주문 제거 후 테이블 총 주문액 재계산. 삭제는 active 세션의 주문에만 적용.
- **BR-ORDER-9**: 주문 생성/상태변경/삭제 발생 시 실시간 이벤트를 store 토픽과 table 토픽으로 발행.

## 테이블/세션 규칙 (Table & Session)
- **BR-TBL-1**: 테이블 초기 설정 시 table_number와 table_password(해시) 저장. 재설정 가능.
- **BR-TBL-2 (현재 주문 집계)**: 테이블의 현재 주문/총액은 active 세션의 Order만 집계. closed 세션은 제외.
- **BR-TBL-3 (이용 완료)**: 이용 완료 처리 시:
  1. active 세션의 모든 Order를 OrderHistory로 스냅샷 이동(completed_at=now 기록).
  2. 해당 Order/OrderItem을 현재 주문에서 제거.
  3. 세션 status='closed', closed_at=now.
  4. 테이블 current_session_id=null로 리셋(현재 주문/총액 0).
  5. session_closed 이벤트 발행.
- **BR-TBL-4**: 이용 완료 후 동일 테이블의 다음 주문은 새 세션을 시작(이전 내역과 분리).
- **BR-TBL-5 (과거 내역)**: 과거 내역 조회는 OrderHistory에서 completed_at 역순. 날짜 필터(date_from/date_to) 적용 가능.

## 실시간 규칙 (Realtime/SSE)
- **BR-RT-1**: 관리자 스트림은 `store:{store_id}` 토픽 구독, 고객 스트림은 `table:{table_id}` 토픽 구독.
- **BR-RT-2**: 이벤트 타입: order_created, order_status_changed, order_deleted, session_closed.
- **BR-RT-3**: 신규 주문 이벤트는 발생 후 2초 이내 구독자에게 전달(NFR-1).
- **BR-RT-4**: 연결 종료 시 구독 정리(메모리 누수 방지).

## 검증/에러 규칙 (Validation & Errors)
- **BR-ERR-1**: 요청 스키마 검증 실패 시 422(Pydantic) 반환.
- **BR-ERR-2**: 존재하지 않는 리소스 접근 시 404.
- **BR-ERR-3**: 권한 없는 접근 시 401/403.
- **BR-ERR-4**: 주문 생성 실패 시 부분 저장 금지(트랜잭션 롤백).
