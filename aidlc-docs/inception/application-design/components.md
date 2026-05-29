# 컴포넌트 정의 (Components)

테이블오더 시스템의 고수준 컴포넌트와 책임을 정의합니다. 상세 비즈니스 로직은 Functional Design 단계에서 다룹니다.

## 아키텍처 개요

- **백엔드**: Python + FastAPI, 단순 구조(Router에서 DB 직접 접근 + 얇은 헬퍼), Pydantic 스키마 검증, SQLite
- **프론트엔드**: 단일 React 프로젝트, 라우팅으로 고객(`/customer`)·관리자(`/admin`) 영역 분리
- **실시간**: SSE 엔드포인트 (관리자용/고객용 분리)
- **인증**: JWT(관리자 16시간) + bcrypt, 클라이언트 localStorage 저장

---

## 백엔드 컴포넌트 (Backend Components)

### C-BE-1: AuthRouter (인증)
- **목적**: 관리자 로그인, 테이블 자격 증명 검증, JWT 발급/검증
- **책임**:
  - 관리자 로그인 처리 (매장 식별자 + 사용자명 + 비밀번호)
  - bcrypt 비밀번호 검증
  - JWT 토큰 발급(16시간) 및 검증 의존성 제공
  - 테이블 로그인(매장 식별자 + 테이블 번호 + 테이블 비밀번호) 처리
  - 로그인 시도 제한
- **인터페이스**: REST 엔드포인트 + JWT 검증 의존성(Depends)

### C-BE-2: MenuRouter (메뉴)
- **목적**: 메뉴 및 카테고리 조회/관리
- **책임**:
  - 고객용: 카테고리별 메뉴 조회(공개)
  - 관리자용: 메뉴 등록/수정/삭제, 노출 순서 조정
  - 입력 검증(필수 필드, 가격 범위)
- **인터페이스**: REST 엔드포인트(공개 조회 + 인증 필요 관리)

### C-BE-3: OrderRouter (주문)
- **목적**: 주문 생성, 조회, 삭제 및 상태 변경
- **책임**:
  - 고객 주문 생성(주문번호 발급, 세션 연결)
  - 현재 세션 주문 내역 조회(고객)
  - 주문 상태 변경(관리자: 대기중/준비중/완료)
  - 주문 삭제(관리자 직권)
  - 주문 변경 시 실시간 이벤트 발행
- **인터페이스**: REST 엔드포인트

### C-BE-4: TableRouter (테이블/세션)
- **목적**: 테이블 초기 설정 및 세션 라이프사이클 관리
- **책임**:
  - 테이블 태블릿 초기 설정(번호/비밀번호, 세션 활성화)
  - 테이블 세션 시작(첫 주문 시) 및 종료(이용 완료) 처리
  - 이용 완료 시 주문 내역 과거 이력 이동 + 현재 주문/총액 리셋
  - 테이블별 현재 주문 및 총액 집계
  - 과거 주문 내역 조회(날짜 필터)
- **인터페이스**: REST 엔드포인트

### C-BE-5: SSERouter (실시간 스트림)
- **목적**: Server-Sent Events 기반 실시간 전달
- **책임**:
  - 관리자용 스트림: 매장 전체 주문 이벤트(신규/상태변경/삭제/세션종료)
  - 고객용 스트림: 특정 테이블 세션 주문 상태 이벤트
  - 이벤트 브로커(EventBus) 구독/해제 관리
- **인터페이스**: SSE 엔드포인트(text/event-stream)

### C-BE-6: EventBus (이벤트 브로커)
- **목적**: 주문 변경 이벤트를 SSE 구독자에게 전달하는 인메모리 발행/구독 허브
- **책임**:
  - 토픽(매장 전체 / 테이블별)별 구독자 관리
  - 이벤트 발행 시 해당 토픽 구독자에게 비동기 전달
  - 연결 종료 시 구독 정리
- **인터페이스**: publish(topic, event), subscribe(topic) → async generator

