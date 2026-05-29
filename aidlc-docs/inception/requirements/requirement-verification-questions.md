# 요구사항 확인 질문 (Requirements Verification Questions)

아래 질문에 답변해 주세요. 각 질문의 `[Answer]:` 태그 뒤에 선택한 항목의 **문자(A, B, C ...)** 를 입력하시면 됩니다.
제시된 선택지가 적절하지 않으면 마지막 옵션(Other)을 선택하고 `[Answer]:` 뒤에 직접 설명을 작성해 주세요.

요구사항 정의서(`requirements/table-order-requirements.md`)와 제외사항(`requirements/constraints.md`)은 이미 검토했습니다. 아래는 구현 방향을 확정하기 위해 추가로 필요한 사항입니다.

---

## Question 1: 백엔드 기술 스택
서버 시스템은 어떤 언어/프레임워크로 구현할까요?

A) Node.js + Express (JavaScript/TypeScript)

B) Node.js + NestJS (TypeScript, 구조화된 아키텍처)

C) Python + FastAPI

D) Java + Spring Boot

E) 추천에 맡김 (프로젝트 특성에 맞춰 AI가 결정)

X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## Question 2: 프론트엔드 기술 스택
고객용 / 관리자용 웹 UI는 어떤 방식으로 구현할까요?

A) React (SPA)

B) Vue.js (SPA)

C) 순수 HTML/CSS/JavaScript (프레임워크 없음, 가벼운 구성)

D) 서버 사이드 렌더링 (예: Next.js / 템플릿 엔진)

E) 추천에 맡김 (프로젝트 특성에 맞춰 AI가 결정)

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 3: 데이터 저장소
매장, 메뉴, 주문, 주문 이력 데이터는 어디에 저장할까요? (요구사항에 OrderHistory 테이블 언급이 있어 관계형 DB를 가정하고 있습니다)

A) 관계형 DB - PostgreSQL

B) 관계형 DB - MySQL

C) 관계형 DB - SQLite (로컬/경량, MVP 및 데모에 적합)

D) NoSQL - MongoDB

E) 추천에 맡김 (프로젝트 특성에 맞춰 AI가 결정)

X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## Question 4: 멀티 매장(테넌시) 범위
"매장 식별자"가 요구사항에 등장합니다. 이 시스템은 여러 매장을 동시에 지원해야 하나요?

A) 다중 매장 지원 (매장 식별자로 데이터 분리, 멀티테넌트)

B) 단일 매장 전용 (MVP는 한 매장만, 매장 식별자는 단순 식별 용도)

X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Question 5: 초기 데이터 준비 방식
매장 계정, 관리자 계정, 초기 메뉴 데이터는 어떻게 준비할까요?

A) 시드(seed) 스크립트로 샘플 매장/관리자/메뉴 자동 생성 (데모용)

B) 매장/관리자 회원가입(등록) 화면을 별도로 구현

C) 둘 다 (시드 데이터 + 등록 기능)

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 6: 배포/실행 환경
어떤 환경에서 실행하는 것을 목표로 할까요?

A) 로컬 개발 환경 (한 머신에서 실행, MVP/데모 우선)

B) Docker 컨테이너 (docker-compose로 일괄 실행)

C) 클라우드 배포 (AWS 등) 고려

D) 추천에 맡김

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 7: 보안 확장 (Security Baseline)
이 프로젝트에 보안 확장 규칙을 강제 적용할까요?

A) Yes — 모든 SECURITY 규칙을 차단(blocking) 제약으로 강제 적용 (운영 수준 애플리케이션 권장)

B) No — 모든 SECURITY 규칙 생략 (PoC, 프로토타입, 실험 프로젝트에 적합)

X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Question 8: 속성 기반 테스트 확장 (Property-Based Testing)
이 프로젝트에 속성 기반 테스트(PBT) 규칙을 강제 적용할까요?

A) Yes — 모든 PBT 규칙을 차단(blocking) 제약으로 강제 적용 (비즈니스 로직, 데이터 변환, 직렬화, 상태 컴포넌트가 있는 프로젝트 권장)

B) Partial — 순수 함수 및 직렬화 왕복(round-trip)에만 PBT 규칙 적용 (알고리즘 복잡도가 제한적인 프로젝트에 적합)

C) No — 모든 PBT 규칙 생략 (단순 CRUD, UI 전용, 비즈니스 로직이 적은 통합 계층에 적합)

X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Question 9: 주문 상태 흐름
주문 상태는 요구사항에 "대기중/준비중/완료" 3단계로 명시되어 있습니다. 이대로 구현하면 될까요?

A) 네, 3단계(대기중/준비중/완료)로 구현

B) 아니요, 다른 상태 흐름 필요 (Other에 설명)

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 10: 실시간 주문 내역 업데이트 (고객용)
고객용 주문 내역 조회에서 주문 상태 실시간 업데이트는 요구사항에 "선택사항"으로 표시되어 있습니다. MVP에 포함할까요?

A) 포함 — 고객 화면도 SSE로 주문 상태 실시간 반영

B) 미포함 — 고객은 새로고침/재조회 시에만 상태 갱신 (MVP 범위 최소화)

X) Other (please describe after [Answer]: tag below)

[Answer]: A
