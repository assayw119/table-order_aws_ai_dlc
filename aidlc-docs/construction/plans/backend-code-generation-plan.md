# 코드 생성 계획 - UoW-1 Backend

**워크스페이스 루트**: 프로젝트 루트 / **코드 위치**: `backend/`
**프로젝트 유형**: Greenfield 멀티유닛(모놀리식). 애플리케이션 코드는 절대 aidlc-docs/에 두지 않음.

## 유닛 컨텍스트
- 구현 스토리: US-C1(테이블 로그인), US-C2(메뉴 조회), US-C4(주문 생성), US-C5(주문 내역), US-A1(인증), US-A2(모니터링 API), US-A3(테이블 관리), US-A4(메뉴 관리), US-T1(SSE), US-T2(인증/세션)
- 의존성: 없음(기반 유닛)
- 소유 엔티티: Store, AdminUser, Table, TableSession, Category, MenuItem, Order, OrderItem, OrderHistory

## 생성 단계 (체크리스트)

- [x] Step 1: 프로젝트 구조 + requirements.txt + config
- [x] Step 2: core 모듈 (database, models, security)
- [x] Step 3: Pydantic 스키마 + 순수 헬퍼(calc_total, next_order_number, serialize, status validate)
- [x] Step 4: realtime 모듈 (EventBus + SSE 라우터)
- [x] Step 5: auth 라우터
- [x] Step 6: menu 라우터
- [x] Step 7: orders 라우터
- [x] Step 8: tables 라우터
- [x] Step 9: main.py (앱 조립, CORS, 라우터 등록) + seed.py
- [x] Step 10: 단위 테스트 + PBT(Hypothesis) + 통합 테스트
- [x] Step 11: README + 코드 요약 문서

## PBT 테스트 요구(PBT Partial: 02/03/07/08/09)
- P1 calc_total 불변식, P2 next_order_number 불변식, P3 history 직렬화 round-trip, P4 JWT round-trip, P5 status 검증 불변식
- 도메인 제너레이터(양수 가격/수량/유효 상태), Hypothesis, shrinking/seed
