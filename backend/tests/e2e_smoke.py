"""종단간(E2E) 스모크 테스트: 실행 중인 서버에 실제 HTTP/SSE 호출.

사전 조건: uvicorn 서버가 http://localhost:8000 에서 실행 중이고 seed 완료.
실행: .venv/bin/python -m tests.e2e_smoke
"""
import json
import threading
import time
import urllib.request
import urllib.error

BASE = "http://localhost:8000"


def http(method, path, body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            text = resp.read().decode()
            return resp.status, json.loads(text) if text else None
    except urllib.error.HTTPError as e:
        return e.code, None


def sse_listen(path, token, collected, stop_after=1):
    """SSE 스트림에서 이벤트를 수신하여 collected에 적재."""
    url = f"{BASE}{path}?token={token}"
    req = urllib.request.Request(url, headers={"Accept": "text/event-stream"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            event_type = None
            for raw in resp:
                line = raw.decode().strip()
                if line.startswith("event:"):
                    event_type = line.split(":", 1)[1].strip()
                elif line.startswith("data:"):
                    payload = line.split(":", 1)[1].strip()
                    if event_type and event_type != "ping":
                        collected.append((event_type, payload))
                        if len(collected) >= stop_after:
                            return
    except Exception:
        return


def main():
    results = []

    def check(name, cond):
        results.append((name, cond))
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    # 헬스
    status, _ = http("GET", "/api/health")
    check("health 200", status == 200)

    # 관리자 로그인
    status, admin = http("POST", "/api/auth/admin/login",
                         {"store_code": "store001", "username": "admin", "password": "admin1234"})
    check("admin login 200", status == 200 and admin and "access_token" in admin)
    admin_token = admin["access_token"]

    # 테이블 로그인
    status, table = http("POST", "/api/auth/table/login",
                         {"store_code": "store001", "table_number": 2, "table_password": "table1234"})
    check("table login 200", status == 200)
    table_token = table["access_token"]

    # 메뉴 조회
    status, items = http("GET", "/api/menu/items", token=table_token)
    check("menu items >0", status == 200 and len(items) > 0)
    menu_id = items[0]["id"]
    menu_price = items[0]["price"]

    # 관리자 SSE 구독 시작 (백그라운드)
    admin_events = []
    t = threading.Thread(target=sse_listen, args=("/api/admin/stream", admin_token, admin_events, 1))
    t.start()
    time.sleep(1.0)  # 구독 연결 대기

    # 주문 생성
    t0 = time.time()
    status, order = http("POST", "/api/orders",
                         {"items": [{"menu_item_id": menu_id, "quantity": 2}]}, token=table_token)
    check("order created 201", status == 201)
    check("order total correct", order and order["total_amount"] == menu_price * 2)

    # SSE 이벤트 수신 확인 (2초 이내 - NFR-P1)
    t.join(timeout=3)
    elapsed = time.time() - t0
    check("admin SSE received order_created", any(e[0] == "order_created" for e in admin_events))
    check("SSE within 2s (NFR-P1)", elapsed < 2.0 and len(admin_events) > 0)

    # 상태 변경
    status, updated = http("PATCH", f"/api/admin/orders/{order['id']}/status",
                          {"status": "준비중"}, token=admin_token)
    check("status change 200", status == 200 and updated["status"] == "준비중")

    # 현재 세션 주문 조회
    status, current = http("GET", "/api/orders/current", token=table_token)
    check("current session has order", status == 200 and len(current) >= 1)

    # 이용 완료
    status, checkout = http("POST", f"/api/admin/tables/{table['table_id']}/checkout", {}, token=admin_token)
    check("checkout 200", status == 200 and checkout["archived_count"] >= 1)

    # 이용 완료 후 현재 세션 비워짐
    status, current_after = http("GET", "/api/orders/current", token=table_token)
    check("session reset after checkout", status == 200 and len(current_after) == 0)

    # 과거 내역 존재
    status, history = http("GET", f"/api/admin/tables/{table['table_id']}/history", token=admin_token)
    check("history has archived order", status == 200 and len(history) >= 1)

    passed = sum(1 for _, c in results if c)
    total = len(results)
    print(f"\nE2E 결과: {passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
