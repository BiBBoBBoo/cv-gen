from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.models.cv import CVData, cv_from_dict


def draft_json(data: CVData) -> str:
    return json.dumps(data.to_dict(), indent=2, ensure_ascii=True)


def load_draft_json(raw: str | bytes) -> CVData:
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    return cv_from_dict(json.loads(raw))


def save_local_draft(data: CVData, path: str | Path = "cv_draft.json") -> None:
    Path(path).write_text(draft_json(data), encoding="utf-8")
