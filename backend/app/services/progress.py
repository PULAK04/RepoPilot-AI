import json
import redis
from app.core.config import settings


class ProgressService:
    def __init__(self):
        self.redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)

    def set(self, analysis_id: int, progress: int, step: str, extra: dict | None = None):
        payload = {"analysis_id": analysis_id, "progress": progress, "step": step}
        if extra:
            payload.update(extra)
        self.redis.setex(f"analysis:{analysis_id}:progress", 60 * 60 * 12, json.dumps(payload))
        self.redis.publish(f"analysis:{analysis_id}:events", json.dumps(payload))

    def get(self, analysis_id: int) -> dict | None:
        raw = self.redis.get(f"analysis:{analysis_id}:progress")
        return json.loads(raw) if raw else None


progress_service = ProgressService()
