AliJaddi — Android
==================

حالياً لا يُبنى APK ضمن هذا المستودع (تم إزالة مسار Flet/Android سابقاً). مجلد
«تنزيل/android» مخصص لملفات التوزيع عند توفرها.

- بعد بناء APK (Gradle / Flutter / غيره)، انسخ الملف إلى هذا المجلد باسم واضح،
  مثال: AliJaddi-Beta-0.4.1-android.apk
- أو شغّل من جذر المشروع:
    powershell -ExecutionPolicy Bypass -File scripts\export_android_to_tanzeel.ps1 -ApkPath "C:\path\to\app-release.apk"

التحديثات البرمجية لعميل أندرويد مستقبلية تُضاف كمشروع منفصل أو فرع ثم تُنسخ
الحزمة هنا ليتم رفعها مع باقي التنزيلات.
