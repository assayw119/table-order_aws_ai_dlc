# NFR 설계 패턴 (NFR Design Patterns) - UoW-1 Backend

## 실시간 전달 패턴 (Performance/Realtime)
- **Publish-Subscribe (인메모리)**: EventBus가 토픽별 `asyncio.Queue` 구독자 목록을 관리. 변경 발생 시 publish가 각 큐에 즉시 push → SSE 핸들러가 큐에서 await하여 스트리밍. 폴링 대비 지연 최소화로 NFR-P1(2초 이내) 충족.
- **토픽 분리**: `store:{id}`(관리자), `table:{id}`(고객)로 구독 범위 최소화 → 불필요한 브로드캐스트 방지.
- **하트비트(keep-alive)**: 일정 주기(예: 15초) 코멘트 이벤트 전송으로 프록시 타임아웃/끊김 감지.

## 인증/보안 패턴 (Security)
- **JWT 검증 의존성**: FastAPI `Depends`로 토큰 디코드 → 컨텍스트 주입. 라우터마다 재사용.
- **비밀번호 해싱**: passlib bcrypt. 검증은 `verify`, 저장은 `hash`.
- **로그인 시도 제한**: 인메모리 카운터(키별 실패 횟수 + 잠금 만료 시각). 단일 프로세스 전제.

## 트랜잭션/신뢰성 패턴 (Reliability)
- **Unit of Work(트랜잭션)**: 주문 생성, 이용 완료 처리는 단일 DB 트랜잭션으로 commit/rollback. 예외 시 전체 롤백(NFR-R1, R2).
- **멱등 처리**: 이용 완료가 이미 종료된 세션에 호출되면 변화 없이 성공 응답.

## 데이터 접근 패턴
- **짧은 트랜잭션**: SQLite 쓰기 잠금 시간을 줄이기 위해 요청 단위 세션 + 빠른 커밋(NFR-S2).
- **요청 스코프 세션**: `Depends(get_session)`로 요청당 세션 생성/종료.

## CORS 패턴
- **CORSMiddleware**: 개발 환경에서 프론트엔드 origin 허용(NFR-I1).

## 에러 처리 패턴
- **계층적 예외 → HTTP 매핑**: 검증 실패 422(Pydantic 자동), 미존재 404, 인증 401/403, 서버 오류 500.
