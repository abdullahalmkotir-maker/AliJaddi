-- إضافة مساعد طبيب الأسنان إلى كتالوج النماذج
INSERT INTO core.model_catalog (model_id, display_name_ar, description) VALUES
  ('dental_assistant', 'مساعد طبيب الأسنان', 'نظام إدارة عيادة أسنان — ملفات المرضى، الجلسات، الصور الشعاعية، التقارير')
ON CONFLICT (model_id) DO UPDATE SET
  display_name_ar = EXCLUDED.display_name_ar,
  description = EXCLUDED.description,
  updated_at = now();
