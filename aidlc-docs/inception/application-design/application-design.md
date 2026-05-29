# 애플리케이션 설계 통합 문서 (Application Design)

본 문서는 테이블오더 시스템의 고수준 애플리케이션 설계를 통합 정리합니다. 세부 내용은 개별 문서를 참조하세요:
- `components.md` — 컴포넌트 정의 및 책임
- `component-methods.md` — 메서드 시그니처
- `services.md` — 서비스 오케스트레이션 흐름
- `component-dependency.md` — 의존성 및 통신 패턴

---

## 1. 설계 결정 요약 (Design Decisions)

| 항목 | 결정 | 출처 |
|---|---|---|
| 백엔드 아키텍처 | 단순 구조 (Router → DB 직접 + 얇은 헬퍼) + Pydantic 검증 | Q1=B, Q3=A |
| 프론트엔드 구성 | 단일 React 프로젝트, 라우팅으로 /customer·/admin 분리 | Q2→B (위임) |
| SSE 채널 | 관리자/고객 별도 엔드포인트 | Q4→A (위임) |
| 주문번호 | 일자별 순번 (당일 1번부터, 매일 리셋) | Q5→B (위임) |
| 토큰 저장 | localStorage | Q6=A |
| 데이터 저장소 | SQLite + SQLAlchemy | 요구사항 Q3=C |
| 실시간 | 인메모리 EventBus + SSE (단일 프로세스) | 로컬 실행 Q6=A |

## 2. 컴포넌트 개요

**백엔드 (FastAPI)**: AuthRouter, MenuRouter, OrderRouter, TableRouter, SSERouter, EventBus, Database, Schemas, Seed

**프론트엔드 (React 단일 앱)**:
- 고객 영역: TableLoginSetup, MenuView, CartView, OrderConfirm, OrderHistoryView
- 관리자 영역: AdminLogin, OrderDashboard, TableManagement, MenuManagement
- 공통: ApiClient, SseClient, AuthStore, CartStore

## 3. 핵심 흐름 (요약)

1. **고객 주문**: 자동 로그인(테이블 토큰) → 메뉴 조회 → 장바구니(로컬) → 주문 생성(세션 보장 + 주문번호 발급 + 저장 + 이벤트 발행) → 5초 후 메뉴 복귀
2. **관리자 모니터링**: 로그인(JWT 16h) → 대시보드 SSE 구독 → 신규/변경 주문 실시간 표시(2초 이내) → 상태 변경/주문 삭제
3. **세션 라이프사이클**: 첫 주문 시 세션 시작 → 이용 완료 시 주문을 OrderHistory로 이동 + 현재 주문/총액 리셋 + 이벤트 발행
4. **실시간 전달**: OrderRouter/TableRouter 발행 → EventBus(토픽: store/table) → SSERouter 푸시 → 관리자/고객 클라이언트

## 4. 데이터 모델 (개요)

```
Store 1---* AdminUser
Store 1---* Table 1---* TableSession 1---* Order 1---* OrderItem
Store 1---* Category 1---* MenuItem
TableSession ---* OrderHistory (이용 완료 시 Order에서 이동)
```

- **Order.status**: 대기중 / 준비중 / 완료 (Q9)
- **Order**: order_number(일자별), session_id, total_amount, created_at
- **OrderItem**: menu_name(스냅샷), unit_price(스냅샷), quantity
- **OrderHistory**: 세션 종료 시 이동, completed_at 기록

> 상세 필드/제약/관계는 Functional Design 단계에서 확정합니다.

## 5. 인터페이스 요약 (주요 엔드포인트)

- 인증: `POST /api/auth/admin/login`, `POST /api/auth/table/login`
- 메뉴: `GET /api/menu/categories`, `GET /api/menu/items`, `POST|PUT|DELETE /api/admin/menu/items`
- 주문: `POST /api/orders`, `GET /api/orders/current`, `GET /api/admin/orders`, `PATCH /api/admin/orders/{id}/status`, `DELETE /api/admin/orders/{id}`
- 테이블/세션: `POST /api/admin/tables/setup`, `GET /api/admin/tables`, `POST /api/admin/tables/{id}/checkout`, `GET /api/admin/tables/{id}/history`
- 실시간: `GET /api/admin/stream`, `GET /api/table/stream`

## 6. 설계 완전성 검증

- [x] 모든 사용자 스토리(US-C1~C5, US-A1~A4, US-T1~T2)가 컴포넌트에 매핑됨 (components.md 매핑표)
- [x] 모든 기능 요구사항(FR-C*, FR-A*)에 대응하는 엔드포인트 정의
- [x] 실시간(US-T1) 및 인증/세션(US-T2) 교차 관심사 반영(EventBus/SSE, Auth)
- [x] 데이터 모델 개요와 상태 흐름(Q9) 일치
- [x] 의존성 및 통신 패턴 명시, 순환 의존 없음
