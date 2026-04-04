# alijaddi_flutter

عميل **Flutter (Dart)** لمنصّة علي جدّي — واجهة تجريبية تتصل بالبوابة REST (`api_gateway_stub`).

## المتطلبات

- [Flutter SDK](https://docs.flutter.dev/get-started/install/windows) (مستقر على القناة stable).

## أول مرة — توليد android / ios / web

من جذر المستودع:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup_flutter_app.ps1
```

أو يدوياً داخل `flutter_alijaddi`:

```text
flutter create . --project-name alijaddi_flutter --org app.alijaddi --platforms=android,ios,web
flutter pub get
```

## تشغيل

1. شغّل البوابة (من جذر المستودع):  
   `uvicorn services.api_gateway_stub:create_app --factory --host 0.0.0.0 --port 8012`
2. من مجلد `flutter_alijaddi`:  
   `flutter run`

على **محاكي أندرويد** استخدم في التطبيق العنوان `http://10.0.2.2:8012`.

## اختبارات

```text
flutter test
```
