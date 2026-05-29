# Unit of Work 분해 계획 (Units Generation Plan)

**목적**: 시스템을 관리 가능한 작업 단위(Unit of Work)로 분해한다.

**컨텍스트**: 단일 매장 MVP, 로컬 실행, FastAPI 모놀리식 백엔드 + 단일 React 앱. 따라서 독립 배포형 마이크로서비스보다는 **단일 애플리케이션 내 논리적 모듈** 분해가 적합하다.

---

## Part A: 분해 질문 (아래 질문에 답변해 주세요)

각 질문의 `[Answer]:` 태그 뒤에 선택한 문자(A, B, C ...)를 입력해 주세요. 적합한 선택지가 없으면 마지막 옵션(Other)을 선택하고 직접 작성해 주세요.

### Question 1: 배포 모델 및 유닛 구성
시스템을 어떤 단위로 분해할까요?

A) 단일 통합 유닛 (백엔드+프론트엔드 전체를 하나의 유닛으로) — 가장 단순, 작은 MVP

B) 기능 도메인별 논리적 모듈 유닛 (예: 인증/메뉴/주문/테이블세션/실시간 + 프론트엔드) — 구조적 분리, 권장

C) 계층별 유닛 (백엔드 유닛 / 프론트엔드 유닛 2개로 분리)

D) 추천에 맡김

X) Other (please describe after [Answer]: tag below)

[Answer]: C

### Question 2: 프론트엔드 유닛 취급
프론트엔드(React)는 어떻게 다룰까요?

A) 별도 유닛으로 분리 (백엔드 유닛들과 독립)

B) 각 기능 도메인 유닛에 관련 프론트엔드 화면을 포함

C) 추천에 맡김

X) Other (please describe after [Answer]: tag below)

[Answer]: C

### Question 3: 유닛 구현(개발) 순서
유닛을 어떤 순서로 구현하기를 원하시나요?

A) 의존성 기반 자동 결정 (기반 유닛 → 의존 유닛 순, AI가 위상 정렬)

B) 사용자가 직접 순서 지정 (Other에 기재)

X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 4: 공유 코드(모델/스키마/DB) 취급
DB 모델, Pydantic 스키마, 인증 유틸 등 공유 코드는 어떻게 배치할까요?

A) 공통 기반(Core/Shared) 유닛으로 분리하여 다른 유닛이 의존

B) 각 유닛에 분산 배치하고 중복 최소화는 개발 중 조정

C) 추천에 맡김

X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## Part B: 실행 체크리스트 (승인 후 진행)

### 위임 항목에 대한 AI 결정 (사용자 위임: Q2/Q4)
- **Q2 → A 취지**: 프론트엔드를 별도 유닛으로 분리 (Q1=C 계층 분리와 일관)
- **Q4 → A 취지(유닛 내 모듈)**: 유닛이 2개(백엔드/프론트엔드)뿐이므로 별도 공유 유닛은 만들지 않고, 공유 코드(DB/모델/스키마/인증 유틸)는 **백엔드 유닛 내 `core` 모듈**로 배치
- **확정 유닛**: UoW-1 Backend(FastAPI), UoW-2 Frontend(React)
- **구현 순서(Q3=A)**: 의존성 기반 → UoW-1 Backend → UoW-2 Frontend

- [x] `unit-of-work.md` 생성: 유닛 정의 및 책임 + (그린필드) 코드 조직 전략
- [x] `unit-of-work-dependency.md` 생성: 유닛 의존성 매트릭스
- [x] `unit-of-work-story-map.md` 생성: 스토리→유닛 매핑
- [x] 유닛 경계 및 의존성 검증
- [x] 모든 스토리가 유닛에 할당되었는지 검증