### C-BE-7: Database (데이터 접근)
- **목적**: SQLite 연결 및 스키마/모델 정의
- **책임**:
  - SQLAlchemy 모델 정의(Store, AdminUser, Table, TableSession, Category, MenuItem, Order, OrderItem, OrderHistory)
  - 세션/연결 관리, 트랜잭션
  - 시드 데이터 로딩 지원
- **인터페이스**: 세션 팩토리, ORM 모델

### C-BE-8: Schemas (Pydantic)
- **목적**: 요청/응답 데이터 검증 및 직렬화
- **책임**: 각 API의 입출력 스키마 정의, 검증 규칙
- **인터페이스**: Pydantic 모델

### C-BE-9: Seed (초기 데이터)
- **목적**: 샘플 매장/관리자/메뉴/테이블 데이터 생성
- **책임**: 데모용 데이터 스크립트
- **인터페이스**: 실행 스크립트(python -m app.seed)

---

## 프론트엔드 컴포넌트 (Frontend Components)

### C-FE-1: AppShell & Router
- **목적**: 단일 React 앱의 라우팅 진입점
- **책임**: `/customer/*`, `/admin/*` 라우트 분리, 공통 레이아웃, 인증 가드

### C-FE-2: 고객 영역 (Customer Area)
- **C-FE-2a: TableLoginSetup** — 테이블 자동 로그인/초기 설정 화면
- **C-FE-2b: MenuView** — 카테고리별 메뉴 조회(기본 화면)
- **C-FE-2c: CartView** — 장바구니(로컬 저장, 수량/총액)
- **C-FE-2d: OrderConfirm** — 주문 확정 및 성공(주문번호, 5초 리다이렉트)
- **C-FE-2e: OrderHistoryView** — 현재 세션 주문 내역(SSE 실시간)

### C-FE-3: 관리자 영역 (Admin Area)
- **C-FE-3a: AdminLogin** — 매장 인증 화면
- **C-FE-3b: OrderDashboard** — 테이블별 그리드, 실시간 모니터링(SSE), 상태 변경
- **C-FE-3c: TableManagement** — 테이블 초기 설정, 주문 삭제, 이용 완료, 과거 내역
- **C-FE-3d: MenuManagement** — 메뉴 CRUD, 순서 조정

### C-FE-4: 공통 클라이언트 모듈
- **C-FE-4a: ApiClient** — REST 호출 래퍼(토큰 첨부)
- **C-FE-4b: SseClient** — SSE 연결/재연결 관리
- **C-FE-4c: AuthStore** — localStorage 기반 토큰/세션 저장
- **C-FE-4d: CartStore** — localStorage 기반 장바구니 상태

---

## 컴포넌트 요약 매핑 (스토리 → 컴포넌트)

| 스토리 | 주요 백엔드 | 주요 프론트엔드 |
|---|---|---|
| US-C1 자동 로그인 | C-BE-1, C-BE-4 | C-FE-2a, C-FE-4c |
| US-C2 메뉴 조회 | C-BE-2 | C-FE-2b |
| US-C3 장바구니 | (클라이언트) | C-FE-2c, C-FE-4d |
| US-C4 주문 생성 | C-BE-3 | C-FE-2d |
| US-C5 주문 내역 | C-BE-3, C-BE-5 | C-FE-2e, C-FE-4b |
| US-A1 매장 인증 | C-BE-1 | C-FE-3a, C-FE-4c |
| US-A2 실시간 모니터링 | C-BE-3, C-BE-5, C-BE-6 | C-FE-3b, C-FE-4b |
| US-A3 테이블 관리 | C-BE-4, C-BE-3 | C-FE-3c |
| US-A4 메뉴 관리 | C-BE-2 | C-FE-3d |
| US-T1 SSE 인프라 | C-BE-5, C-BE-6 | C-FE-4b |
| US-T2 인증/세션 | C-BE-1 | C-FE-4c |
