# -*- coding: utf-8 -*-
"""مراقبة اختيارية للمجلد المحمي — تسجيل الأحداث دون حظر نظام التشغيل."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
except ImportError:
    FileSystemEventHandler = object  # type: ignore[misc, assignment]
    Observer = None  # type: ignore[misc, assignment]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class _Handler(FileSystemEventHandler):  # type: ignore[misc]
    def __init__(self, log_path: Path) -> None:
        super().__init__()
        self.log_path = log_path

    def on_any_event(self, event):  # type: ignore[no-untyped-def]
        if event.is_directory and event.event_type in ("opened", "closed_no_write"):
            return
        line = json.dumps(
            {
                "t": _utc_now(),
                "type": event.event_type,
                "src": getattr(event, "src_path", ""),
                "dest": getattr(event, "dest_path", None),
            },
            ensure_ascii=False,
        )
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


def start_watching(root: Path) -> Observer | None:
    if Observer is None:
        return None
    root = Path(root).resolve()
    log_path = root / ".hassan12_watch.jsonl"
    handler = _Handler(log_path)
    observer = Observer()
    observer.schedule(handler, str(root), recursive=True)
    observer.start()
    return observer
