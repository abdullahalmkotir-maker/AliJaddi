; AliJaddi — المعيار الرسمي لتوزيع Windows (أسلوب التطبيقات الكلاسيكية مثل Blender):
; تسجيل في النظام، مجلد Program Files، اختصار قائمة ابدأ، إزالة من إعدادات Windows.
; يتطلب مجلد dist\AliJaddi من PyInstaller مسبقاً.
; التجميع: Inno Setup 6 — ISCC.exe AliJaddi_Setup.iss

#define MyAppVersion "0.4.1"
#define MyAppName "AliJaddi"

[Setup]
AppId={{D472A435-3565-4A99-8A93-7BF64F74A1F2}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} Beta {#MyAppVersion}
UninstallDisplayName={#MyAppName} Beta {#MyAppVersion}
VersionInfoVersion={#MyAppVersion}.0
AppPublisher=AliJaddi
AppPublisherURL=https://alijaddi.app
AppSupportURL=https://alijaddi.app
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=installer
OutputBaseFilename=AliJaddi-Beta-0.4.1-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; أيقونة المثبت: استخدم أيقونة التنفيذي بعد التثبيت (لا يلزم ملف .ico منفصل)
UninstallDisplayIcon={app}\AliJaddi.exe
PrivilegesRequired=admin
MinVersion=10.0
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\AliJaddi\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\AliJaddi.exe"; IconFilename: "{app}\AliJaddi.exe"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\AliJaddi.exe"; Tasks: desktopicon; IconFilename: "{app}\AliJaddi.exe"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Run]
Filename: "{app}\AliJaddi.exe"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
