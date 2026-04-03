"""اكتشاف المشاريع الشقيقة والتحقق من وجودها."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .config import PLATFORM_ROOT, account_project_root, cloud_project_root


@dataclass
class ProjectProbe:
    role: str
    path: Path
    exists: bool
    markers: List[str]

    def ok(self) -> bool:
        return self.exists and all((self.path / m).exists() for m in self.markers)


def probe_cloud(root: Optional[Path] = None) -> ProjectProbe:
    p = root or cloud_project_root()
    return ProjectProbe(
        role="AliJaddi Cloud",
        path=p,
        exists=p.is_dir(),
        markers=["supabase/migrations", "README.md"],
    )


def probe_account(root: Optional[Path] = None) -> ProjectProbe:
    p = root or account_project_root()
    return ProjectProbe(
        role="AliJaddiAccount",
        path=p,
        exists=p.is_dir(),
        markers=["auth_model/cloud_client.py", "config.py"],
    )


def workspace_report() -> str:
    lines = [
        f"AliJaddi platform root: {PLATFORM_ROOT}",
        "",
    ]
    for pr in (probe_cloud(), probe_account()):
        status = "OK" if pr.ok() else "MISSING / incomplete"
        lines.append(f"[{status}] {pr.role}")
        lines.append(f"    path: {pr.path}")
        if pr.exists and not pr.ok():
            missing = [m for m in pr.markers if not (pr.path / m).exists()]
            lines.append(f"    missing: {', '.join(missing)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
