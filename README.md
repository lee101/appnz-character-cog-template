# app.nz character Cog template

[![CI](https://github.com/lee101/appnz-character-cog-template/actions/workflows/ci.yml/badge.svg)](https://github.com/lee101/appnz-character-cog-template/actions/workflows/ci.yml)
[![Deploy to app.nz](https://app.nz/deploy-button.svg)](https://app.nz/deploy?image=ghcr.io/lee101/appnz-character-cog-template:latest&name=character-cog-starter&hardware=gpu-l40s&minVramGb=24&idleSeconds=120)

A tiny MIT-licensed starter for turning portrait-animation, lip-sync, voice, and
3D character research into a scale-to-zero app.nz endpoint. The repository is
deliberately a working contract shell, not a disguised model demo: CI performs
no model download and spends no GPU time. Replace `CharacterPipeline` with the
specific upstream model, then update the schema, sizing, provenance, and badge.

## Contract

The FastAPI server listens on port 5000:

- `GET /health-check` reports `SETUP` or `READY`;
- `GET /openapi.json` returns the app.nz generated-UI schema;
- `POST /predictions` accepts `{ "input": { ... } }` and returns a Cog-style
  success/error envelope.

The starter schema supports a portrait plus either audio or a driving video,
with bounded seed/quality controls. It returns deterministic JSON until a model
adapter replaces the marked section in `pipeline.py`.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest -q
uvicorn app:app --host 0.0.0.0 --port 5000

curl -sS localhost:5000/predictions \
  -H 'Content-Type: application/json' \
  -d '{"input":{"portrait":"https://example.test/face.png","audio":"https://example.test/voice.wav"}}'
```

## Add a model

1. Pin the upstream commit and Python/CUDA/XLA stack.
2. Load weights and compile common shapes in `CharacterPipeline.__init__`;
   keep `ready=False` until warm-up is complete.
3. Return a public output URL or a `data:<mime>;base64,...` URI. Change
   `outputKind` to `video`, `image`, `audio`, or `model3d` as appropriate.
4. Add hard limits for resolution, duration, frames, steps, and batch size.
5. Measure image pull, setup, first inference, steady inference, and peak VRAM.
6. Update `appnz.template.json` and the badge with the smallest truthful GPU.

For large/frequently changing weights, use the persistent model cache with a
content checksum. For small stable weights, a separate Docker layer can produce
faster deterministic cold starts. Do not install packages or download unbounded
weights during every container boot.

## Provenance checklist

Fill this in before publishing a model image:

| Item | Required value |
| --- | --- |
| Upstream repository + commit | TODO |
| Code license | TODO |
| Weights source + checksum | TODO |
| Weights license / hosted-inference permission | TODO |
| Training-data caveats | TODO |
| Tested accelerator, runtime, peak VRAM | TODO |
| Cold start / first / steady inference | TODO |
| Consent, identity, and watermark policy | TODO |

Character systems can enable impersonation. Deployments should require rights
to source likeness/audio, preserve upstream safety notices, and clearly label
synthetic output where appropriate.

## Publishing

Pushes to `main` test the HTTP contract, build the container, and publish tagged
images to GHCR. Make the package public before using the one-click badge. app.nz
defaults the deployed Cog to 120 seconds idle and tears the backing machine down
when idle.

License: MIT. Upstream model code and weights retain their own licenses.
