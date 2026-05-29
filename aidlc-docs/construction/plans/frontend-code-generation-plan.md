# 코드 생성 계획 - UoW-2 Frontend

**코드 위치**: `frontend/` (React + Vite, JavaScript/JSX)
**의존성**: UoW-1 Backend의 REST/SSE API (런타임)

## 생성 단계 (체크리스트)

- [x] Step 1: 프로젝트 구조 + package.json + vite/vitest 설정 + index.html
- [x] Step 2: 공통 모듈 (api/client, api/sse, store/auth, store/cart)
- [x] Step 3: 앱 셸 + 라우팅 (App.jsx, main.jsx, RouteGuard)
- [x] Step 4: 고객 영역 (TableLoginSetup, CustomerLayout, MenuView, CartView, OrderConfirm, OrderHistoryView)
- [x] Step 5: 관리자 영역 (AdminLogin, AdminLayout, OrderDashboard, TableManagement, MenuManagement)
- [x] Step 6: 스타일(CSS, 터치 친화)
- [x] Step 7: 단위 테스트 (CartStore 총액 계산 등) + 빌드 검증
- [x] Step 8: README + 코드 요약

## 스토리 커버리지
US-C1~C5(고객), US-A1~A4(관리자), US-T1(SSE 클라이언트), US-T2(인증/토큰 저장)
