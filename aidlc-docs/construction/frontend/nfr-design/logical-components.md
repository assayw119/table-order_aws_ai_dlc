# 논리 컴포넌트 (Logical Components) - UoW-2 Frontend

| 컴포넌트 | 역할 | 구현 |
|---|---|---|
| ApiClient | REST 호출 래퍼 | fetch 기반, 토큰 첨부, 에러 정규화 |
| useSse 훅 | SSE 구독/재연결 | EventSource + useEffect 정리 |
| AuthStore | 토큰/자격증명 저장 | localStorage 모듈 |
| CartStore | 장바구니 상태 | localStorage 모듈 + 총액 계산(순수 함수) |
| RouteGuard | 인증 가드 | react-router 래퍼 컴포넌트 |
| Toast/ErrorBanner | 피드백 표시 | 경량 컴포넌트 |

## 비기능 ↔ 컴포넌트 추적
- FE-NFR-P1, R1 → useSse 훅(푸시/재연결)
- FE-NFR-S1 → CartStore, AuthStore(localStorage)
- FE-NFR-SEC1 → ApiClient(토큰 첨부), RouteGuard
- FE-NFR-U1~3 → CSS(터치 타깃), CustomerLayout
- FE-NFR-M1 → CartStore 순수 총액 계산(단위 테스트 대상)

## 클라이언트 순수 로직 (테스트 대상)
- `calcCartTotal(items)` = Σ(price × qty) — 단위 테스트로 검증(백엔드 calc_total과 일관).
