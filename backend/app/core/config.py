"""애플리케이션 설정(config).

환경 변수로 override 가능하며, 로컬 개발 기본값을 제공합니다.
"""
import os

# JWT 서명 비밀키 (운영에서는 환경 변수로 주입)
JWT_SECRET = os.getenv("TABLEORDER_JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"

# 관리자 세션 16시간 (초 단위)
ADMIN_TOKEN_TTL_SECONDS = 16 * 60 * 60

# 테이블 토큰 TTL: 자동 로그인 특성상 길게 (30일)
TABLE_TOKEN_TTL_SECONDS = 30 * 24 * 60 * 60

# 데이터베이스 URL (SQLite 단일 파일)
DATABASE_URL = os.getenv("TABLEORDER_DATABASE_URL", "sqlite:///./tableorder.db")

# 로그인 시도 제한
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 5 * 60  # 5분

# CORS 허용 origin (프론트엔드 개발 서버)
CORS_ORIGINS = os.getenv(
    "TABLEORDER_CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")

# 주문 상태 허용 값
ORDER_STATUSES = ("대기중", "준비중", "완료")
