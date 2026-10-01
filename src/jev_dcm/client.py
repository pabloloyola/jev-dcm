from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class KevClient:
    base_url: str = "http://127.0.0.1:8009"
    model: str = "kev-latest"
    timeout: float = 120.0
    api_key: str | None = None

    def _headers(self) -> dict[str, str]:
        key = self.api_key or os.environ.get("KEV_API_KEY")
        return {"Authorization": f"Bearer {key}"} if key else {}

    def system_one(self, state: Any, questions: dict[str, dict[str, Any]]) -> dict[str, Any]:
        payload = {"state": state, "model": self.model, "questions": questions}
        url = self.base_url.rstrip("/") + "/v1/systemone"
        with httpx.Client(timeout=self.timeout, headers=self._headers()) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            body = response.json()
        if "answers" not in body:
            raise ValueError(f"Kev response has no answers: {body}")
        return body

    def models(self) -> dict[str, Any]:
        url = self.base_url.rstrip("/") + "/v1/models"
        with httpx.Client(timeout=self.timeout, headers=self._headers()) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.json()
