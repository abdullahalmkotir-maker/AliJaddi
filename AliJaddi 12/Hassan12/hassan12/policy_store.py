# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class RequestKind(str, Enum):
    DELETE = "delete"
    MOVE = "move"
    SEND = "send"


@dataclass
class PendingRequest:
    id: str
    kind: str
    source: str
    destination: str
    reason: str
    created_utc: str
    status: str = "pending"
    approver: str = ""
    approved_utc: str = ""


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class PolicyStore:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.pending_path = self.base_dir / "pending_approvals.json"
        self.audit_path = self.base_dir / "audit_log.jsonl"

    def _load_pending(self) -> list[dict[str, Any]]:
        if not self.pending_path.is_file():
            return []
        try:
            data = json.loads(self.pending_path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

    def _save_pending(self, items: list[dict[str, Any]]) -> None:
        self.pending_path.write_text(
            json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def enqueue(
        self,
        kind: RequestKind,
        source: Path,
        destination: Path | None,
        reason: str,
    ) -> PendingRequest:
        req = PendingRequest(
            id=str(uuid.uuid4()),
            kind=kind.value,
            source=str(source.resolve()),
            destination=str(destination.resolve()) if destination else "",
            reason=reason.strip(),
            created_utc=_utc_now(),
        )
        items = self._load_pending()
        items.append(asdict(req))
        self._save_pending(items)
        self._audit(
            "enqueued",
            {
                "id": req.id,
                "kind": req.kind,
                "source": req.source,
                "destination": req.destination,
                "reason": req.reason,
            },
        )
        return req

    def list_pending(self) -> list[PendingRequest]:
        out: list[PendingRequest] = []
        for d in self._load_pending():
            st = d.get("status", "pending")
            if st in ("pending", "approved"):
                out.append(
                    PendingRequest(
                        id=d["id"],
                        kind=d["kind"],
                        source=d["source"],
                        destination=d.get("destination", ""),
                        reason=d.get("reason", ""),
                        created_utc=d.get("created_utc", ""),
                        status=st,
                        approver=d.get("approver", ""),
                        approved_utc=d.get("approved_utc", ""),
                    )
                )
        return out

    def approve(self, req_id: str, approver_name: str) -> PendingRequest | None:
        items = self._load_pending()
        found: PendingRequest | None = None
        for d in items:
            if d.get("id") == req_id and d.get("status") == "pending":
                d["status"] = "approved"
                d["approver"] = approver_name.strip()
                d["approved_utc"] = _utc_now()
                found = PendingRequest(
                    id=d["id"],
                    kind=d["kind"],
                    source=d["source"],
                    destination=d.get("destination", ""),
                    reason=d.get("reason", ""),
                    created_utc=d.get("created_utc", ""),
                    status="approved",
                    approver=d["approver"],
                    approved_utc=d["approved_utc"],
                )
                break
        if found is None:
            return None
        self._save_pending(items)
        self._audit("approved", {"id": req_id, "approver": approver_name})
        return found

    def mark_done(self, req_id: str) -> None:
        items = self._load_pending()
        for d in items:
            if d.get("id") == req_id:
                d["status"] = "approved_done"
                break
        self._save_pending(items)
        self._audit("executed", {"id": req_id})

    def get_request(self, req_id: str) -> dict[str, Any] | None:
        for d in self._load_pending():
            if d.get("id") == req_id:
                return d
        return None

    def reject(self, req_id: str, approver_name: str, note: str = "") -> None:
        items = [d for d in self._load_pending() if d.get("id") != req_id]
        self._save_pending(items)
        self._audit(
            "rejected",
            {"id": req_id, "approver": approver_name, "note": note},
        )

    def _audit(self, event: str, payload: dict[str, Any]) -> None:
        line = json.dumps(
            {"t": _utc_now(), "event": event, **payload},
            ensure_ascii=False,
        )
        with self.audit_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
