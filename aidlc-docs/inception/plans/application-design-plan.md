# Application Design 계획 (Application Design Plan)

**목적**: 고수준 컴포넌트 식별 및 서비스 계층 설계 (상세 비즈니스 로직은 이후 Functional Design에서 다룸)

---

## Part A: 설계 질문 (아래 질문에 답변해 주세요)

각 질문의 `[Answer]:` 태그 뒤에 선택한 문자(A, B, C ...)를 입력해 주세요. 적합한 선택지가 없으면 마지막 옵션(Other)을 선택하고 직접 작성해 주세요.

### Question 1: 백엔드 아키텍처 스타일
FastAPI 백엔드의 내부 구조를 어떻게 설계할까요?

A) 계층형 아키텍처 (Router → Service → Repository → DB) — 관심사 분리 명확, 권장

B) 단순 구조 (Router에서 직접 DB 접근) — 빠른 구현, MVP 최소화

C) 도메인 주도 설계(DDD) 기반의 풍부한 도메인 모델

X) Other (please describe after [Answer]: tag below)

[Answer]: B

### Question 2: 프론트엔드 구성
고객용/관리자용 React 앱을 어떻게 구성할까요?

A) 별도 두 개의 React 프로젝트 (customer-app, admin-app)로 완전 분리

B) 하나의 React 프로젝트 내에서 라우팅으로 고객/관리자 영역 분리

C) 추천에 맡김

X) Other (please describe after [Answer]: tag below)

[Answer]: C

### Question 3: API 스타일 및 데이터 검증
API 설계 방식은?

A) REST + Pydantic 스키마 기반 요청/응답 검증 (FastAPI 표준, 권장)

B) REST (검증 최소화)

X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 4: SSE 채널 분리 방식
실시간(SSE) 스트림을 어떻게 구성할까요?

A) 관리자용 스트림(매장 전체 주문)과 고객용 스트림(특정 테이블 주문)을 별도 엔드포인트로 분리

B) 단일 스트림 엔드포인트에서 구독 대상(매장/테이블)을 파라미터로 구분

C) 추천에 맡김

X) Other (please describe after [Answer]: tag below)

[Answer]: C

### Question 5: 주문번호 생성 방식
고객에게 표시되는 주문 번호는 어떤 방식으로 생성할까요?

A) 매장 전역 순번 (예: 1, 2, 3 ... 일 단위 리셋 없음)

B) 일자별 순번 (예: 당일 1번부터 시작, 매일 리셋)

C) 세션/테이블 기준 순번

D) 추천에 맡김

X) Other (please describe after [Answer]: tag below)

[Answer]: D

### Question 6: 인증 토큰 저장 위치 (클라이언트)
관리자 JWT 및 테이블 자격 증명을 클라이언트 어디에 저장할까요?

A) localStorage (구현 단순, MVP 적합 — 요구사항의 "로컬 저장"과 부합)

B) httpOnly 쿠키 (XSS 방어 측면 유리)

C) 추천에 맡김

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Part B: 실행 체크리스트 (승인 후 진행)

### 위임 항목에 대한 AI 결정 (사용자 위임: Q2/Q4/Q5)
- **Q2 → B**: 단일 React 프로젝트, 라우팅으로 고객(/customer)·관리자(/admin) 영역 분리
- **Q4 → A**: 관리자용 SSE 스트림과 고객용 SSE 스트림을 별도 엔드포인트로 분리
- **Q5 → B**: 일자별 순번 (당일 1번부터, 매일 리셋)

### 확정된 설계 전제
- 백엔드: 단순 구조(Router → DB 직접 접근, 얇은 헬퍼 함수 허용) + Pydantic 스키마 검증
- 토큰 저장: localStorage

- [x] `components.md` 생성: 컴포넌트 정의 및 고수준 책임
- [x] `component-methods.md` 생성: 메서드 시그니처 및 입출력 타입
- [x] `services.md` 생성: 서비스 정의 및 오케스트레이션 패턴
- [x] `component-dependency.md` 생성: 의존성 매트릭스, 통신 패턴, 데이터 흐름
- [x] `application-design.md` 생성: 위 문서 통합본
- [x] 설계 완전성 및 일관성 검증
