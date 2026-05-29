# NFR 요구사항 (NFR Requirements) - UoW-2 Frontend

## 성능 (Performance)
- **FE-NFR-P1**: 관리자 대시보드는 SSE 이벤트 수신 후 즉시(체감 1초 이내) 화면 반영.
- **FE-NFR-P2**: 초기 로드는 Vite 번들로 경량 유지.

## 사용성 (Usability)
- **FE-NFR-U1**: 터치 친화 — 주요 버튼 최소 44x44px (요구사항 UI/UX).
- **FE-NFR-U2**: 카드 기반 메뉴 레이아웃, 명확한 시각 계층.
- **FE-NFR-U3**: 고객 화면은 무로그인 즉시 사용(자동 로그인 후 메뉴 기본 표시).

## 신뢰성 (Reliability)
- **FE-NFR-R1**: SSE 연결 끊김 시 자동 재연결(지수 백오프) — US-T1.
- **FE-NFR-R2**: 주문 실패 시 장바구니 보존 + 에러 메시지.

## 상태 지속성 (Persistence)
- **FE-NFR-S1**: 장바구니와 인증 정보는 localStorage에 저장, 새로고침 시 유지.

## 보안 (Security)
- **FE-NFR-SEC1**: 토큰은 localStorage 저장(Q6=A). API 호출 시 Authorization 헤더 첨부.
- 참고: Security Baseline 확장 미적용(Q7=B).

## 유지보수/테스트
- **FE-NFR-M1**: 컴포넌트/공통 모듈 분리. 순수 로직(장바구니 총액)은 단위 테스트.
- **FE-NFR-M2**: 주요 인터랙션 요소에 data-testid 부여(자동화 친화).
