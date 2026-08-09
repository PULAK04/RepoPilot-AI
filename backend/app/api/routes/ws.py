import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models import Analysis
from app.services.progress import progress_service

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/analyses/{analysis_id}")
async def analysis_ws(websocket: WebSocket, analysis_id: int):
    token = websocket.query_params.get("token", "")
    subject = decode_access_token(token)
    if not subject:
        await websocket.close(code=4401)
        return

    db = SessionLocal()
    try:
        analysis = db.get(Analysis, analysis_id)
        if not analysis or analysis.user_id != int(subject):
            await websocket.close(code=4404)
            return
    finally:
        db.close()

    await websocket.accept()
    last = None
    try:
        while True:
            current = progress_service.get(analysis_id)
            if current and current != last:
                await websocket.send_json(current)
                last = current
                if current.get("status") in {"completed", "failed"} or current.get("progress") == 100:
                    break
            await asyncio.sleep(0.8)
    except WebSocketDisconnect:
        return
