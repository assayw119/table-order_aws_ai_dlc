# 빌드 지침 (Build Instructions)

## 사전 요구 사항
- Python 3.11+ (백엔드)
- Node.js 18+ (권장 20+) (프론트엔드)
- OS: macOS/Linux/Windows

## 백엔드 (UoW-1)

### 1. 의존성 설치
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 데모 데이터 생성
```bash
python -m app.seed
```

### 3. 서버 실행
```bash
uvicorn app.main:app --port 8000
```
- 성공 출력: `Uvicorn running on http://127.0.0.1:8000`
- API 문서: http://localhost:8000/docs
- 빌드 산출물: 별도 컴파일 없음(인터프리터). DB 파일 `tableorder.db` 자동 생성.

## 프론트엔드 (UoW-2)

### 1. 의존성 설치
```bash
cd frontend
npm install
```

### 2. 개발 서버
```bash
npm run dev   # http://localhost:5173
```

### 3. 프로덕션 빌드
```bash
npm run build   # dist/ 생성
```
- 성공 출력: `built in ...`, `dist/` 에 정적 자산 생성(약 50 modules).

## 실행 순서 (로컬 통합)
1. 백엔드: seed 후 `uvicorn app.main:app --port 8000`
2. 프론트엔드: `npm run dev` (기본 5173, 백엔드 CORS 허용됨)
3. 고객: http://localhost:5173/customer , 관리자: http://localhost:5173/admin/login

## 트러블슈팅
- **CORS 오류**: 백엔드 `TABLEORDER_CORS_ORIGINS` 환경변수에 프론트 origin 추가.
- **SSE 미수신**: 프론트 `VITE_API_BASE`가 백엔드 주소와 일치하는지 확인.
- **bcrypt 경고**: passlib의 crypt DeprecationWarning은 무해(동작 영향 없음).
