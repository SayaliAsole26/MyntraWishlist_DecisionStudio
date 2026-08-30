"""Groq LLM adapter. Used offline (FAST) and online (QUALITY) from Phase 4."""

import logging
import time
from typing import Any

import httpx

from backend import config

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
logger = logging.getLogger("groq.usage")


class LlmNotConfiguredError(RuntimeError):
    pass


class LlmUnavailableError(RuntimeError):
    pass


class LlmClient:
    def __init__(self, api_key: str | None = None, timeout: float | None = None):
        self.api_key = (api_key if api_key is not None else config.GROQ_API_KEY).strip()
        self.timeout = timeout if timeout is not None else config.GROQ_TIMEOUT

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def complete(
        self,
        model: str,
        messages: list[dict[str, Any]],
        *,
        context: str | None = None,
    ) -> str:
        if not self.api_key:
            raise LlmNotConfiguredError(
                "GROQ_API_KEY is not set. Add it to .env for Phase 4 LLM features."
            )

        last_error: Exception | None = None
        for attempt in range(2):
            try:
                return self._request(model, messages, context=context)
            except LlmUnavailableError as exc:
                last_error = exc
                if attempt == 0 and "429" in str(exc):
                    time.sleep(1.5)
                    continue
                raise
        raise last_error or LlmUnavailableError("Groq request failed")

    def _request(
        self,
        model: str,
        messages: list[dict[str, Any]],
        *,
        context: str | None = None,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.2,
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(GROQ_CHAT_URL, headers=headers, json=payload)
        except httpx.TimeoutException as exc:
            raise LlmUnavailableError("Groq request timed out") from exc
        except httpx.HTTPError as exc:
            raise LlmUnavailableError(f"Groq HTTP error: {exc}") from exc

        if res.status_code == 429:
            raise LlmUnavailableError("Groq rate limited (429)")
        if res.status_code >= 400:
            raise LlmUnavailableError(f"Groq error {res.status_code}: {res.text[:200]}")

        data = res.json()
        usage = data.get("usage") or {}
        logger.info(
            "groq_call endpoint=%s model=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s",
            context or "unknown",
            model,
            usage.get("prompt_tokens"),
            usage.get("completion_tokens"),
            usage.get("total_tokens"),
        )

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LlmUnavailableError("Unexpected Groq response shape") from exc

    def complete_fast(
        self,
        messages: list[dict[str, Any]],
        *,
        context: str | None = None,
    ) -> str:
        return self.complete(config.GROQ_MODEL_FAST, messages, context=context)

    def complete_quality(
        self,
        messages: list[dict[str, Any]],
        *,
        context: str | None = None,
    ) -> str:
        return self.complete(config.GROQ_MODEL_QUALITY, messages, context=context)
