!include LogicLib.nsh

Outfile "..\\dist\\PythonDepInstaller.exe"
Name "Python Checker"
InstallDir $EXEDIR

Section "Check and Install Python"
    Call CheckPython
SectionEnd

Function CheckPython
    ; Check for Python in Registry (official installer)
    ReadRegStr $0 HKLM "SOFTWARE\Python\PythonCore\3.11\InstallPath" ""
    ${If} $0 == ""
        ReadRegStr $0 HKCU "SOFTWARE\Python\PythonCore\3.11\InstallPath" ""
    ${EndIf}

    ; Check for Windows Store Python
    ${If} $0 == ""
        ReadRegStr $0 HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Python 3.11" "InstallLocation"
    ${EndIf}

    ; Check typical folder locations
    ${If} $0 == ""
        ${If} ${FileExists} "C:\Program Files\Python311\python.exe"
            StrCpy $0 "C:\Program Files\Python311\"
        ${ElseIf} ${FileExists} "C:\Program Files (x86)\Python311\python.exe"
            StrCpy $0 "C:\Program Files (x86)\Python311\"
        ${ElseIf} ${FileExists} "$LOCALAPPDATA\Programs\Python\Python311\python.exe"
            StrCpy $0 "$LOCALAPPDATA\Programs\Python\Python311\"
        ${ElseIf} ${FileExists} "$LOCALAPPDATA\Microsoft\WindowsApps\python.exe"
            StrCpy $0 "$LOCALAPPDATA\Microsoft\WindowsApps\"
        ${Else}
            MessageBox MB_ICONEXCLAMATION|MB_YESNO "Python is not installed. Would you like to install it now?" IDYES InstallPython IDNO End
        ${EndIf}
    ${EndIf}

    ; If found, show success
    ${If} $0 != ""
        MessageBox MB_OK "Python found at: $0"
        MessageBox MB_OK "Installing App Python dependencies..."
        MessageBox MB_OK "Installing dependencies..."
        __REQUIREMENTS__
    ${EndIf}
    Return

InstallPython:
    MessageBox MB_OK "Downloading Python installer..."
    nsExec::ExecToStack 'powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe -OutFile $EXEDIR\python_installer.exe"'
    MessageBox MB_OK "Installing Python..."
    nsExec::ExecToStack '"$EXEDIR\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1'
    MessageBox MB_OK "Python installed successfully!"

    Return

End:
FunctionEnd