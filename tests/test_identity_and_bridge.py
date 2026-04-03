"""هوية بصرية وجسر Qt للتطبيقات الفرعية."""
from __future__ import annotations

import os

import pytest

from alijaddi.visual_identity import theme_tokens, parse_theme_from_env, D_BG, L_BG


def test_theme_tokens_dark_light():
    assert theme_tokens(True)["bg"] == D_BG
    assert theme_tokens(False)["bg"] == L_BG
    assert theme_tokens(True)["primary"] != theme_tokens(False)["primary"]


def test_parse_theme_env():
    assert parse_theme_from_env("dark") is True
    assert parse_theme_from_env("LIGHT") is False
    assert parse_theme_from_env(None) is None
    assert parse_theme_from_env("") is None


def test_fusion_stylesheet_non_empty():
    from alijaddi.qt_host_bridge import fusion_stylesheet_for_host

    q = fusion_stylesheet_for_host(True)
    assert D_BG in q
    assert "QMainWindow" in q


@pytest.mark.parametrize("host_val,expected", [("1", True), ("true", True), ("0", False), ("", False)])
def test_is_hosted_launch(monkeypatch, host_val, expected):
    from alijaddi import qt_host_bridge

    monkeypatch.delenv("ALIJADDI_PLATFORM_HOST", raising=False)
    if host_val != "":
        monkeypatch.setenv("ALIJADDI_PLATFORM_HOST", host_val)
    assert qt_host_bridge.is_hosted_launch() == expected


def test_apply_host_theme_smoke():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    from alijaddi.qt_host_bridge import apply_host_theme

    assert apply_host_theme(app, dark=True) is True
    assert len(app.styleSheet()) > 50
    app.quit()
