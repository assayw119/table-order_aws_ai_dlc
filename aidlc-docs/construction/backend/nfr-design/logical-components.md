# 논리 컴포넌트 (Logical Components) - UoW-1 Backend

## 인프라성 논리 컴포넌트

| 컴포넌트 | 역할 | 구현 방식 |
|---|---|---|
| EventBus | 인메모리 pub/sub 허브 | `dict[topic, set[asyncio.Queue]]`, publish/subscribe/unsubscribe |
| SSE Streamer | 구독 큐 → text/event-stream | sse-starlette `EventSourceResponse` + async generator |
| JWT Provider | 토큰 발급/검증 | python-jose, 비밀키(config), exp 클레임 |
| Password Hasher | 해싱/검증 | passlib bcrypt |
| LoginThrottle | 시도 제한 카운터 | 인메모리 dict{key: (fail_count, locked_until)} |
| DB Session Factory | 요청 스코프 세션 | SQLAlchemy sessionmaker + FastAPI Depends |

## 컴포넌트 배치(모듈 매핑)
- `core/database.py` → DB Session Factory, 엔진
- `core/models.py` → ORM 엔티티
- `core/security.py` → JWT Provider, Password Hasher, LoginThrottle, 인증 의존성
- `core/config.py` → 설정(비밀키, 토큰 만료, DB URL, CORS origins)
- `realtime/event_bus.py` → EventBus
- `realtime/router.py` → SSE Streamer 엔드포인트

## 이벤트 스키마(논리)
```
{
  "type": "order_created" | "order_status_changed" | "order_deleted" | "session_closed",
  "table_id": int,
  "table_number": int,
  "order": { ... } | null,
  "ts": ISO8601
}
```

## 비기능 ↔ 컴포넌트 추적
- NFR-P1 → EventBus + SSE Streamer
- NFR-SEC1~4 → JWT Provider, Password Hasher, LoginThrottle, 인증 의존성
- NFR-R1/R2 → DB Session Factory(트랜잭션)
- NFR-I1 → CORSMiddleware(main.py)
