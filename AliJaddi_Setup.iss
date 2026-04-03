[Setup]
AppId={{D472A435-3565-4A99-8A93-7BF64F74A1F2}
AppName=AliJaddi
AppVersion=0.2.0
AppPublisher=AliJaddi
AppPublisherURL=https://alijaddi.app
AppSupportURL=https://alijaddi.app
DefaultDirName={autopf}\AliJaddi
DefaultGroupName=AliJaddi
OutputDir=installer
OutputBaseFilename=AliJaddi_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\AliJaddi.exe

[Languages]
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\AliJaddi.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\AliJaddi"; Filename: "{app}\AliJaddi.exe"; IconFilename: "{app}\AliJaddi.exe"
Name: "{autodesktop}\AliJaddi"; Filename: "{app}\AliJaddi.exe"; Tasks: desktopicon; IconFilename: "{app}\AliJaddi.exe"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\AliJaddi.exe"; Description: "Launch AliJaddi"; Flags: nowait postinstall skipifsilent
