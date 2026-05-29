# 코드 생성 요약 - UoW-1 Backend

## 생성된 파일 (워크스페이스 `backend/`)

### 설정/패키지
- `requirements.txt` — 의존성(FastAPI, SQLAlchemy, Pydantic, JWT, bcrypt, sse-starlette, pytest, Hypothesis)
- `.gitignore`, `README.md`
- `app/__init__.py`

### core 모듈
- `app/core/config.py` — 설정(JWT, TTL, DB URL, CORS, 주문 상태)
- `app/core/database.py` — 엔진/세션/Base/init_db
- `app/core/models.py` — 9개 ORM 모델
- `app/core/security.py` — bcrypt 해싱, JWT 발급/검증, 로그인 시도 제한, 인증 의존성
- `app/core/schemas.py` — Pydantic 요청/응답 스키마
- `app/core/logic.py` — 순수 헬퍼(calc_total, next_order_number, is_valid_status, serialize/deserialize history) — PBT 대상

### 기능 모듈
- `app/auth/router.py` — 관리자/테이블 로그인 (US-A1, US-C1, US-T2)
- `app/menu/router.py` — 메뉴 조회/CRUD (US-C2, US-A4)
- `app/orders/router.py` — 주문 생성/조회/상태변경/삭제 + 이벤트 발행 (US-C4, US-C5, US-A2)
- `app/tables/router.py` + `session_helpers.py` — 테이블 설정/집계/이용완료/과거내역 (US-A3)
- `app/realtime/event_bus.py` + `router.py` — EventBus + SSE 스트림 (US-T1)
- `app/main.py` — 앱 조립, CORS, 라우터 등록
- `app/seed.py` — 데모 시드 데이터

### 테스트
- `tests/generators.py` — 도메인 제너레이터(PBT-07)
- `tests/test_logic_pbt.py` — 속성 기반 테스트(PBT-02/03/07/08): P1~P5
- `tests/conftest.py` — 격리 인메모리 DB + TestClient 픽스처
- `tests/test_api_integration.py` — API 통합 테스트(예시 기반, PBT-10 보완)

## 검증 결과
- 앱 임포트/라우트 등록 정상
- `pytest`: **24 passed** (PBT 8 + 통합 16), 15.7초
- seed 스크립트 정상 실행

## 스토리 구현 매핑
US-C1, US-C2, US-C4, US-C5, US-A1, US-A2, US-A3, US-A4, US-T1, US-T2 → 구현 완료 (백엔드 측)

## PBT 컴플라이언스 (Partial 모드)
- PBT-02 (round-trip): history 직렬화, JWT — 충족
- PBT-03 (invariant): calc_total, next_order_number, status 검증 — 충족
- PBT-07 (generator): 도메인 제너레이터 `tests/generators.py` — 충족
- PBT-08 (shrinking/seed): Hypothesis 기본 활성 — 충족
- PBT-09 (framework): Hypothesis 의존성 추가 — 충족
- PBT-05, PBT-06 등: 해당 없음(N/A) — 단순 CRUD/순수 함수 범위
