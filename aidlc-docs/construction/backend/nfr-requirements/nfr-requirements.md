# NFR 요구사항 (NFR Requirements) - UoW-1 Backend

## 성능 (Performance)
- **NFR-P1**: 신규 주문 이벤트는 발생 후 2초 이내에 관리자/고객 SSE 구독자에게 전달.
- **NFR-P2**: 일반 REST 응답은 로컬 환경에서 체감 즉시(수십~수백 ms). SQLite 단일 파일 기준.
- **NFR-P3**: 동시 접속 규모는 단일 매장 수준(수~수십 테이블 + 1 관리자)으로 가정.

## 확장성 (Scalability)
- **NFR-S1**: 단일 프로세스/단일 머신 전제. EventBus는 인메모리. 다중 워커/수평 확장은 범위 외(문서화).
- **NFR-S2**: SQLite 동시 쓰기 제약을 고려해 짧은 트랜잭션 사용.

## 가용성 (Availability)
- **NFR-A1**: 로컬 데모/개발 수준. 고가용성·장애 복구는 범위 외.
- **NFR-A2**: SSE 연결 끊김 시 클라이언트 자동 재연결로 복원(프론트 책임, US-T1).

## 보안 (Security)
- **NFR-SEC1**: 비밀번호 bcrypt 해싱(BR-AUTH-4).
- **NFR-SEC2**: 관리자 JWT 16시간, 서명 검증(BR-AUTH-2).
- **NFR-SEC3**: 로그인 시도 제한(BR-AUTH-5).
- **NFR-SEC4**: 인증 필요한 API 토큰 검증(BR-AUTH-6).
- 참고: Security Baseline 확장은 미적용(Q7=B). 위 항목은 기능 요구사항 수준으로 구현.

## 신뢰성 (Reliability)
- **NFR-R1**: 주문 생성은 트랜잭션 처리(부분 저장 방지, BR-ERR-4).
- **NFR-R2**: 이용 완료 처리(history 이동 + 삭제 + 세션 종료)는 트랜잭션으로 원자성 보장.

## 유지보수성 / 테스트 (Maintainability & Test)
- **NFR-M1**: PBT Partial 적용 — 순수 함수/직렬화 중심 속성 테스트(PBT-02/03/07/08/09).
- **NFR-M2**: 단위 테스트 + 통합 테스트(API 레벨) 작성.
- **NFR-M3**: 모듈 분리(core/auth/menu/orders/tables/realtime)로 응집도 유지.

## CORS / 통합
- **NFR-I1**: 프론트엔드(다른 포트)에서의 호출을 위해 CORS 허용 설정 필요.
