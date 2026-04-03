# -*- coding: utf-8 -*-
"""
معيار **store_consent_v2** — التثبيت الفعلي لتطبيقات المتجر يتم عبر **Ali12**
(``scripts/ali12_store_install.py``) خارج واجهة المنصّة؛ الحاضنة الافتراضية «تطبيقات علي جدي».

دوال ``run_store_install_consent`` تبقى للتوافق مع شيفرة قديمة أو مسارات خاصة؛
واجهة متجر Qt الحالية لا تستدعي التثبيت المباشر.

**منصّة Windows:** المثبّت الرسمي Inno — ``AliJaddi_Setup.iss`` و``training/Ali12_seed.jsonl``.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget

from services.addon_manager import load_installed
from services.install_telemetry import emit_install_event
from services.paths import apps_root

# يُكتب في التتبع وبيانات التدريب — v2: زر «تثبيت تلقائي» على سطح المكتب بدون منتقي مجلد إلزامي
STORE_INSTALL_CONTRACT_VERSION = "store_consent_v2"
STORE_INSTALL_FLOW_KIND = "store_consent"


@dataclass(frozen=True)
class StoreInstallPrep:
    """نتيجة خطوات الموافقة + (اختياري) المجلد قبل بدء التحميل."""

    apps_parent: Optional[Path]
    """مسار المجلد الأب لـ ``install_model`` — حاضنة «تطبيقات علي جدي» أو مسار مخصّص."""

    cancel_phase: Optional[str]
    """``consent`` | ``folder`` إن أُلغي؛ وإلا ``None``."""


def run_store_install_consent(
    parent: QWidget,
    *,
    model_id: str,
    manifest_folder: str,
    version: str,
    display_name: str,
) -> StoreInstallPrep:
    """
    1) حوار موافقة يشرح المعيار الجديد (سطح المكتب التلقائي).
    2) إما ``apps_root()`` مباشرة، أو منتقي مجلد الأب لمن يريد مساراً مختلفاً.
    """
    consent = QMessageBox(parent)
    consent.setIcon(QMessageBox.Icon.Information)
    consent.setWindowTitle("تثبيت من المتجر")
    consent.setText(
        "بعد موافقتك، تثبّت المنصّة التطبيق <b>تلقائياً</b> داخل مجلد "
        "<b>«تطبيقات علي جدي»</b> على سطح المكتب (أو OneDrive Desktop إن وُجد) — "
        "ويُنشأ <b>اختصار على سطح المكتب</b> باسم التطبيق عند النجاح. "
        f"معيار المتجر: <b>{STORE_INSTALL_CONTRACT_VERSION}</b>."
    )
    consent.setInformativeText(
        "يمكنك بدلاً من ذلك اختيار <b>مجلد أب</b> مختلف (مثل قرص آخر). "
        "مساعد <b>Ali12</b> يفسّر أخطاء التنزيل والفك من سجلات المنصّة."
    )
    btn_auto = consent.addButton(
        "تثبيت تلقائياً على سطح المكتب (موصى به)", QMessageBox.ButtonRole.AcceptRole
    )
    btn_custom = consent.addButton(
        "اختيار مجلد آخر…", QMessageBox.ButtonRole.ActionRole
    )
    btn_cancel = consent.addButton("إلغاء", QMessageBox.ButtonRole.RejectRole)
    consent.setDefaultButton(btn_auto)
    consent.exec()

    clicked = consent.clickedButton()
    if clicked is None or clicked == btn_cancel:
        emit_install_event(
            "install_fail",
            model_id=model_id,
            success=False,
            detail={
                "phase": "consent_cancelled",
                "folder": manifest_folder,
                "version": version,
                "install_flow": STORE_INSTALL_FLOW_KIND,
                "install_contract": STORE_INSTALL_CONTRACT_VERSION,
                "display_name": display_name[:120],
            },
        )
        return StoreInstallPrep(None, "consent")

    if clicked == btn_auto:
        return StoreInstallPrep(apps_root().resolve(), None)

    # مجلد مخصّص
    row = load_installed().get(model_id) or {}
    prev_parent = (row.get("apps_parent") or "").strip()
    if prev_parent and Path(prev_parent).is_dir():
        default_parent = str(Path(prev_parent).resolve())
    else:
        default_parent = str(apps_root())

    chosen = QFileDialog.getExistingDirectory(
        parent,
        f"اختر مجلد التثبيت — {display_name} (يُضاف مجلد التطبيق تلقائياً)",
        default_parent,
        QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks,
    )
    if not chosen:
        emit_install_event(
            "install_fail",
            model_id=model_id,
            success=False,
            detail={
                "phase": "folder_picker_cancelled",
                "folder": manifest_folder,
                "version": version,
                "install_flow": STORE_INSTALL_FLOW_KIND,
                "install_contract": STORE_INSTALL_CONTRACT_VERSION,
                "display_name": display_name[:120],
            },
        )
        return StoreInstallPrep(None, "folder")

    return StoreInstallPrep(Path(chosen).resolve(), None)
