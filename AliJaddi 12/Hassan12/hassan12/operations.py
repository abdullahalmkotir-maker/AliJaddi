# -*- coding: utf-8 -*-
from __future__ import annotations

import shutil
from pathlib import Path

from hassan12.policy_store import PendingRequest, RequestKind


class PolicyError(RuntimeError):
    pass


def execute_approved(req: PendingRequest) -> None:
    if req.status != "approved":
        raise PolicyError("التنفيذ مسموح فقط لطلبات حالتها: معتمد.")
    src = Path(req.source)
    if not src.exists():
        raise FileNotFoundError(str(src))

    kind = RequestKind(req.kind)
    if kind == RequestKind.DELETE:
        if src.is_dir():
            shutil.rmtree(src)
        else:
            src.unlink()
    elif kind == RequestKind.MOVE:
        dst = Path(req.destination)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
    elif kind == RequestKind.SEND:
        dst = Path(req.destination)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
    else:
        raise PolicyError(f"نوع غير معروف: {req.kind}")
