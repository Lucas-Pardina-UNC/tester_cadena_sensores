Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# --- Helper UI Functions ---
function Show-InfoBox($message, $title = "Python Checker") {
    [System.Windows.Forms.MessageBox]::Show($message, $title, 'OK', 'Information')
}

function Show-YesNo($message, $title = "Python Checker") {
    return [System.Windows.Forms.MessageBox]::Show($message, $title, 'YesNo', 'Question') -eq "Yes"
}

function Show-OkCancel($message, $title = "Python Checker") {
    return [System.Windows.Forms.MessageBox]::Show($message, $title, [System.Windows.Forms.MessageBoxButtons]::OKCancel, [System.Windows.Forms.MessageBoxIcon]::Information) -eq [System.Windows.Forms.DialogResult]::OK
}

function Show-Choice($message, $title = "Python Checker") {
    return [System.Windows.Forms.MessageBox]::Show($message, $title, [System.Windows.Forms.MessageBoxButtons]::YesNoCancel, 'Question')
}

# --- Progress Bar Function ---
function Show-Progress($title, $labelText) {
    $form = New-Object System.Windows.Forms.Form
    $form.Text = $title
    $form.Size = New-Object System.Drawing.Size(400,120)
    $form.StartPosition = "CenterScreen"
    $form.Topmost = $true

    $label = New-Object System.Windows.Forms.Label
    $label.AutoSize = $true
    $label.Location = New-Object System.Drawing.Point(20,20)
    $label.Text = $labelText
    $form.Controls.Add($label)

    $progressBar = New-Object System.Windows.Forms.ProgressBar
    $progressBar.Location = New-Object System.Drawing.Point(20,50)
    $progressBar.Size = New-Object System.Drawing.Size(340,20)
    $progressBar.Style = 'Marquee'
    $form.Controls.Add($progressBar)

    $form.Show()
    $form.Refresh()
    return $form
}

# --- Python Detection ---
function Is-BrokenShortcut($path) {
    try {
        $target = (New-Object -ComObject WScript.Shell).CreateShortcut($path).TargetPath
        return -not (Test-Path $target)
    } catch {
        return $true
    }
}

function Try-PythonHello($pythonExe) {
    try {
        $result = & "$pythonExe" -c "print('Hello from Python')" 2>&1
        return $result -like "*Hello from Python*"
    } catch {
        return $false
    }
}

function Detect-Python {
    $username = $env:USERNAME
    $versions = "313", "312", "311", "310", "39", "38", "37"
    $basePaths = @(
        "C:\Program Files\Python{0}\python.exe",
        "C:\Program Files (x86)\Python{0}\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python{0}\python.exe"
        #"$env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe",
        #"C:\Users\$username\AppData\Roaming\Python\Python{0}\python.exe"
    )

    $working = @()
    $broken = @()
    $failed = @()

    foreach ($v in $versions) {
        foreach ($p in $basePaths) {
            $fullPath = $p -f $v
            if (Test-Path $fullPath) {
                if ($fullPath -like "*.lnk" -and (Is-BrokenShortcut $fullPath)) {
                    $broken += $fullPath
                    continue
                }
                if (Try-PythonHello $fullPath) {
                    $working += $fullPath
                } else {
                    $failed += $fullPath
                }
            }
        }
    }

    return @{
        Working = $working
        Broken = $broken
        Failed = $failed
    }
}

# --- PATH Check/Update ---
function Ensure-PathEntries($pathsToCheck) {
    $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $systemPath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPathList = $userPath.Split(";") | Where-Object { $_ -ne "" }
    $systemPathList = $systemPath.Split(";") | Where-Object { $_ -ne "" }

    $missingUser = $pathsToCheck | Where-Object { $_ -and -not ($userPathList -contains $_) }
    $missingSystem = $pathsToCheck | Where-Object { $_ -and -not ($systemPathList -contains $_) }

    if ($missingUser.Count -eq 0 -and $missingSystem.Count -eq 0) {
        Show-InfoBox "Python and Scripts folders are already in both User and System PATH." "PATH OK"
        return $true
    }

    $msg = ""
    if ($missingUser.Count -gt 0) {
        $msg += "Missing from USER PATH:`n" + ($missingUser -join "`n") + "`n`n"
    }
    if ($missingSystem.Count -gt 0) {
        $msg += "Missing from SYSTEM PATH:`n" + ($missingSystem -join "`n") + "`n`n"
    }
    $msg += "Do you want to add the missing paths to both USER and SYSTEM PATH? (Yes to continue, No to finish)"

    if (Show-YesNo $msg "Add Python to PATH?") {
        # Add to User PATH
        $newUserPath = $userPath
        foreach ($entry in $missingUser) {
            $newUserPath += ";$entry"
        }
        [System.Environment]::SetEnvironmentVariable("Path", $newUserPath, "User")
        # Add to System PATH (requires admin)
        try {
            $newSystemPath = $systemPath
            foreach ($entry in $missingSystem) {
                $newSystemPath += ";$entry"
            }
            Start-Process powershell -Verb RunAs -ArgumentList "-Command `"Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment' -Name Path -Value '$newSystemPath'`""
            Show-InfoBox "Paths added to USER and SYSTEM PATH. You may need to restart your terminal or session." "✅ PATH Updated"
        } catch {
            Show-InfoBox "Failed to update SYSTEM PATH. Try running as administrator."
        }
        return $true
    } else {
        Show-InfoBox "No changes were made to PATH."
        return $false
    }
}

