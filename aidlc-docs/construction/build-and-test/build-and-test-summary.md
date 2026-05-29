# 빌드 및 테스트 요약 (Build and Test Summary)

## 빌드 상태
| 유닛 | 빌드 도구 | 상태 | 산출물 |
|---|---|---|---|
| UoW-1 Backend | pip / uvicorn (인터프리터) | 성공 | 앱 임포트/라우트 등록 정상, seed 동작 |
| UoW-2 Frontend | Vite | 성공 | dist/ (50 modules, gzip JS ~59.8kB) |

## 테스트 실행 요약

### 단위 / 속성 기반 테스트 (백엔드)
- 도구: pytest + Hypothesis
- 결과: **24 passed** (PBT 8 + 통합 16), ~14.5초
- PBT 속성: P1(calc_total 불변식), P2(주문번호 불변식), P3(history round-trip), P4(JWT round-trip), P5(상태 검증)

### 단위 테스트 (프론트엔드)
- 도구: Vitest
- 결과: **7 passed** (장바구니 로직/총액)

### 통합 / E2E 스모크 (실서버)
- 도구: 커스텀 HTTP/SSE 스크립트 (`tests/e2e_smoke.py`)
- 결과: **13/13 passed**
- 검증: 로그인, 메뉴, 주문 생성, **SSE 실시간 수신(2초 이내, NFR-P1)**, 상태 변경, 세션 라이프사이클(이용 완료 → 리셋 → 과거 이력)

### 성능
- 신규 주문 SSE 전달: 목표 < 2초, 측정 로컬 < 0.1초 → PASS

## 전체 상태
- **빌드**: 성공 (양 유닛)
- **모든 테스트**: PASS (백엔드 24 + 프론트 7 + E2E 13 = 44)
- **Operations 준비**: Yes (로컬 실행 기준)

## PBT 컴플라이언스 요약 (Partial 모드: PBT-02/03/07/08/09)
| 규칙 | 상태 | 비고 |
|---|---|---|
| PBT-02 round-trip | 충족 | history 직렬화, JWT |
| PBT-03 invariant | 충족 | calc_total, next_order_number, status |
| PBT-07 generator | 충족 | tests/generators.py 도메인 제너레이터 |
| PBT-08 shrinking/seed | 충족 | Hypothesis 기본 활성 |
| PBT-09 framework | 충족 | Hypothesis 의존성 |
| PBT-01,04,05,06,10 | N/A/보완 | 단순 CRUD 범위, 예시 기반 테스트로 보완(PBT-10) |

## 스토리 커버리지
US-C1~C5, US-A1~A4, US-T1, US-T2 → 백엔드+프론트엔드 구현 및 테스트 완료.

## 생성된 지침 파일
- build-instructions.md
- unit-test-instructions.md
- integration-test-instructions.md
- performance-test-instructions.md
- build-and-test-summary.md
