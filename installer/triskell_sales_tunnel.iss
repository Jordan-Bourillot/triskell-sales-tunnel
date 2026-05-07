; ============================================================
;  Triskell Sales Tunnel — installeur Windows (Inno Setup)
;  Compilation : double-cliquer sur build_installer.bat
;  Sortie : installer_output\TriskellSalesTunnel_setup_X.Y.Z.exe
; ============================================================

#define MyAppName "Triskell Sales Tunnel"
#ifndef MyAppVersion
  #define MyAppVersion "1.1.0"
#endif
#define MyAppPublisher "Triskell Studio"
#define MyAppURL "https://prospect.triskell-studio.fr"
#define MyAppExeName "Triskell Sales Tunnel.exe"

[Setup]
AppId={{D4A8E7C2-1B5F-4E3A-9C7D-6F2A8B9E1C4D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\Triskell Sales Tunnel
DefaultGroupName=Triskell Sales Tunnel
DisableProgramGroupPage=yes
OutputDir=..\installer_output
OutputBaseFilename=TriskellSalesTunnel_setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#MyAppName}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} - Génère le bon message au bon moment
VersionInfoProductName={#MyAppName}
VersionInfoVersion={#MyAppVersion}

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\Triskell Sales Tunnel\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\Triskell Sales Tunnel\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Désinstaller {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Lancer {#MyAppName} maintenant"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
