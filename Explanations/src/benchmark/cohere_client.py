from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from project_paths import EXPLANATIONS_ROOT, REPOSITORY_ROOT


class CohereClientError(RuntimeError):
    """Raised when the Cohere client cannot be initialized or used."""


@dataclass(frozen=True)
class CohereGenerationConfig:
    model: str = "command-a-03-2025"
    temperature: float = 0.2
    max_output_tokens: int = 1200
    response_format: Dict[str, str] = None

    def __post_init__(self) -> None:
        if self.response_format is None:
            object.__setattr__(self, "response_format", {"type": "json_object"})


@dataclass(frozen=True)
class CohereCallMetrics:
    provider: str
    model: str
    api_latency_s: float
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    total_tokens: Optional[int]
    prompt_chars: int
    response_chars: int
    response_id: Optional[str] = None
    usage_snapshot: Optional[Dict[str, Any]] = None
    meta_snapshot: Optional[Dict[str, Any]] = None


def build_generation_messages(prompt: str) -> List[Dict[str, str]]:
    prompt = prompt.strip()
    if not prompt:
        raise CohereClientError("Prompt cannot be empty.")
    return [{"role": "user", "content": prompt}]


def extract_text_from_cohere_response(response: Any) -> str:
    try:
        content = response.message.content
        if not content:
            raise CohereClientError("Cohere response has empty message content.")

        first_item = content[0]
        text = getattr(first_item, "text", None)
        if text is None:
            raise CohereClientError("Cohere response content does not contain text.")

        cleaned = text.strip()
        if not cleaned:
            raise CohereClientError("Cohere response text is empty.")

        return cleaned
    except AttributeError as exc:
        raise CohereClientError(
            "Unexpected Cohere response structure while extracting text."
        ) from exc


def _try_load_dotenv() -> None:
    try:
        from dotenv import load_dotenv  # type: ignore
    except ImportError:
        return

    for env_path in (REPOSITORY_ROOT / ".env", EXPLANATIONS_ROOT / ".env"):
        if env_path.exists():
            load_dotenv(env_path)
            return
    load_dotenv()


def _get_attr_or_key(obj: Any, name: str) -> Any:
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, None)


def _coerce_optional_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except Exception:  # noqa: BLE001
        return None


def _json_safe(value: Any) -> Any:
    """
    Convert arbitrary SDK objects into JSON-safe values.
    """
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v) for v in value]

    return repr(value)

def _shallow_debug_dict(obj: Any) -> Optional[Dict[str, Any]]:
    if obj is None:
        return None
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}

    result: Dict[str, Any] = {}
    for name in dir(obj):
        if name.startswith("_"):
            continue
        try:
            value = getattr(obj, name)
        except Exception:  # noqa: BLE001
            continue
        if callable(value):
            continue
        result[name] = _json_safe(value)

    return result or None

def extract_usage_metrics(response: Any) -> tuple[Optional[int], Optional[int], Optional[int]]:
    """
    Best-effort extraction of token usage from Cohere response metadata.
    Safe if the fields are absent or the SDK changes slightly.
    """
    usage = _get_attr_or_key(response, "usage")
    meta = _get_attr_or_key(response, "meta")

    usage_tokens = _get_attr_or_key(usage, "tokens")
    usage_billed_units = _get_attr_or_key(usage, "billed_units")
    meta_tokens = _get_attr_or_key(meta, "tokens")
    meta_billed_units = _get_attr_or_key(meta, "billed_units")

    input_tokens = (
        _coerce_optional_int(_get_attr_or_key(usage, "input_tokens"))
        or _coerce_optional_int(_get_attr_or_key(usage_tokens, "input_tokens"))
        or _coerce_optional_int(_get_attr_or_key(usage_billed_units, "input_tokens"))
        or _coerce_optional_int(_get_attr_or_key(meta_tokens, "input_tokens"))
        or _coerce_optional_int(_get_attr_or_key(meta_billed_units, "input_tokens"))
    )

    output_tokens = (
        _coerce_optional_int(_get_attr_or_key(usage, "output_tokens"))
        or _coerce_optional_int(_get_attr_or_key(usage_tokens, "output_tokens"))
        or _coerce_optional_int(_get_attr_or_key(usage_billed_units, "output_tokens"))
        or _coerce_optional_int(_get_attr_or_key(meta_tokens, "output_tokens"))
        or _coerce_optional_int(_get_attr_or_key(meta_billed_units, "output_tokens"))
    )

    total_tokens = (
        _coerce_optional_int(_get_attr_or_key(usage, "total_tokens"))
        or _coerce_optional_int(_get_attr_or_key(usage_tokens, "total_tokens"))
        or _coerce_optional_int(_get_attr_or_key(meta_tokens, "total_tokens"))
        or (
            input_tokens + output_tokens
            if input_tokens is not None and output_tokens is not None
            else None
        )
    )

    return input_tokens, output_tokens, total_tokens


class CohereCandidateGenerator:
    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[CohereGenerationConfig] = None,
    ) -> None:
        _try_load_dotenv()
        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        if not self.api_key:
            raise CohereClientError(
                "COHERE_API_KEY is not set. Export it in the environment before use."
            )

        self.config = config or CohereGenerationConfig()
        self.last_metrics: Optional[CohereCallMetrics] = None

        try:
            import cohere  # type: ignore
        except ImportError as exc:
            raise CohereClientError(
                "The 'cohere' package is not installed. Install it before using the Cohere client."
            ) from exc

        try:
            self._client = cohere.ClientV2(self.api_key)
        except Exception as exc:  # noqa: BLE001
            raise CohereClientError(
                f"Failed to initialize Cohere ClientV2: {exc}"
            ) from exc

    def generate_raw_json_text(self, prompt: str) -> str:
        messages = build_generation_messages(prompt)

        t0 = time.perf_counter()
        try:
            response = self._client.chat(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_output_tokens,
                response_format=self.config.response_format,
            )
        except Exception as exc:  # noqa: BLE001
            raise CohereClientError(f"Cohere chat request failed: {exc}") from exc
        latency_s = time.perf_counter() - t0

        raw_text = extract_text_from_cohere_response(response)
        input_tokens, output_tokens, total_tokens = extract_usage_metrics(response)

        response_id = _get_attr_or_key(response, "id")
        usage_snapshot = _shallow_debug_dict(_get_attr_or_key(response, "usage"))
        meta_snapshot = _shallow_debug_dict(_get_attr_or_key(response, "meta"))

        self.last_metrics = CohereCallMetrics(
            provider="cohere",
            model=self.config.model,
            api_latency_s=latency_s,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            prompt_chars=len(prompt),
            response_chars=len(raw_text),
            response_id=response_id,
            usage_snapshot=usage_snapshot,
            meta_snapshot=meta_snapshot,
        )

        return raw_text