# --- Python Installer ---
function Install-Python {
    $temp = "$env:TEMP\python-installer.exe"
    $url = "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe"

    # Create a single progress form
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Python Installation"
    $form.Size = New-Object System.Drawing.Size(400,140)
    $form.StartPosition = "CenterScreen"
    $form.Topmost = $true

    $label = New-Object System.Windows.Forms.Label
    $label.AutoSize = $true
    $label.Location = New-Object System.Drawing.Point(20,20)
    $label.Text = "Downloading Python..."
    $form.Controls.Add($label)

    $progressBar = New-Object System.Windows.Forms.ProgressBar
    $progressBar.Location = New-Object System.Drawing.Point(20,50)
    $progressBar.Size = New-Object System.Drawing.Size(340,20)
    $progressBar.Minimum = 0
    $progressBar.Maximum = 100
    $progressBar.Value = 0
    $form.Controls.Add($progressBar)

    $form.Show()
    $form.Refresh()

    # Download Python (first half)
    try {
        $label.Text = "Downloading Python..."
        $form.Refresh()
        Invoke-WebRequest -Uri $url -OutFile $temp
        $progressBar.Value = 50
        $form.Refresh()
    } catch {
        $form.Close()
        Show-InfoBox "Failed to download Python installer." "Error"
        return $false
    }

    # Install Python (second half)
    try {
        $label.Text = "Installing Python..."
        $form.Refresh()
        Start-Process -Wait -FilePath $temp -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0"
        $progressBar.Value = 100
        $form.Refresh()
    } catch {
        $form.Close()
        Show-InfoBox "Failed to run Python installer." "Error"
        return $false
    }

    Start-Sleep -Milliseconds 500
    $form.Close()

    Remove-Item $temp -ErrorAction SilentlyContinue

    Show-InfoBox "Python was installed successfully." "Python Installed"
    return $true
}

# --- Main Logic ---

# 1. Welcome
$welcomeMsg = "Welcome! This program will now check whether the minimum required version of Python (3.8.7) is installed on your system.`n`nClick Accept to continue."
if (-not (Show-OkCancel $welcomeMsg "Python Checker")) { exit }

$result = Detect-Python

if ($result.Working.Count -gt 0) {
    $msg = "Python found and working in:`n" + ($result.Working -join "`n")
    Show-InfoBox $msg "Python Checker"

    # Tomar la primera instalación funcional encontrada
    $pythonPath = $result.Working[0]
    $pythonFolder = Split-Path $pythonPath -Parent
    $scriptsFolder = Join-Path $pythonFolder "Scripts"

    $msg2 = "We will now determine whether the Python and Scripts folders are in your PATH environment variable.`n`nClick Accept to continue."
    Show-InfoBox $msg2 "Python Checker"

    # Check PATH
    $pathsToCheck = @($pythonFolder, $scriptsFolder)
    $pathsOk = Ensure-PathEntries $pathsToCheck
    if ($pathsOk) {
        Show-InfoBox "All done! You can now use Python from any terminal." "Finished"
    }
    exit
}
elseif ($result.Failed.Count -gt 0 -or $result.Broken.Count -gt 0) {
    $msg = "Python found but NOT working in:`n" + ($result.Failed -join "`n") + "`n`nBroken links:`n" + ($result.Broken -join "`n")
    if (Show-YesNo "$msg`n`nWould you like to install Python?") {
        if(Install-Python)
        {
            # Tomar la primera instalación funcional encontrada
            $pythonPath = $result.Working[0]
            $pythonFolder = Split-Path $pythonPath -Parent
            $scriptsFolder = Join-Path $pythonFolder "Scripts"

            $msg2 = "We will now determine whether the Python and Scripts folders are in your PATH environment variable.`n`nClick Accept to continue."
            Show-InfoBox $msg2 "Python Checker"

            # Check PATH
            $pathsToCheck = @($pythonFolder, $scriptsFolder)
            $pathsOk = Ensure-PathEntries $pathsToCheck
            if ($pathsOk) {
                Show-InfoBox "All done! You can now use Python from any terminal." "Finished"
            }
            exit
        } else {
            Show-InfoBox "Python installation failed"
        }
    } else {
        Show-InfoBox "Python installation cancelled."
    }
} else {
    if (Show-YesNo "Python not found on this system. Do you want to install it?") {
        if(Install-Python)
        {
            # Tomar la primera instalación funcional encontrada
            $pythonPath = $result.Working[0]
            $pythonFolder = Split-Path $pythonPath -Parent
            $scriptsFolder = Join-Path $pythonFolder "Scripts"

            $msg2 = "We will now determine whether the Python and Scripts folders are in your PATH environment variable.`n`nClick Accept to continue."
            Show-InfoBox $msg2 "Python Checker"

            # Check PATH
            $pathsToCheck = @($pythonFolder, $scriptsFolder)
            $pathsOk = Ensure-PathEntries $pathsToCheck
            if ($pathsOk) {
                Show-InfoBox "All done! You can now use Python from any terminal." "Finished"
            }
            exit
        } else {
            Show-InfoBox "Python installation failed"
        }
    } else {
        Show-InfoBox "Python installation cancelled."
    }
}