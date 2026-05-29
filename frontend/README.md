# 테이블오더 프론트엔드 (UoW-2)

React + Vite 단일 앱. 라우팅으로 고객(`/customer`)·관리자(`/admin`) 영역 분리.

## 요구 사항
- Node.js 18+ (권장 20+)
- 백엔드 서버 실행 중 (http://localhost:8000)

## 설치 및 실행

```bash
cd frontend
npm install

# 개발 서버 (http://localhost:5173)
npm run dev
```

백엔드 주소가 다르면 환경 변수로 지정:
```bash
VITE_API_BASE=http://localhost:8000 npm run dev
```

## 화면
- 고객: `http://localhost:5173/customer` (최초 1회 테이블 설정 → 자동 로그인)
- 관리자: `http://localhost:5173/admin/login`

데모 자격 증명은 백엔드 seed 참조 (store001 / admin / admin1234, 테이블 비밀번호 table1234).

## 테스트 / 빌드
```bash
npm test       # Vitest 단위 테스트
npm run build  # 프로덕션 빌드
```

## 구조
- `src/api` — ApiClient(REST), useSse(SSE 훅), config
- `src/store` — authStore, cartStore (localStorage)
- `src/customer` — 고객 화면(설정/메뉴/장바구니/주문확인/주문내역)
- `src/admin` — 관리자 화면(로그인/대시보드/테이블관리/메뉴관리)
- `src/App.jsx` — 라우팅 + 인증 가드
