import json
import re
import httpx
from app.core.config import settings


class LLMService:
    @property
    def available(self) -> bool:
        return bool(settings.llm_api_key.strip())

    def _extract_json(self, text: str):
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.S)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start, end = text.find("{"), text.rfind("}")
            if start >= 0 and end > start:
                return json.loads(text[start:end + 1])
            raise

    def complete(self, system: str, user: str, temperature: float = 0.1) -> str:
        if not self.available:
            return ""
        url = settings.llm_base_url.rstrip("/") + "/chat/completions"
        headers = {"Authorization": f"Bearer {settings.llm_api_key}", "Content-Type": "application/json"}
        body = {
            "model": settings.llm_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
        }
        with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
            r = client.post(url, headers=headers, json=body)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]

    def complete_json(self, system: str, user: str, fallback: dict) -> dict:
        if not self.available:
            return fallback
        strict_system = system + "\nReturn ONLY valid JSON. Do not wrap it in markdown."
        try:
            raw = self.complete(strict_system, user)
            data = self._extract_json(raw)
            return data if isinstance(data, dict) else fallback
        except Exception:
            return fallback


llm = LLMService()
