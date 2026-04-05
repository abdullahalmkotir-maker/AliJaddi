# -*- coding: utf-8 -*-
"""
بيانات ومسارات **قديمة** لعلي جدّي — لا تُحذف؛ تُقرأ للتوافق والاستفادة من تثبيتات سابقة.

- ``تطبيقات علي جدي`` على سطح المكتب (حاضنة قديمة).
- مجلدات التطبيق باسم ``manifest.folder`` مباشرة على سطح المكتب.

المسار الحالي للمتجر: ``~/.alijaddi/downloads`` (يُفضَّل لكل تثبيت جديد).
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

# اسم الحاضنة القديمة — يبقى ثابتاً لأن المستخدمين قد يملكون مجلداً بهذا الاسم
LEGACY_DESKTOP_HOST_DIR_NAME = "تطبيقات علي جدي"

# وسم يُسجَّل في التتبع/التدريب لمعرفة مصدر المسار
SOURCE_STORE_DOWNLOADS = "store_downloads"
SOURCE_LEGACY_DESKTOP_HOST = "legacy_desktop_host"
SOURCE_LEGACY_DESKTOP_FLAT = "legacy_desktop_flat"


def desktop_candidates() -> list[Path]:
    """سطح المكتب (OneDrive ثم Desktop) إن وُجد."""
    home = Path.home()
    out: list[Path] = []
    for d in (home / "OneDrive" / "Desktop", home / "Desktop"):
        if d.is_dir():
            try:
                out.append(d.resolve())
            except OSError:
                out.append(d)
    return out


def legacy_host_roots() -> list[Path]:
    """جذور ``…/Desktop/تطبيقات علي جدي`` الموجودة فعلياً."""
    roots: list[Path] = []
    for d in desktop_candidates():
        h = d / LEGACY_DESKTOP_HOST_DIR_NAME
        if h.is_dir():
            roots.append(h.resolve())
    return roots


def iter_legacy_app_locations(folder_name: str) -> list[tuple[Path, str]]:
    """
    مواقع **قديمة** فقط (بدون ``~/.alijaddi/downloads``).
    تُرجع قائمة (مسار، وسوم_المصدر) بترتيب الأولوية للعرض/الدمج.
    """
    name = (folder_name or "").strip()
    if not name:
        return []
    out: list[tuple[Path, str]] = []
    for d in desktop_candidates():
        old_host = d / LEGACY_DESKTOP_HOST_DIR_NAME / name
        if old_host.is_dir():
            out.append((old_host.resolve(), SOURCE_LEGACY_DESKTOP_HOST))
        flat = d / name
        if flat.is_dir() and flat.resolve() not in {p for p, _ in out}:
            # تجنّب تكرار إن كان نفس المسار
            out.append((flat.resolve(), SOURCE_LEGACY_DESKTOP_FLAT))
    return out


def resolve_app_path_with_source(folder_name: str, downloads_root: Path) -> tuple[Path, str]:
    """
    يحدد مسار تطبيق مثبّت والمصدر: مدير التنزيلات الحالي ثم مسارات قديمة.
    ``downloads_root`` يُمرَّر من ``paths.apps_root()`` لتفادي استيراد دائري.
    """
    name = (folder_name or "").strip()
    primary = downloads_root / name
    if primary.is_dir():
        return primary.resolve(), SOURCE_STORE_DOWNLOADS
    for path, tag in iter_legacy_app_locations(name):
        if path.is_dir():
            return path, tag
    return primary.resolve(), SOURCE_STORE_DOWNLOADS


def iter_legacy_install_entries(*, max_per_root: int = 500) -> Iterator[dict[str, str]]:
    """
    يمرّ على الحاضنة القديمة ومجلدات سطح المكتب «المسطّحة» ويُنتج صفوفاً للأدوات/التدريب.
    كل عنصر: name, path, source
    """
    seen: set[str] = set()
    for root in legacy_host_roots():
        try:
            subs = sorted(root.iterdir(), key=lambda x: x.name.lower())
        except OSError:
            continue
        n = 0
        for p in subs:
            if n >= max_per_root:
                break
            if not p.is_dir() or p.name.startswith("."):
                continue
            key = f"{SOURCE_LEGACY_DESKTOP_HOST}:{p.resolve()}"
            if key in seen:
                continue
            seen.add(key)
            yield {
                "name": p.name,
                "path": str(p.resolve()),
                "source": SOURCE_LEGACY_DESKTOP_HOST,
            }
            n += 1


def legacy_summary() -> dict[str, object]:
    """ملخص سريع لمسارات قديمة (تشخيص، سكربتات)."""
    hosts = legacy_host_roots()
    return {
        "legacy_desktop_host_name": LEGACY_DESKTOP_HOST_DIR_NAME,
        "legacy_host_roots": [str(p) for p in hosts],
        "desktop_candidates": [str(p) for p in desktop_candidates()],
    }
