# 테이블오더 백엔드 (UoW-1)

FastAPI + SQLite 기반 테이블오더 서버. REST API + SSE 실시간 스트림.

## 요구 사항
- Python 3.11+

## 설치 및 실행

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 데모 데이터 생성
python -m app.seed

# 서버 실행
uvicorn app.main:app --reload --port 8000
```

API 문서: http://localhost:8000/docs

## 데모 자격 증명 (seed)
- 매장 식별자: `store001`
- 관리자: `admin` / `admin1234`
- 테이블: 1~6번, 비밀번호 `table1234`

## 테스트

```bash
source .venv/bin/activate
python -m pytest -q
```

- 단위/속성 기반 테스트(PBT, Hypothesis): `tests/test_logic_pbt.py`
- API 통합 테스트: `tests/test_api_integration.py`

## 모듈 구조
- `app/core` — DB, 모델, 보안(JWT/bcrypt), 설정, 스키마, 순수 로직 헬퍼
- `app/auth` — 관리자/테이블 인증
- `app/menu` — 메뉴/카테고리 조회·관리
- `app/orders` — 주문 생성/조회/상태변경/삭제
- `app/tables` — 테이블 설정, 세션 라이프사이클, 과거 내역
- `app/realtime` — EventBus(인메모리 pub/sub) + SSE 라우터

## 주요 엔드포인트
- 인증: `POST /api/auth/admin/login`, `POST /api/auth/table/login`
- 메뉴: `GET /api/menu/categories`, `GET /api/menu/items`, `POST|PUT|DELETE /api/admin/menu/items`
- 주문: `POST /api/orders`, `GET /api/orders/current`, `GET /api/admin/orders`, `PATCH /api/admin/orders/{id}/status`, `DELETE /api/admin/orders/{id}`
- 테이블: `POST /api/admin/tables/setup`, `GET /api/admin/tables`, `POST /api/admin/tables/{id}/checkout`, `GET /api/admin/tables/{id}/history`
- 실시간: `GET /api/admin/stream`, `GET /api/table/stream`
