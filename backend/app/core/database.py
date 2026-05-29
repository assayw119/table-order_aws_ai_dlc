"""데이터베이스 연결 및 세션 관리 (SQLAlchemy + SQLite)."""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.core.config import DATABASE_URL

# SQLite는 동일 스레드 체크를 비활성화해야 FastAPI(멀티스레드)에서 동작
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """모든 ORM 모델의 베이스 클래스."""
    pass


def get_session() -> Generator[Session, None, None]:
    """FastAPI 의존성: 요청 스코프 DB 세션을 제공하고 종료 시 닫는다."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """모든 테이블 스키마를 생성한다."""
    # 모델 등록을 위해 import (순환 방지: 함수 내부 import)
    from app.core import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
