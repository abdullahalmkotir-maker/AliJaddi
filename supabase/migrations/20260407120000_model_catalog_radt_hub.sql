-- معرّف مركزي لحفظ لقطة Radt في model_user_data (دون تثبيت كوحدة Streamlit)
INSERT INTO core.model_catalog (model_id, display_name_ar, description) VALUES
  ('radt', 'Radt — المركز', 'لقطة حالة منصة ربط النماذج (قائمة مثبتة، مستخدم)')
ON CONFLICT (model_id) DO UPDATE SET
  display_name_ar = EXCLUDED.display_name_ar,
  description = EXCLUDED.description,
  updated_at = now();
