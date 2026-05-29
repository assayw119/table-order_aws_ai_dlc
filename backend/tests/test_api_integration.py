"""API 통합 테스트: 인증, 메뉴, 주문, 세션 라이프사이클 (예시 기반, PBT-10 보완)."""


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------- 인증 ----------
def test_admin_login_success(client, seeded):
    resp = client.post("/api/auth/admin/login", json={
        "store_code": "store001", "username": "admin", "password": "admin1234",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_admin_login_wrong_password(client, seeded):
    resp = client.post("/api/auth/admin/login", json={
        "store_code": "store001", "username": "admin", "password": "wrong",
    })
    assert resp.status_code == 401


def test_table_login_success(client, seeded):
    resp = client.post("/api/auth/table/login", json={
        "store_code": "store001", "table_number": 1, "table_password": "table1234",
    })
    assert resp.status_code == 200
    assert resp.json()["table_number"] == 1


def test_protected_endpoint_requires_token(client, seeded):
    resp = client.get("/api/admin/orders")
    assert resp.status_code == 401


# ---------- 메뉴 ----------
def test_customer_menu_listing(client, seeded, table_token):
    resp = client.get("/api/menu/items", headers=auth_header(table_token))
    assert resp.status_code == 200
    names = [m["name"] for m in resp.json()]
    assert "비빔밥" in names


def test_admin_create_and_delete_menu(client, seeded, admin_token):
    # 카테고리 id 확보
    cats = client.get("/api/menu/categories", headers=auth_header(
        client.post("/api/auth/table/login", json={
            "store_code": "store001", "table_number": 1, "table_password": "table1234"
        }).json()["access_token"]
    )).json()
    cat_id = cats[0]["id"]

    resp = client.post("/api/admin/menu/items", headers=auth_header(admin_token), json={
        "category_id": cat_id, "name": "김치찌개", "price": 8000,
    })
    assert resp.status_code == 201
    item_id = resp.json()["id"]

    resp = client.delete(f"/api/admin/menu/items/{item_id}", headers=auth_header(admin_token))
    assert resp.status_code == 204


def test_create_menu_negative_price_rejected(client, seeded, admin_token):
    resp = client.post("/api/admin/menu/items", headers=auth_header(admin_token), json={
        "category_id": 1, "name": "이상메뉴", "price": -100,
    })
    assert resp.status_code == 422


# ---------- 주문 ----------
def test_create_order_and_total(client, seeded, table_token):
    resp = client.post("/api/orders", headers=auth_header(table_token), json={
        "items": [
            {"menu_item_id": seeded["item1_id"], "quantity": 2},  # 9000*2
            {"menu_item_id": seeded["item2_id"], "quantity": 1},  # 2000
        ]
    })
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["total_amount"] == 20000
    assert body["order_number"] == 1
    assert body["status"] == "대기중"


def test_order_number_increments(client, seeded, table_token):
    for expected in (1, 2, 3):
        resp = client.post("/api/orders", headers=auth_header(table_token), json={
            "items": [{"menu_item_id": seeded["item1_id"], "quantity": 1}]
        })
        assert resp.json()["order_number"] == expected


def test_empty_order_rejected(client, seeded, table_token):
    resp = client.post("/api/orders", headers=auth_header(table_token), json={"items": []})
    assert resp.status_code == 422


def test_order_status_change(client, seeded, table_token, admin_token):
    order_id = client.post("/api/orders", headers=auth_header(table_token), json={
        "items": [{"menu_item_id": seeded["item1_id"], "quantity": 1}]
    }).json()["id"]

    resp = client.patch(f"/api/admin/orders/{order_id}/status",
                        headers=auth_header(admin_token), json={"status": "준비중"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "준비중"


def test_invalid_status_rejected(client, seeded, table_token, admin_token):
    order_id = client.post("/api/orders", headers=auth_header(table_token), json={
        "items": [{"menu_item_id": seeded["item1_id"], "quantity": 1}]
    }).json()["id"]
    resp = client.patch(f"/api/admin/orders/{order_id}/status",
                        headers=auth_header(admin_token), json={"status": "취소됨"})
    assert resp.status_code == 422


def test_delete_order(client, seeded, table_token, admin_token):
    order_id = client.post("/api/orders", headers=auth_header(table_token), json={
        "items": [{"menu_item_id": seeded["item1_id"], "quantity": 1}]
    }).json()["id"]
    resp = client.delete(f"/api/admin/orders/{order_id}", headers=auth_header(admin_token))
    assert resp.status_code == 204


# ---------- 세션 라이프사이클 ----------
def test_checkout_archives_and_resets(client, seeded, table_token, admin_token):
    # 주문 2건 생성
    for _ in range(2):
        client.post("/api/orders", headers=auth_header(table_token), json={
            "items": [{"menu_item_id": seeded["item1_id"], "quantity": 1}]
        })
    # 현재 세션 주문 확인
    current = client.get("/api/orders/current", headers=auth_header(table_token)).json()
    assert len(current) == 2

    # 이용 완료
    resp = client.post(f"/api/admin/tables/{seeded['table_id']}/checkout",
                       headers=auth_header(admin_token))
    assert resp.status_code == 200
    assert resp.json()["archived_count"] == 2

    # 현재 세션 비워짐
    current_after = client.get("/api/orders/current", headers=auth_header(table_token)).json()
    assert current_after == []

    # 과거 내역에 2건
    history = client.get(f"/api/admin/tables/{seeded['table_id']}/history",
                         headers=auth_header(admin_token)).json()
    assert len(history) == 2


def test_new_session_after_checkout(client, seeded, table_token, admin_token):
    """이용 완료 후 새 주문은 새 세션에서 시작, 주문번호는 당일 연속."""
    o1 = client.post("/api/orders", headers=auth_header(table_token), json={
        "items": [{"menu_item_id": seeded["item1_id"], "quantity": 1}]
    }).json()
    client.post(f"/api/admin/tables/{seeded['table_id']}/checkout", headers=auth_header(admin_token))
    o2 = client.post("/api/orders", headers=auth_header(table_token), json={
        "items": [{"menu_item_id": seeded["item1_id"], "quantity": 1}]
    }).json()
    assert o2["session_id"] != o1["session_id"]


def test_table_summary(client, seeded, table_token, admin_token):
    client.post("/api/orders", headers=auth_header(table_token), json={
        "items": [{"menu_item_id": seeded["item1_id"], "quantity": 3}]  # 27000
    })
    resp = client.get("/api/admin/tables", headers=auth_header(admin_token))
    assert resp.status_code == 200
    summary = [t for t in resp.json() if t["table_id"] == seeded["table_id"]][0]
    assert summary["total_amount"] == 27000
    assert summary["session_active"] is True
