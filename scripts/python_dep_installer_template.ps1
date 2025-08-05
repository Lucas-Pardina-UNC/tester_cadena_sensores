Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

__PACKAGES__

# --- Welcome Window ---
$depList = ($packages -join "`n")
$welcomeMsg = "The following Python dependencies will be installed:`n`n$depList`n`nDo you want to continue?"
$welcomeResult = [System.Windows.Forms.MessageBox]::Show($welcomeMsg, "Python Dependency Installer", [System.Windows.Forms.MessageBoxButtons]::OKCancel, [System.Windows.Forms.MessageBoxIcon]::Information)
if ($welcomeResult -ne [System.Windows.Forms.DialogResult]::OK) {
    exit
}

# --- Progress Bar Window ---
$form = New-Object System.Windows.Forms.Form
$form.Text = "Installing Python Dependencies"
$form.Size = New-Object System.Drawing.Size(500,150)
$form.StartPosition = "CenterScreen"

$label = New-Object System.Windows.Forms.Label
$label.AutoSize = $true
$label.Location = New-Object System.Drawing.Point(20,20)
$label.Text = "Preparing installation..."
$form.Controls.Add($label)

$progressBar = New-Object System.Windows.Forms.ProgressBar
$progressBar.Location = New-Object System.Drawing.Point(20,60)
$progressBar.Size = New-Object System.Drawing.Size(440,25)
$progressBar.Minimum = 0
$progressBar.Maximum = $packages.Count
$form.Controls.Add($progressBar)

$form.Topmost = $true
$form.Show()
$form.Refresh()

# --- Results Dictionaries ---
$alreadyInstalled = @{}
$successfullyInstalled = @{}
$failedToInstall = @{}

# --- Detect Python ---
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    [System.Windows.Forms.MessageBox]::Show("Python is not available in PATH. Run the checker script first.", "Python Not Found")
    $form.Close()
    exit
}
$pythonExe = $python.Source
$pipExe = "$($pythonExe -replace 'python.exe$', 'Scripts\pip.exe')"

if (-not (Test-Path $pipExe)) {
    & "$pythonExe" -m ensurepip
}

# --- Install Loop with Progress ---
for ($i=0; $i -lt $packages.Count; $i++) {
    $pkg = $packages[$i]
    #$pkgName = $pkg.Split(">=")[0]
    $pkgName = $pkg -replace '\[.*\]', '' -replace '>=.*', ''
    $label.Text = "Installing: $pkg"
    $progressBar.Value = $i
    $form.Refresh()
    Start-Sleep -Milliseconds 300

    try {
        $info = & "$pythonExe" -c "import $pkgName; print($pkgName.__file__)" 2>&1
        if ($info -match "ModuleNotFoundError" -or $info -match "No module named") {
            # Try to install
            #$result = & "$pipExe" install $pkg 2>&1
            $result = & "$pipExe" install @("$pkg") 2>&1
            if ($LASTEXITCODE -eq 0) {
                # Verify import
                $check = & "$pythonExe" -c "import $pkgName; print($pkgName.__file__)" 2>&1
                if ($check -match "ModuleNotFoundError") {
                    $failedToInstall[$pkg] = "Installed but still not importable"
                } else {
                    $successfullyInstalled[$pkg] = $check
                }
            } else {
                $failedToInstall[$pkg] = $result
            }
        } else {
            $alreadyInstalled[$pkg] = $info
        }
    } catch {
        $failedToInstall[$pkg] = $_.Exception.Message
    }
}
$progressBar.Value = $packages.Count
$label.Text = "Installation finished."
$form.Refresh()
Start-Sleep -Milliseconds 500
$form.Close()

# --- Summary Window ---
$msg = ""

if ($alreadyInstalled.Count -gt 0) {
    $msg += "Already Installed:`n"
    foreach ($k in $alreadyInstalled.Keys) {
        $msg += "  $k -> $($alreadyInstalled[$k])`n"
    }
    $msg += "`n"
}

if ($successfullyInstalled.Count -gt 0) {
    $msg += "Installed Successfully:`n"
    foreach ($k in $successfullyInstalled.Keys) {
        $msg += "  $k -> $($successfullyInstalled[$k])`n"
    }
    $msg += "`n"
}

if ($failedToInstall.Count -gt 0) {
    $msg += "Failed to Install:`n"
    foreach ($k in $failedToInstall.Keys) {
        $msg += "  $k -> $($failedToInstall[$k])`n"
    }
}

if ($msg -eq "") {
    $msg = "No actions were performed."
}

[System.Windows.Forms.MessageBox]::Show($msg, "Python Dependency Installation Summary", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)