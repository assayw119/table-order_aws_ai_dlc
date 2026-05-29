# 통합 테스트 지침 (Integration Test)

## 종단간(E2E) 스모크 테스트

백엔드와 SSE 실시간 흐름을 실제 HTTP로 검증한다 (UoW-1 ↔ UoW-2 API 계약).

### 사전 조건
1. 백엔드 서버 실행 + seed 완료
```bash
cd backend
source .venv/bin/activate
python -m app.seed
uvicorn app.main:app --port 8000   # 별도 터미널
```

### 실행
```bash
cd backend
.venv/bin/python -m tests.e2e_smoke
```

### 검증 시나리오 (13개)
1. health 200
2. 관리자 로그인 / 테이블 로그인
3. 메뉴 조회
4. 주문 생성(총액 정확성)
5. **관리자 SSE로 order_created 수신** (UoW-1 ↔ UoW-2 실시간 계약)
6. **SSE 2초 이내 전달** (NFR-P1)
7. 주문 상태 변경
8. 현재 세션 주문 조회
9. 이용 완료(checkout) → 과거 이력 이동
10. 이용 완료 후 현재 세션 리셋
11. 과거 내역 조회

### 기대 결과
- `E2E 결과: 13/13 passed`

## 유닛 간 통합 포인트
- **계약**: 프론트엔드는 백엔드 REST(JSON) + SSE(event-stream)에 의존.
- **인증**: 프론트가 발급받은 JWT/테이블 토큰을 헤더(REST)·쿼리(SSE)로 전달.
- **실시간**: 주문 변경 시 백엔드 EventBus → SSE → 프론트 화면 자동 갱신.

## 프론트엔드-백엔드 수동 통합 확인
1. 백엔드/프론트 실행
2. 관리자 대시보드 열기 → 다른 탭에서 고객 주문 생성 → 대시보드에 2초 내 표시 + 신규 강조 확인
3. 대시보드에서 상태 변경 → 고객 주문내역 화면에서 상태 실시간 갱신 확인
4. 이용 완료 → 카드 리셋 + 과거 내역 이동 확인
