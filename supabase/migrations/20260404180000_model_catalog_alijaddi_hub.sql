-- معرّف المركز في كتالوج النماذج (مزامنة model_user_data / الحساب الموحد)
INSERT INTO core.model_catalog (model_id, display_name_ar, description) VALUES
  (
    'alijaddi',
    'علي جدي — المركز',
    'حساب مركزي ومزامنة مع AliJaddi Cloud وAliJaddiAccount'
  )
ON CONFLICT (model_id) DO UPDATE SET
  display_name_ar = EXCLUDED.display_name_ar,
  description = EXCLUDED.description,
  updated_at = now();
