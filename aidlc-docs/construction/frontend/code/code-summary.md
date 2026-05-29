# 코드 생성 요약 - UoW-2 Frontend

## 생성된 파일 (워크스페이스 `frontend/`)

### 설정
- `package.json`, `vite.config.js`, `index.html`, `.gitignore`, `README.md`

### 공통 모듈
- `src/api/config.js` — API_BASE
- `src/api/client.js` — REST 래퍼(ApiError, 토큰 첨부)
- `src/api/sse.js` — useSse 훅(SSE 구독 + 지수 백오프 재연결)
- `src/store/auth.js` — authStore(localStorage)
- `src/store/cart.js` — cartStore + calcCartTotal(순수 함수)

### 앱 셸
- `src/main.jsx`, `src/App.jsx`(라우팅 + RequireTable/RequireAdmin 가드)
- `src/styles.css`(터치 친화 스타일)

### 고객 영역
- `TableLoginSetup.jsx`(US-C1), `CustomerLayout.jsx`, `MenuView.jsx`(US-C2),
  `CartView.jsx`(US-C3), `OrderConfirm.jsx`(US-C4, 5초 리다이렉트), `OrderHistoryView.jsx`(US-C5, SSE)

### 관리자 영역
- `AdminLogin.jsx`(US-A1), `AdminLayout.jsx`, `OrderDashboard.jsx`(US-A2, SSE+강조),
  `TableManagement.jsx`(US-A3, 설정/이용완료/과거내역), `MenuManagement.jsx`(US-A4 CRUD)

### 테스트
- `src/test/setup.js`, `src/store/cart.test.js`(7 tests)

## 검증 결과
- `npm test`: **7 passed** (장바구니 로직)
- `npm run build`: 성공 (50 modules, gzip JS 59.85kB)

## 백엔드 연동 변경
- SSE 엔드포인트를 쿼리 파라미터 토큰 방식으로 변경(브라우저 EventSource는 커스텀 헤더 불가).
  → `backend/app/realtime/router.py` 수정, 백엔드 재검증 통과.

## 스토리 구현 매핑 (프론트엔드 측)
US-C1~C5, US-A1~A4, US-T1(SSE 클라이언트), US-T2(토큰 저장/첨부) → 구현 완료

## data-testid 적용
주요 인터랙션 요소에 안정적 testid 부여(자동화 친화): table-login-submit, menu-card-add-{id},
cart-checkout-button, order-submit, admin-login-submit, set-status-{status}, table-checkout-{id} 등
