# 기술 스택 결정 (Tech Stack Decisions) - UoW-2 Frontend

| 영역 | 선택 | 근거 |
|---|---|---|
| 프레임워크 | React 18 | 요구사항 Q2=A |
| 빌드 도구 | Vite | 빠른 개발 서버, 경량, 기본 포트 5173(CORS 설정과 일치) |
| 언어 | JavaScript (JSX) | MVP 단순화 (TS 미도입) |
| 라우팅 | react-router-dom v6 | /customer·/admin 분리 |
| HTTP | fetch (브라우저 내장) | 별도 라이브러리 불필요 |
| 실시간 | EventSource (브라우저 내장 SSE) | 백엔드 SSE 소비 |
| 상태/저장 | localStorage + React state | 요구사항 Q6=A(localStorage), 장바구니 로컬 저장 |
| 스타일 | 일반 CSS (경량) | 외부 UI 프레임워크 미도입, 터치 친화 스타일 |
| 테스트 | Vitest + @testing-library/react | Vite 친화 단위 테스트 |

## PBT 적용 여부
- 프론트엔드는 UI/통합 계층으로 비즈니스 로직이 적음 → PBT는 백엔드 중심 적용.
- 단, 클라이언트 순수 로직(장바구니 총액 계산)이 존재하면 단위 테스트로 검증.

## 의존성 (package.json 예정)
```
react, react-dom, react-router-dom
(dev) vite, @vitejs/plugin-react, vitest, @testing-library/react, jsdom
```
