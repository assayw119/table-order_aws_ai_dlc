"""SSE 스트림 라우터: 관리자/고객 실시간 이벤트 전달.

브라우저 EventSource는 커스텀 헤더를 설정할 수 없으므로, 토큰을 쿼리
파라미터로 받아 검증한다.
"""
import asyncio
import json

from fastapi import APIRouter, HTTPException, Request, status
from jose import JWTError
from sse_starlette.sse import EventSourceResponse

from app.core.security import decode_token
from app.realtime.event_bus import event_bus, store_topic, table_topic

router = APIRouter(tags=["realtime"])


def _decode_query_token(token: str, expected_role: str) -> dict:
    """쿼리 파라미터 토큰을 검증하고 역할을 확인한다."""
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않거나 만료된 토큰입니다.")
    if payload.get("role") != expected_role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")
    return payload

# SSE 하트비트 주기 (초)
HEARTBEAT_INTERVAL = 15


async def _event_stream(request: Request, topic: str):
    """구독 큐에서 이벤트를 받아 SSE로 스트리밍한다."""
    queue = event_bus.subscribe(topic)
    try:
        while True:
            if await request.is_disconnected():
                break
            try:
                event = await asyncio.wait_for(queue.get(), timeout=HEARTBEAT_INTERVAL)
                yield {"event": event.get("type", "message"), "data": json.dumps(event, ensure_ascii=False)}
            except asyncio.TimeoutError:
                # keep-alive 코멘트 (BR-RT, 연결 유지)
                yield {"event": "ping", "data": "{}"}
    finally:
        event_bus.unsubscribe(topic, queue)


@router.get("/api/admin/stream")
async def admin_stream(request: Request, token: str):
    """관리자 매장 전체 주문 이벤트 스트림 (US-A2, US-T1)."""
    payload = _decode_query_token(token, "admin")
    topic = store_topic(payload["store_id"])
    return EventSourceResponse(_event_stream(request, topic))


@router.get("/api/table/stream")
async def table_stream(request: Request, token: str):
    """고객 테이블 세션 이벤트 스트림 (US-C5, US-T1)."""
    payload = _decode_query_token(token, "table")
    topic = table_topic(payload["table_id"])
    return EventSourceResponse(_event_stream(request, topic))
