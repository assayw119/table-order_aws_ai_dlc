# 스토리 → 유닛 매핑 (Unit of Work Story Map)

각 사용자 스토리가 어떤 유닛에서 구현되는지 매핑합니다. 대부분의 스토리는 백엔드(API/로직)와 프론트엔드(UI) 양쪽에 걸치므로, 유닛별로 담당 부분을 표기합니다.

## 매핑 표

| 스토리 | UoW-1 Backend | UoW-2 Frontend |
|---|---|---|
| US-C1 테이블 자동 로그인/세션 | 테이블 로그인 API, 토큰 발급 | TableLoginSetup 화면, AuthStore(localStorage) |
| US-C2 메뉴 조회 | 메뉴/카테고리 조회 API | MenuView |
| US-C3 장바구니 | (없음 - 클라이언트 전용) | CartView, CartStore(localStorage) |
| US-C4 주문 생성 | 주문 생성 API(번호 발급/총액/세션 보장) | OrderConfirm(성공·5초 리다이렉트) |
| US-C5 주문 내역 조회 | 현재 세션 주문 조회 API + 고객 SSE | OrderHistoryView, SseClient |
| US-A1 매장 인증 | 관리자 로그인 API(JWT 16h, bcrypt, 시도 제한) | AdminLogin, AuthStore |
| US-A2 실시간 모니터링 | 매장 주문 조회 API, 상태 변경 API, 관리자 SSE | OrderDashboard, SseClient |
| US-A3 테이블 관리 | 테이블 설정/집계/이용완료/과거내역 API, 주문 삭제 API | TableManagement |
| US-A4 메뉴 관리 | 메뉴 CRUD/순서 API | MenuManagement |
| US-T1 SSE 실시간 인프라 | EventBus + SSE 엔드포인트(관리자/고객) | SseClient(연결/재연결) |
| US-T2 인증/세션 인프라 | JWT/bcrypt, 토큰 검증 의존성 | AuthStore, ApiClient(토큰 첨부) |

## 유닛별 스토리 커버리지

### UoW-1 Backend
- 직접 구현: US-C1, US-C2, US-C4, US-C5, US-A1, US-A2, US-A3, US-A4, US-T1, US-T2
- 해당 없음: US-C3(장바구니, 클라이언트 전용)

### UoW-2 Frontend
- 직접 구현: US-C1 ~ US-C5, US-A1 ~ US-A4, US-T1(클라이언트 측), US-T2(클라이언트 측)

## 검증
- [x] 모든 스토리(US-C1~C5, US-A1~A4, US-T1~T2)가 최소 하나의 유닛에 할당됨
- [x] US-C3는 클라이언트 전용으로 Frontend에만 할당(백엔드 N/A 명시)
- [x] 교차 관심사(US-T1, US-T2)는 양 유닛에 적절히 분배됨
