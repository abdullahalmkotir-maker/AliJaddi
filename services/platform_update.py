"""
فحص تحديثات المنصّة من GitHub Releases (اختياري — يفتح صفحة الإصدار للتنزيل اليدوي).
"""
from __future__ import annotations

from typing import NamedTuple

import httpx

from alijaddi import __version__

_GITHUB_API_LATEST = (
    "https://api.github.com/repos/abdullahalmkotir-maker/AliJaddi/releases/latest"
)


class ReleaseInfo(NamedTuple):
    ok: bool
    message: str
    tag_name: str
    html_url: str
    has_newer: bool


def check_platform_update(current: str | None = None) -> ReleaseInfo:
    cur = (current or __version__).strip()
    try:
        r = httpx.get(
            _GITHUB_API_LATEST,
            timeout=18,
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        r.raise_for_status()
        data = r.json()
        tag = (data.get("tag_name") or "").strip().lstrip("v")
        url = (data.get("html_url") or "").strip()
        if not tag:
            return ReleaseInfo(True, "لم يُعثر على رقم إصدار في آخر إصدار.", "", "", False)
        # مقارنة بسيطة: اختلاف السلسلة يُعتبر تحديثاً متاحاً (تكفي لبيتا)
        newer = tag != cur
        if newer:
            msg = f"يتوفر إصدار على GitHub: {tag} (المثبّت لديك: {cur})"
        else:
            msg = f"المنصّة محدّثة ({cur})."
        return ReleaseInfo(True, msg, tag, url, newer)
    except httpx.HTTPStatusError as e:
        return ReleaseInfo(False, f"HTTP {e.response.status_code}", "", "", False)
    except Exception as e:
        return ReleaseInfo(False, str(e), "", "", False)
