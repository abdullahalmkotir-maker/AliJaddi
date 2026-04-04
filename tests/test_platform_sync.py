# -*- coding: utf-8 -*-
"""تحقق التزامن الكامل بين manifest والسرب وBento routing."""
from __future__ import annotations

from services.platform_sync import full_platform_sync


def test_full_platform_sync_ok():
    r = full_platform_sync()
    assert r["ok"], f"sync failed: {r.get('errors')}"
