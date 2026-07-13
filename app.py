from __future__ import annotations

import os
import time
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from pipeline import CharacterPipeline

app = FastAPI(title="app.nz character Cog starter", version="0.1.0", openapi_url=None)
pipeline = CharacterPipeline()

COG_SCHEMA: dict[str, Any] = {
    "outputKind": "json",
    "inputs": [
        {"name": "portrait", "type": "image", "description": "Source character portrait", "required": True, "order": 0},
        {"name": "audio", "type": "audio", "description": "Optional driving speech or music", "order": 1},
        {"name": "driving_video", "type": "video", "description": "Optional pose/expression driver", "order": 2},
        {"name": "prompt", "type": "string", "description": "Motion and style direction", "default": "natural expression", "order": 3},
        {"name": "seed", "type": "integer", "default": 0, "min": 0, "max": 2147483647, "order": 4},
        {"name": "quality", "type": "string", "choices": ["fast", "quality"], "default": "fast", "order": 5},
    ],
}


class PredictionRequest(BaseModel):
    input: dict[str, Any] = Field(default_factory=dict)


@app.get("/health-check")
def health_check() -> dict[str, str]:
    return {"status": "READY" if pipeline.ready else "SETUP"}


@app.get("/openapi.json", include_in_schema=False)
def cog_schema() -> dict[str, Any]:
    return COG_SCHEMA


@app.post("/predictions")
def predictions(request: PredictionRequest) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        output = pipeline.predict(request.input)
        output["timing_ms"] = round((time.perf_counter() - started) * 1000, 2)
        return {"status": "succeeded", "output": output}
    except (TypeError, ValueError) as exc:
        return {"status": "failed", "error": str(exc)}
    except Exception as exc:  # keep provider errors useful without leaking a traceback
        if os.getenv("APPNZ_DEBUG") == "1":
            raise
        return {"status": "failed", "error": f"inference failed: {type(exc).__name__}"}
