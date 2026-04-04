# -*- coding: utf-8 -*-
from __future__ import annotations

import Ali12 as ali12


def test_ali12_id_constant():
    assert ali12.ALI12_ASSISTANT_ID == "Ali12"


def test_suggest_no_url():
    s = ali12.suggest_after_install_failure(event_kind="install_no_url", message="", detail={})
    assert "رابط" in s or "تحميل" in s


def test_suggest_404():
    s = ali12.suggest_after_install_failure(
        event_kind="install_fail",
        message="HTTP 404",
        detail={"http_status": 404},
    )
    assert "404" in s


def test_resolve_ali12_has_engine_and_confidence():
    r = ali12.resolve_ali12(
        event_kind="install_no_url",
        message="",
        detail={},
    )
    assert r["rule_id"] == "install_no_url"
    assert "hint_ar" in r
    assert r["signals"]["engine"] == ali12.ALI12_ENGINE_VERSION
    assert 0.0 <= r["confidence"] <= 1.0


def test_jaccard():
    assert ali12.jaccard_keywords("error 404 not found", frozenset({"404", "not"})) > 0.0


def test_infer_stack_streamlit():
    assert ali12.infer_stack_family("streamlit run app.py") == "streamlit"


def test_runtime_profile_keys():
    p = ali12.runtime_profile()
    assert "os_family" in p and "python_version" in p


def test_release_tanzeel_hint_when_user_missing_zip():
    r = ali12.resolve_ali12(
        event_kind="install_fail",
        message="لماذا لا أرى البيتا في مجلد تنزيل",
        detail={},
    )
    assert r["rule_id"] == "release_tanzeel_build"
    assert "build_windows" in r["hint_ar"].lower() or "build_windows" in r["hint_ar"]


def test_store_flow_folder_cancel_resolves_to_store_install_folder():
    r = ali12.resolve_ali12(
        event_kind="install_fail",
        message="",
        detail={
            "phase": "folder_picker_cancelled",
            "install_flow": "store_consent",
            "model_id": "euqid",
            "folder": "Euqid",
        },
    )
    assert r["rule_id"] == "store_install_folder"
    assert "مجلد" in r["hint_ar"] or "محاولة" in r["hint_ar"]


def test_platform_alijaddi_install_question():
    r = ali12.resolve_ali12(
        event_kind="install_fail",
        message="كيف أثبت منصة علي جدي على ويندوز؟",
        detail={},
    )
    assert r["rule_id"] == "platform_alijaddi_install"
    assert "AliJaddi" in r["hint_ar"] or "علي" in r["hint_ar"]


def test_platform_alijaddi_product_detail():
    r = ali12.resolve_ali12(
        event_kind="install_fail",
        message="",
        detail={"product": "alijaddi_platform", "phase": "first_launch"},
    )
    assert r["rule_id"] == "platform_alijaddi_install"


def test_platform_inno_distribution_detail_wins():
    r = ali12.resolve_ali12(
        event_kind="install_fail",
        message="",
        detail={"distribution": "inno_setup", "product": "alijaddi_platform"},
    )
    assert r["rule_id"] == "platform_alijaddi_install"
    assert "Setup" in r["hint_ar"] or "مثبت" in r["hint_ar"]


def test_platform_user_asks_for_setup_exe():
    r = ali12.resolve_ali12(
        event_kind="install_fail",
        message="أين ملف Setup لتثبيت علي جدي الرسمي؟",
        detail={},
    )
    assert r["rule_id"] == "platform_alijaddi_install"


def test_platform_install_hint_omits_python_path_suffix():
    """إجابات تثبيت المنصّة لا تُلحق لاحقة PATH (ضوضاء)."""
    r = ali12.resolve_ali12(
        event_kind="install_fail",
        message="كيف أثبت منصة علي جدي على ويندوز؟",
        detail={},
    )
    assert r["rule_id"] == "platform_alijaddi_install"
    assert "PATH لـ Python" not in r["hint_ar"]


def test_post_install_ux_after_store_ok():
    r = ali12.resolve_ali12(
        event_kind="install_ok",
        message="",
        detail={
            "install_flow": "store_folder_picker",
            "apps_parent": "C:\\Users\\me\\.alijaddi\\downloads",
            "folder": "Euqid",
            "model_id": "euqid",
        },
    )
    assert r["rule_id"] == "post_install_ux"
    assert "فتح التطبيق" in r["hint_ar"] or "المنصّة" in r["hint_ar"]


def test_store_flow_consent_cancel_resolves_to_store_install_folder():
    r = ali12.resolve_ali12(
        event_kind="install_fail",
        message="",
        detail={
            "phase": "consent_cancelled",
            "install_flow": "store_consent",
            "install_contract": "store_consent_v2",
            "model_id": "tahlil",
            "folder": "tahlil",
        },
    )
    assert r["rule_id"] == "store_install_folder"
    assert "Ali12" in r["hint_ar"] or "المتجر" in r["hint_ar"] or "موافقة" in r["hint_ar"]


def test_euqid_rule_module_error():
    r = ali12.resolve_ali12(
        event_kind="install_fail",
        message="",
        detail={
            "model_id": "euqid",
            "folder": "Euqid",
            "phase": "install",
            "error": "ModuleNotFoundError: No module named 'pywebview'",
        },
    )
    assert r["rule_id"] == "euqid_contract_python_stack"


def test_recompute_merges_top_level_model_id():
    r = ali12.recompute_from_telemetry_row(
        {
            "event_kind": "install_fail",
            "model_id": "euqid",
            "detail": {"error": "No module named 'pywebview'", "phase": "install"},
        }
    )
    assert r["rule_id"] == "euqid_contract_python_stack"


def test_launch_fail_uses_launch_command_for_rules():
    """رسالة التتبع فارغة؛ يجب أن يُستدل المكدس من launch_command ولا يسقط إلى fallback."""
    r = ali12.resolve_ali12(
        event_kind="launch_fail",
        message="",
        detail={
            "phase": "smoke",
            "launch_command": "python -m streamlit run app.py",
            "title": "Smoke",
        },
    )
    assert r["rule_id"] != "fallback"
    assert r["candidates_n"] >= 1
    assert r["signals"].get("stack_family") == "streamlit"


def test_infer_kind():
    assert (
        ali12.infer_install_event_kind_from_message("رابط التنزيل غير متوفر", ok=False)
        == "install_no_url"
    )


def test_training_payload_keys():
    p = ali12.training_payload_stub(
        event_kind="install_fail",
        model_id="euqid",
        user_message_snippet="timeout",
        ali12_hint_ar="انتظر",
        resolution_label="",
    )
    assert p["assistant_id"] == "Ali12"
    assert p["task"] == "install_help"


def test_training_payload_assistant_override():
    p = ali12.training_payload_stub(
        event_kind="install_fail",
        model_id="",
        user_message_snippet="x",
        ali12_hint_ar="y",
        assistant_id="Hassan12",
    )
    assert p["assistant_id"] == "Hassan12"


def test_suggest_launch_fail_empty_cmd():
    s = ali12.suggest_after_install_failure(
        event_kind="launch_fail",
        message="",
        detail={"phase": "empty_command"},
    )
    assert "manifest" in s or "التطبيق" in s


def test_suggest_launch_fail_exit_code():
    s = ali12.suggest_after_install_failure(
        event_kind="launch_fail",
        message="",
        detail={"exit_code": 1},
    )
    assert "رمز" in s or "1" in s
