# 단위 테스트 실행 지침 (Unit Test)

## 백엔드 (pytest + Hypothesis)

```bash
cd backend
source .venv/bin/activate
python -m pytest -q
```

- 기대 결과: **24 passed** (PBT 8 + 통합 16), 약 16초
- PBT 파일: `tests/test_logic_pbt.py` (속성 P1~P5)
- 통합 파일: `tests/test_api_integration.py`
- PBT 재현성(PBT-08): 실패 시 Hypothesis가 seed와 최소 반례를 출력. 재현은 출력된 `@reproduce_failure` 데코레이터 사용.

### PBT 시드/CI 메모 (PBT-08)
- Hypothesis 기본 DB(`.hypothesis/`)에 반례 캐시. CI에서는 매 실행 seed 로깅됨.
- shrinking은 기본 활성(비활성화하지 않음).

## 프론트엔드 (Vitest)

```bash
cd frontend
npm test
```

- 기대 결과: **7 passed** (장바구니 로직)
- 파일: `src/store/cart.test.js`

## 실패 시 대응
1. 출력에서 실패 테스트/입력 확인
2. PBT 실패는 최소 반례를 회귀 테스트로 추가(PBT-10)
3. 코드 수정 후 재실행
