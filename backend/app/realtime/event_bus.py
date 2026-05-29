"""인메모리 Publish/Subscribe 이벤트 버스.

토픽별로 asyncio.Queue 구독자를 관리하며, 변경 발생 시 즉시 push 합니다.
단일 프로세스 전제(로컬 실행). (nfr-design/logical-components.md 참조)
"""
import asyncio
from collections import defaultdict


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, set[asyncio.Queue]] = defaultdict(set)

    def subscribe(self, topic: str) -> asyncio.Queue:
        """토픽을 구독하고 이벤트를 받을 큐를 반환한다."""
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers[topic].add(queue)
        return queue

    def unsubscribe(self, topic: str, queue: asyncio.Queue) -> None:
        """구독을 해제한다 (BR-RT-4: 연결 종료 시 정리)."""
        subs = self._subscribers.get(topic)
        if subs and queue in subs:
            subs.discard(queue)
            if not subs:
                self._subscribers.pop(topic, None)

    async def publish(self, topic: str, event: dict) -> None:
        """토픽 구독자 전원에게 이벤트를 전달한다 (BR-RT-1~3)."""
        for queue in list(self._subscribers.get(topic, set())):
            await queue.put(event)

    def subscriber_count(self, topic: str) -> int:
        """해당 토픽 구독자 수 (테스트/모니터링용)."""
        return len(self._subscribers.get(topic, set()))


# 애플리케이션 전역 단일 인스턴스
event_bus = EventBus()


def store_topic(store_id: int) -> str:
    return f"store:{store_id}"


def table_topic(table_id: int) -> str:
    return f"table:{table_id}"
