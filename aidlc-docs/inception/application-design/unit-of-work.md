# 작업 단위 정의 (Unit of Work)

## 분해 전략 요약
- **분해 방식(Q1=C)**: 계층별 유닛 — 백엔드 유닛 / 프론트엔드 유닛 2개
- **프론트엔드(Q2 위임→분리)**: 별도 유닛
- **공유 코드(Q4 위임→유닛 내 모듈)**: 백엔드 유닛 내 `core` 모듈에 DB/모델/스키마/인증 유틸 배치
- **구현 순서(Q3=A)**: 의존성 기반 → Backend(UoW-1) → Frontend(UoW-2)
- **배포 모델**: 단일 매장 로컬 실행. 독립 배포형 서비스 아님 → "모놀리식 + 논리 모듈" 성격

---

## UoW-1: Backend (FastAPI 서버)

- **유형**: 애플리케이션 서버 (REST API + SSE)
- **책임**:
  - 인증/인가(관리자 JWT, 테이블 토큰)
  - 메뉴/카테고리 조회 및 관리
  - 주문 생성/조회/상태변경/삭제
  - 테이블 초기 설정 및 세션 라이프사이클(시작/이용 완료/과거 이력)
  - 실시간 이벤트(EventBus) 및 SSE 스트림
  - 데이터 영속(SQLite), 시드 데이터
- **포함 컴포넌트**: C-BE-1~C-BE-9 (AuthRouter, MenuRouter, OrderRouter, TableRouter, SSERouter, EventBus, Database, Schemas, Seed)
- **논리 모듈 (백엔드 유닛 내부)**:
  - `core`: DB 연결/세션, ORM 모델, 공통 Pydantic 베이스, 인증 유틸(JWT/bcrypt), 설정
  - `auth`: 인증 라우터/스키마
  - `menu`: 메뉴 라우터/스키마
  - `orders`: 주문 라우터/스키마 + 주문번호/총액 헬퍼
  - `tables`: 테이블/세션 라우터/스키마 + 세션 헬퍼
  - `realtime`: EventBus + SSE 라우터
- **소유 데이터 엔티티**: Store, AdminUser, Table, TableSession, Category, MenuItem, Order, OrderItem, OrderHistory
- **인터페이스 제공**: REST 엔드포인트, SSE 스트림 (프론트엔드가 소비)

## UoW-2: Frontend (React 단일 앱)

- **유형**: 웹 클라이언트 (SPA)
- **책임**:
  - 고객 영역: 자동 로그인/설정, 메뉴 조회, 장바구니, 주문 생성, 주문 내역(SSE)
  - 관리자 영역: 로그인, 실시간 모니터링 대시보드(SSE), 테이블 관리, 메뉴 관리
  - 공통: REST 클라이언트, SSE 클라이언트, 로컬 저장(Auth/Cart)
- **포함 컴포넌트**: C-FE-1~C-FE-4 (AppShell/Router, 고객 영역, 관리자 영역, 공통 모듈)
- **인터페이스 소비**: UoW-1 Backend의 REST/SSE

---

## 코드 조직 전략 (Greenfield, 모놀리식 멀티유닛)

워크스페이스 루트 기준 구조 (애플리케이션 코드는 절대 aidlc-docs/에 두지 않음):

```
/ (workspace root)
├── backend/                 # UoW-1: FastAPI
│   ├── app/
│   │   ├── main.py          # FastAPI 앱 진입점, 라우터 등록
│   │   ├── core/            # DB, 모델, 설정, 인증 유틸, 공통 스키마 베이스
│   │   │   ├── database.py
│   │   │   ├── models.py
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── auth/            # 인증 라우터/스키마
│   │   ├── menu/            # 메뉴 라우터/스키마
│   │   ├── orders/          # 주문 라우터/스키마/헬퍼
│   │   ├── tables/          # 테이블·세션 라우터/스키마/헬퍼
│   │   ├── realtime/        # EventBus + SSE 라우터
│   │   └── seed.py          # 시드 데이터
│   ├── tests/               # 단위/통합/PBT 테스트
│   ├── requirements.txt
│   └── README.md
│
├── frontend/                # UoW-2: React (단일 앱, /customer·/admin 라우팅)
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx          # 라우터 (/customer, /admin)
│   │   ├── api/             # ApiClient, SseClient
│   │   ├── store/           # AuthStore, CartStore (localStorage)
│   │   ├── customer/        # 고객 화면들
│   │   └── admin/           # 관리자 화면들
│   ├── tests/
│   ├── package.json
│   └── README.md
│
└── README.md                # 전체 실행 안내
```

> 참고: 본 구조는 code-generation.md의 "Greenfield multi-unit (monolith)" 패턴을 두 개의 최상위 앱 디렉터리(backend/, frontend/)로 적용한 것입니다. 각 유닛이 독립 실행 단위(서버/클라이언트)이므로 루트 분리가 자연스럽습니다.

## 검증
- [x] 모든 백엔드 컴포넌트(C-BE-*)가 UoW-1에 할당
- [x] 모든 프론트엔드 컴포넌트(C-FE-*)가 UoW-2에 할당
- [x] 공유 코드는 UoW-1의 core 모듈로 명확히 배치
- [x] 유닛 경계가 계층(서버/클라이언트)으로 명확히 구분됨
