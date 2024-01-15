# Define the download URL and the destination
$pythonUrl = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
$destination = "$env:TEMP\python_installer.exe"

# Download Python installer
Invoke-RestMethod -Uri $pythonUrl -OutFile $destination

# Install Python silently
Start-Process -FilePath "$env:TEMP\python_installer.exe" -ArgumentList "/S" -Wait

python -m venv $PSScriptRoot\virt
cd $PSScriptRoot
.\virt\Scripts\Activate.ps1

pip install PyQt6

$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$Home\Desktop\PyTimer.lnk")
$Shortcut.TargetPath = "$PSScriptRoot\run.bat"
$shortcut.IconLocation = "$PSScriptRoot\icon.ico"
$Shortcut.Save()