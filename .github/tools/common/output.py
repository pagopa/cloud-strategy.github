from __future__ import annotations

import json


def log_info(message: str) -> None:
    print(f"ℹ️  {message}", flush=True)


def log_warn(message: str) -> None:
    print(f"⚠️  {message}", flush=True)


def log_success(message: str) -> None:
    print(f"✅ {message}", flush=True)


def log_error(message: str) -> None:
    print(f"❌ {message}", flush=True)


def render_json(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True)
