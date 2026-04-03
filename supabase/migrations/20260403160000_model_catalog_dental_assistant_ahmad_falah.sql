-- تحديث وصف كتالوج مساعد الأسنان — إسناد أحمد فلاح وAli12
INSERT INTO core.model_catalog (model_id, display_name_ar, description) VALUES
  (
    'dental_assistant',
    'مساعد طبيب الأسنان — أحمد فلاح',
    'إدارة عيادة أسنان مع مزامنة AliJaddi Cloud ودعم Ali12 لأخطاء التثبيت والتشغيل (Streamlit)'
  )
ON CONFLICT (model_id) DO UPDATE SET
  display_name_ar = EXCLUDED.display_name_ar,
  description = EXCLUDED.description,
  updated_at = now();
