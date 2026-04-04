-- كتالوج مساعد الأسنان — إسناد العرض إلى أحمد الياسري (المجلد الفني AhmadFalahDentalAssistant دون تغيير في التطبيق)
INSERT INTO core.model_catalog (model_id, display_name_ar, description) VALUES
  (
    'dental_assistant',
    'مساعد طبيب الأسنان — أحمد الياسري',
    'إدارة عيادة أسنان مع مزامنة AliJaddi Cloud ودعم Ali12 لأخطاء التثبيت والتشغيل (Streamlit) — مساعد أحمد الياسري'
  )
ON CONFLICT (model_id) DO UPDATE SET
  display_name_ar = EXCLUDED.display_name_ar,
  description = EXCLUDED.description,
  updated_at = now();
