"""pytest 픽스처: 격리된 인메모리 DB와 TestClient 제공."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.core.database import Base, get_session
from app.core import models  # noqa: F401  (모델 등록)
from app.main import app
from app.core.security import hash_password
from app.core.models import Store, AdminUser, Table, Category, MenuItem


@pytest.fixture()
def db_session():
    """테스트마다 새 인메모리 SQLite 엔진/세션 생성."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session):
    """get_session 의존성을 테스트 세션으로 오버라이드한 TestClient."""
    def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def seeded(db_session):
    """기본 매장/관리자/메뉴/테이블 시드."""
    store = Store(store_code="store001", name="테스트 식당")
    db_session.add(store)
    db_session.flush()
    db_session.add(AdminUser(
        store_id=store.id, username="admin", password_hash=hash_password("admin1234")
    ))
    cat = Category(store_id=store.id, name="메인", display_order=1)
    db_session.add(cat)
    db_session.flush()
    item1 = MenuItem(store_id=store.id, category_id=cat.id, name="비빔밥", price=9000, display_order=1)
    item2 = MenuItem(store_id=store.id, category_id=cat.id, name="콜라", price=2000, display_order=2)
    db_session.add_all([item1, item2])
    table = Table(store_id=store.id, table_number=1, password_hash=hash_password("table1234"))
    db_session.add(table)
    db_session.commit()
    db_session.refresh(store)
    db_session.refresh(item1)
    db_session.refresh(item2)
    db_session.refresh(table)
    return {
        "store": store, "item1_id": item1.id, "item2_id": item2.id,
        "table_id": table.id, "table_number": table.table_number,
    }


@pytest.fixture()
def admin_token(client, seeded):
    """관리자 로그인 토큰."""
    resp = client.post("/api/auth/admin/login", json={
        "store_code": "store001", "username": "admin", "password": "admin1234",
    })
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture()
def table_token(client, seeded):
    """테이블 로그인 토큰."""
    resp = client.post("/api/auth/table/login", json={
        "store_code": "store001", "table_number": 1, "table_password": "table1234",
    })
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]
