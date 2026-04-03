"""اختبارات تجهيز أوامر التشغيل — بدون Qt."""
from __future__ import annotations

import pytest

from services.shell_launch import prepare_shell_command


def test_prepare_empty():
    assert prepare_shell_command("") == ""
    assert prepare_shell_command("   ") == ""


def test_streamlit_adds_headless_and_stats():
    s = prepare_shell_command("streamlit run app.py")
    assert "streamlit run app.py" in s
    assert "--server.headless true" in s
    assert "--browser.gatherUsageStats false" in s


def test_streamlit_idempotent():
    s = prepare_shell_command(
        "streamlit run main.py --server.headless true --browser.gatherUsageStats false"
    )
    assert s.count("--server.headless") == 1


def test_python_rewritten(monkeypatch):
    def _which(name):
        if name == "python":
            return r"C:\Test\python.exe"
        return None

    monkeypatch.setattr("services.shell_launch.shutil.which", _which)
    s = prepare_shell_command("python app.py")
    assert r'"C:\Test\python.exe"' in s
    assert s.endswith("app.py")


def test_python3_rewritten(monkeypatch):
    def _which(name):
        if name == "python":
            return r"C:\Test\python3alias.exe"
        if name == "python3":
            return None
        return None

    monkeypatch.setattr("services.shell_launch.shutil.which", _which)
    s = prepare_shell_command("python3 app.py")
    assert r'"C:\Test\python3alias.exe"' in s
    assert "app.py" in s


def test_python3_streamlit_gets_headless(monkeypatch):
    def _which(name):
        if name == "python":
            return r"/usr/bin/python3"
        return None

    monkeypatch.setattr("services.shell_launch.shutil.which", _which)
    s = prepare_shell_command("python3 -m streamlit run app.py")
    assert "--server.headless true" in s


def test_python_falls_back_to_py_launcher_on_windows(monkeypatch):
    def _which(name):
        if name == "python":
            return None
        if name == "python3":
            return None
        if name == "py":
            return r"C:\Windows\py.exe"
        return None

    monkeypatch.setattr("services.shell_launch.shutil.which", _which)
    monkeypatch.setattr("services.shell_launch.os.name", "nt")
    s = prepare_shell_command("python -m mypkg")
    assert "py.exe" in s
    assert "-3" in s
    assert "mypkg" in s
