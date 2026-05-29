"""시드 데이터 스크립트: 샘플 매장/관리자/메뉴/테이블 생성 (데모용).

실행: python -m app.seed
"""
from sqlalchemy import select

from app.core.database import SessionLocal, init_db
from app.core.security import hash_password
from app.core.models import Store, AdminUser, Table, Category, MenuItem

# 데모 자격 증명
STORE_CODE = "store001"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin1234"
TABLE_PASSWORD = "table1234"
NUM_TABLES = 6


def run_seed() -> None:
    """샘플 데이터를 삽입한다 (이미 존재하면 건너뜀)."""
    init_db()
    db = SessionLocal()
    try:
        existing = db.scalar(select(Store).where(Store.store_code == STORE_CODE))
        if existing:
            print(f"[seed] 매장 '{STORE_CODE}' 이미 존재 — 건너뜀")
            return

        store = Store(store_code=STORE_CODE, name="데모 식당")
        db.add(store)
        db.flush()

        db.add(AdminUser(
            store_id=store.id,
            username=ADMIN_USERNAME,
            password_hash=hash_password(ADMIN_PASSWORD),
        ))

        # 카테고리 + 메뉴
        categories = [
            ("메인", 1, [
                ("불고기 정식", 12000, "직화 불고기와 공기밥"),
                ("비빔밥", 9000, "신선한 나물 비빔밥"),
                ("김치찌개", 8000, "돼지고기 김치찌개"),
            ]),
            ("사이드", 2, [
                ("계란말이", 5000, "부드러운 계란말이"),
                ("감자튀김", 4000, "바삭한 감자튀김"),
            ]),
            ("음료", 3, [
                ("콜라", 2000, "시원한 콜라"),
                ("사이다", 2000, "탄산 사이다"),
                ("아메리카노", 3000, "따뜻한 아메리카노"),
            ]),
        ]
        for cat_name, cat_order, items in categories:
            category = Category(store_id=store.id, name=cat_name, display_order=cat_order)
            db.add(category)
            db.flush()
            for idx, (name, price, desc) in enumerate(items, start=1):
                db.add(MenuItem(
                    store_id=store.id,
                    category_id=category.id,
                    name=name,
                    price=price,
                    description=desc,
                    image_url=None,
                    display_order=idx,
                    is_available=True,
                ))

        # 테이블 (비밀번호 설정 → 자동 로그인 활성)
        for num in range(1, NUM_TABLES + 1):
            db.add(Table(
                store_id=store.id,
                table_number=num,
                password_hash=hash_password(TABLE_PASSWORD),
            ))

        db.commit()
        print("[seed] 데모 데이터 생성 완료")
        print(f"  매장 식별자: {STORE_CODE}")
        print(f"  관리자: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
        print(f"  테이블: 1~{NUM_TABLES}번 (비밀번호: {TABLE_PASSWORD})")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
