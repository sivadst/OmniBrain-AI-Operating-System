from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import asyncio
from sse_starlette.sse import EventSourceResponse
from app.core.database import redis_pool
from redis.asyncio import Redis

router = APIRouter()

async def redis_event_generator(task_id: str):
    client = Redis(connection_pool=redis_pool)
    pubsub = client.pubsub()
    channel = f"task_events:{task_id}"
    await pubsub.subscribe(channel)
    
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                data = message['data']
                if data == "END_STREAM":
                    break
                yield {"data": data}
            else:
                await asyncio.sleep(0.1)
    finally:
        await pubsub.unsubscribe(channel)
        await client.aclose()

@router.get("/{task_id}/stream")
async def stream_task_events(task_id: str):
    """Server-Sent Events endpoint connected to Redis PubSub for task logs."""
    return EventSourceResponse(redis_event_generator(task_id))
