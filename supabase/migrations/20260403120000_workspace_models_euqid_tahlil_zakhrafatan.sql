-- نماذج مساحة العمل: Euqid, tahlil, Zakhrafatan, SniperPerspective
INSERT INTO core.model_catalog (model_id, display_name_ar, description) VALUES
  ('euqid', 'عقد (Euqid)', 'منصة إدارة وتحليل العقود — دورة حياة العقد والقانون العراقي'),
  ('tahlil', 'تحليل (tahlil)', 'تحليل بيانات وتعلم آلي وتصور — تطبيق Streamlit'),
  ('zakhrafatan', 'زخرفة', 'Zakhrafatan — توليد وتصنيف ومعالجة الزخارف والمكتبة المحلية'),
  ('sniper_perspective', 'منظور القناص', 'SniperPerspective — تتبع YOLO وواجهة استهداف (مشروع سطح المكتب)')
ON CONFLICT (model_id) DO UPDATE SET
  display_name_ar = EXCLUDED.display_name_ar,
  description = EXCLUDED.description,
  updated_at = now();
