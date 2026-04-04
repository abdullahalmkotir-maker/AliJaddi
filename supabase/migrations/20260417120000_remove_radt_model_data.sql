-- إزالة معرّف radt وبياناته بالكامل دون المساس بنماذج AliJaddi الأخرى.

DELETE FROM storage.objects
WHERE bucket_id = 'model-assets'
  AND split_part(name, '/', 2) = 'radt';

DELETE FROM core.platform_install_events WHERE model_id = 'radt';

DELETE FROM core.user_models WHERE model_name = 'radt';

UPDATE core.stars_log SET source_model = NULL WHERE source_model = 'radt';

DELETE FROM core.model_user_data WHERE model_id = 'radt';

DELETE FROM core.model_catalog WHERE model_id = 'radt';
