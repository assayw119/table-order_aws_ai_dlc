# 기술 스택 결정 (Tech Stack Decisions) - UoW-1 Backend

| 영역 | 선택 | 근거 |
|---|---|---|
| 언어 | Python 3.11+ | 요구사항 Q1=C |
| 웹 프레임워크 | FastAPI | 요구사항 Q1=C, Pydantic 통합, SSE 용이 |
| ASGI 서버 | Uvicorn | FastAPI 표준 |
| ORM | SQLAlchemy 2.x | SQLite 매핑, 트랜잭션 |
| DB | SQLite | 요구사항 Q3=C, 로컬/경량 |
| 검증 | Pydantic v2 | 요구사항 Q3=A |
| 인증 | python-jose (JWT) + passlib[bcrypt] | JWT 16h, bcrypt 해싱 |
| SSE | sse-starlette (EventSourceResponse) | FastAPI 친화 SSE 스트리밍 |
| 테스트 | pytest + httpx(TestClient) | 단위/통합 테스트 |
| PBT 프레임워크 | **Hypothesis** | PBT-09: Python 표준 PBT, shrinking/seed 지원 |

## PBT-09 준수
- Hypothesis를 `requirements.txt`에 의존성으로 추가.
- 커스텀 제너레이터(양수 가격/수량, 유효 상태)를 테스트 유틸로 정의(PBT-07).
- 기본 shrinking 활성, 실패 시 seed 로깅(PBT-08).

## 주요 의존성 (requirements.txt 예정)
```
fastapi
uvicorn[standard]
sqlalchemy
pydantic
python-jose[cryptography]
passlib[bcrypt]
sse-starlette
pytest
httpx
hypothesis
```
