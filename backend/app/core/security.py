"""보안 유틸: 비밀번호 해싱, JWT 발급/검증, 로그인 시도 제한, 인증 의존성."""
import time
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)


# ---------- 비밀번호 ----------
def hash_password(plain: str) -> str:
    """평문 비밀번호를 bcrypt 해시로 변환한다 (BR-AUTH-4)."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """평문과 해시를 비교한다."""
    return pwd_context.verify(plain, hashed)


# ---------- JWT ----------
def create_token(claims: dict, ttl_seconds: int) -> str:
    """클레임과 만료 시간을 담은 JWT를 발급한다."""
    to_encode = dict(claims)
    expire = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """JWT를 검증/디코드한다. 실패 시 JWTError 발생."""
    return jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])


# ---------- 로그인 시도 제한 (인메모리) ----------
_login_attempts: dict[str, tuple[int, float]] = {}  # key -> (fail_count, locked_until_ts)


def check_login_allowed(key: str) -> bool:
    """해당 키의 로그인 시도가 허용되는지 확인한다 (BR-AUTH-5)."""
    entry = _login_attempts.get(key)
    if not entry:
        return True
    fail_count, locked_until = entry
    if locked_until and time.time() < locked_until:
        return False
    return True


def record_login_failure(key: str) -> None:
    """로그인 실패를 기록하고 임계치 초과 시 잠금한다."""
    fail_count, _ = _login_attempts.get(key, (0, 0.0))
    fail_count += 1
    locked_until = 0.0
    if fail_count >= config.MAX_LOGIN_ATTEMPTS:
        locked_until = time.time() + config.LOGIN_LOCKOUT_SECONDS
        fail_count = 0  # 잠금 후 카운터 리셋
    _login_attempts[key] = (fail_count, locked_until)


def reset_login_attempts(key: str) -> None:
    """로그인 성공 시 카운터를 초기화한다."""
    _login_attempts.pop(key, None)


# ---------- 인증 의존성 ----------
def _decode_or_401(creds: HTTPAuthorizationCredentials | None) -> dict:
    if creds is None or not creds.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증 토큰이 없습니다.")
    try:
        return decode_token(creds.credentials)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않거나 만료된 토큰입니다.")


def get_current_admin(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    """관리자 토큰을 검증하고 컨텍스트(store_id, username)를 반환한다."""
    payload = _decode_or_401(creds)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="관리자 권한이 필요합니다.")
    return {"store_id": payload["store_id"], "username": payload.get("sub")}


def get_current_table(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    """테이블 토큰을 검증하고 컨텍스트(store_id, table_id)를 반환한다."""
    payload = _decode_or_401(creds)
    if payload.get("role") != "table":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="테이블 권한이 필요합니다.")
    return {"store_id": payload["store_id"], "table_id": payload["table_id"]}
