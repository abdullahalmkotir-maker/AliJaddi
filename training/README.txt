نُقلت بذور التدريب إلى المجلد 12/seeds/ (Ali12_seed.jsonl، Hassan12_seed.jsonl، Hussein12_seed.jsonl).
راجع 12/manifest.json و services/squad12_paths.py.

— تصدير دمج البذور + (اختياري) سجل التليمتري المحلي ~/.alijaddi/telemetry_install_events.jsonl:
  python scripts/export_ali12_training_jsonl.py -o training/squad12_bundle.jsonl --with-all-seeds
  python scripts/export_ali12_training_jsonl.py -o training/squad12_bundle.jsonl --seeds-only --with-all-seeds

— تثبيت تطبيق متجر من CLI (معيار store_consent_v2):
  python scripts/ali12_store_install.py list
  python scripts/ali12_store_install.py install <model_id>

— بناء نسخة ويندوز قابلة للتثبيت (ZIP + Setup عند توفر Inno):
  powershell -ExecutionPolicy Bypass -File scripts/build_windows_release.ps1
  المخرجات: تنزيل\windows\AliJaddi-Beta-0.5.1-Setup.exe و AliJaddi-Beta-0.5.1-Windows.zip
