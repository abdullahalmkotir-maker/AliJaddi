# -*- coding: utf-8 -*-
from __future__ import annotations

from services.platform_release_download import pick_platform_asset


def _a(name: str, url: str) -> dict:
    return {"name": name, "browser_download_url": url}


def test_pick_setup_on_windows_auto():
    assets = [
        _a("other.txt", "https://x/t.txt"),
        _a("AliJaddi-Beta-0.5.2-Setup.exe", "https://x/setup.exe"),
        _a("AliJaddi-Beta-0.5.2-Windows.zip", "https://x/z.zip"),
    ]
    got = pick_platform_asset(assets, prefer="auto", is_windows=True)
    assert got == ("AliJaddi-Beta-0.5.2-Setup.exe", "https://x/setup.exe")


def test_pick_zip_when_no_setup_auto_win():
    assets = [_a("AliJaddi-Beta-0.5.2-Windows.zip", "https://x/z.zip")]
    got = pick_platform_asset(assets, prefer="auto", is_windows=True)
    assert got == ("AliJaddi-Beta-0.5.2-Windows.zip", "https://x/z.zip")


def test_pick_zip_non_windows_auto():
    assets = [
        _a("AliJaddi-Beta-0.5.2-Setup.exe", "https://x/setup.exe"),
        _a("AliJaddi-Beta-0.5.2-Windows.zip", "https://x/z.zip"),
    ]
    got = pick_platform_asset(assets, prefer="auto", is_windows=False)
    assert got == ("AliJaddi-Beta-0.5.2-Windows.zip", "https://x/z.zip")


def test_pick_explicit_setup():
    assets = [
        _a("AliJaddi-Beta-0.5.2-Setup.exe", "https://x/s.exe"),
        _a("AliJaddi-Beta-0.5.2-Windows.zip", "https://x/z.zip"),
    ]
    assert pick_platform_asset(assets, prefer="setup", is_windows=False) == (
        "AliJaddi-Beta-0.5.2-Setup.exe",
        "https://x/s.exe",
    )


def test_pick_empty():
    assert pick_platform_asset([], prefer="auto", is_windows=True) is None


def test_pick_fallback_generic_setup_zip():
    assets = [
        _a("AliJaddi_Setup.exe", "https://x/s.exe"),
    ]
    assert pick_platform_asset(assets, prefer="auto", is_windows=True) == (
        "AliJaddi_Setup.exe",
        "https://x/s.exe",
    )


def test_pick_rejects_unrelated_model_zip():
    assets = [_a("euqid.zip", "https://x/z.zip")]
    assert pick_platform_asset(assets, prefer="auto", is_windows=True) is None
