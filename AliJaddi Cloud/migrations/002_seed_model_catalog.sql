-- كتالوج النماذج على Supabase — موحّد مع auth_model/model_ids.py في Account و Store (بيانات المستخدم تبقى محلية هناك).
-- نفّذ بعد 001_core_tables.sql

insert into public.model_catalog (model_id, display_name_ar, description) values
  ('legal', 'قانون', 'استعلامات قانونية'),
  ('maps', 'خرائط', 'خرائط'),
  ('adich', 'أدّيش', 'AliJaddi Cloud'),
  ('sniper', 'قناص', 'لعبة تفاعلية'),
  ('qanun_example', 'مثال قانون', 'qanun'),
  ('euqid', 'عقد', 'Euqid'),
  ('tahlil', 'تحليل', 'تحليل بيانات'),
  ('zakhrafatan', 'زخرفة', 'Zakhrafatan'),
  ('sniper_perspective', 'منظور القناص', 'YOLO'),
  ('mudir', 'مدير التواصل', 'social_post_queue'),
  ('dental_assistant', 'مساعد طبيب الأسنان', 'عيادة'),
  ('alijaddi', 'علي جدّي — المركز', 'الكتالوج والمنصّة')
on conflict (model_id) do update set
  display_name_ar = excluded.display_name_ar,
  description = excluded.description;
