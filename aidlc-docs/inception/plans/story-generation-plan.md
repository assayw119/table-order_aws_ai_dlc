# User Story 생성 계획 (Story Generation Plan)

**역할**: Product Owner
**목적**: 요구사항을 INVEST 기준을 만족하는 사용자 중심 스토리로 변환하고, 페르소나를 정의한다.

---

## Part A: 계획 질문 (아래 질문에 답변해 주세요)

각 질문의 `[Answer]:` 태그 뒤에 선택한 문자(A, B, C ...)를 입력해 주세요. 적합한 선택지가 없으면 마지막 옵션(Other)을 선택하고 직접 작성해 주세요.

### Question 1: 스토리 구성(브레이크다운) 방식
사용자 스토리를 어떤 기준으로 조직할까요?

A) Persona-Based (페르소나별 그룹화: 고객 스토리 / 관리자 스토리)

B) Feature-Based (기능별 그룹화: 메뉴, 장바구니, 주문, 세션, 모니터링 등)

C) User Journey-Based (사용자 여정 흐름별)

D) Hybrid (페르소나 + 기능 혼합: 페르소나로 1차 그룹, 기능으로 2차 그룹)

X) Other (please describe after [Answer]: tag below)

[Answer]: D

### Question 2: 스토리 세분화 수준 (Granularity)
스토리의 크기를 어느 정도로 할까요?

A) 세분화 (작은 단위, 각 화면/동작 단위로 분리 — 스토리 수 많음)

B) 중간 수준 (기능 단위로 묶되 수용 기준으로 세부 동작 표현 — 권장)

C) 큰 단위 (에픽 중심, 굵직한 기능 묶음)

X) Other (please describe after [Answer]: tag below)

[Answer]: B

### Question 3: 수용 기준(Acceptance Criteria) 형식
각 스토리의 수용 기준을 어떤 형식으로 작성할까요?

A) Given-When-Then (BDD 형식)

B) 체크리스트 형식 (조건 나열)

C) 둘 다 혼합 (핵심 시나리오는 Given-When-Then, 부가 조건은 체크리스트)

X) Other (please describe after [Answer]: tag below)

[Answer]: B

### Question 4: 우선순위 표기
스토리에 MVP 우선순위를 표기할까요?

A) 네, 각 스토리에 우선순위(Must/Should/Could) 표기

B) 아니요, 요구사항의 MVP 범위가 이미 명확하므로 모두 Must로 간주

X) Other (please describe after [Answer]: tag below)

[Answer]: B

### Question 5: 비기능/기술 스토리 포함 여부
실시간(SSE), 인증/세션, 테스트(PBT) 같은 기술적 요구사항도 별도 스토리로 포함할까요?

A) 네, 기능 스토리에 더해 기술/비기능 스토리(예: SSE 실시간, JWT 세션)도 별도 작성

B) 아니요, 비기능 요구사항은 관련 기능 스토리의 수용 기준 안에 녹여서 표현

X) Other (please describe after [Answer]: tag below)

[Answer]: X. 추천해줘 → **하이브리드로 확정** (사용자 승인: "추천한대로 하이브리드로 해줘")

> **AI 추천 (확정 대기)**: Lean-Hybrid 방식.
> - 대부분의 비기능 요구사항은 관련 기능 스토리의 수용 기준에 포함 (옵션 B 기조)
> - 단, 두 페르소나에 걸친 교차 관심사(cross-cutting)는 별도 **기술 인에이블러(Technical Enabler) 스토리**로 명시:
>   - SSE 실시간 전달 인프라 (관리자 모니터링 + 고객 주문 내역 공유)
>   - 인증/세션 인프라 (관리자 JWT 16시간 + 테이블 자동 로그인)
> - PBT는 별도 스토리 대신 관련 스토리의 수용 기준 및 후속 Construction 단계에서 처리
> 이 방식으로 진행합니다. (승인 단계에서 조정 가능)

---

## Part B: 실행 체크리스트 (승인 후 진행)

- [x] 승인된 브레이크다운 방식(Q1)에 따라 스토리 구조 결정
- [x] `personas.md` 생성: 고객(테이블 이용자), 매장 관리자 페르소나 정의 (특성, 목표, 동기, 페인포인트)
- [x] `stories.md` 생성: INVEST 기준(Independent, Negotiable, Valuable, Estimable, Small, Testable) 만족하는 사용자 스토리
- [x] 각 스토리에 고유 ID 부여 및 요구사항(FR) 추적성 연결
- [x] 각 스토리에 승인된 형식(Q3)의 수용 기준 작성
- [x] (Q4 결정 시) 우선순위 표기 → 전체 Must로 간주(별도 표기 생략)
- [x] (Q5 결정 시) 기술/비기능 스토리 작성 → Lean-Hybrid: US-T1(SSE), US-T2(인증/세션)
- [x] 페르소나를 관련 스토리에 매핑
- [x] 고객 기능(FR-C1~C5) 및 관리자 기능(FR-A1~A4) 전체 커버리지 검증
