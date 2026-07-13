from __future__ import annotations

from typing import Any
from urllib.parse import urlparse


class CharacterPipeline:
    """Replace this deterministic adapter with LivePortrait, MuseTalk, etc."""

    def __init__(self) -> None:
        # Load weights and compile common shapes here. Keep ready=False until the
        # model can accept a prediction; app.nz polls /health-check during setup.
        self.ready = True

    def predict(self, inputs: dict[str, Any]) -> dict[str, Any]:
        portrait = self._media_url(inputs.get("portrait"), "portrait", required=True)
        audio = self._media_url(inputs.get("audio"), "audio")
        driving_video = self._media_url(inputs.get("driving_video"), "driving_video")
        if not audio and not driving_video:
            raise ValueError("one of audio or driving_video is required")

        quality = inputs.get("quality", "fast")
        if quality not in {"fast", "quality"}:
            raise ValueError("quality must be fast or quality")

        # The starter intentionally performs no network fetch or GPU work. Swap
        # this return for a CDN-safe data URI or public output URL after running
        # the model. Keeping the shell deterministic makes contract CI cheap.
        return {
            "adapter": "replace-me",
            "portrait": portrait,
            "driver": audio or driving_video,
            "driver_kind": "audio" if audio else "video",
            "prompt": str(inputs.get("prompt", "natural expression"))[:500],
            "seed": int(inputs.get("seed", 0)),
            "quality": quality,
        }

    @staticmethod
    def _media_url(value: Any, name: str, required: bool = False) -> str:
        if value in (None, ""):
            if required:
                raise ValueError(f"{name} is required")
            return ""
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a URL or data URI")
        if value.startswith("data:"):
            return value
        parsed = urlparse(value)
        if parsed.scheme not in {"https", "http"} or not parsed.netloc:
            raise ValueError(f"{name} must be an http(s) URL or data URI")
        return value
