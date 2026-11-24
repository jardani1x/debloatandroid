# CleanYourPhone Restore All Script (PowerShell)
# Target Device: adb-UBS1241116012667-mmsCJ7._adb-tls-connect._tcp
$adb = "C:\Users\jun yi\AppData\Local\Microsoft\WinGet\Packages\Google.PlatformTools_Microsoft.Winget.Source_8wekyb3d8bbwe\platform-tools\adb.exe"
$deviceId = "adb-UBS1241116012667-mmsCJ7._adb-tls-connect._tcp"

Write-Host "Re-connecting to device $deviceId..."
& $adb connect $deviceId
Start-Sleep -Seconds 1

Write-Host "Restoring packages to original baseline states from original-package-states.json..."
$jsonPath = Join-Path $PSScriptRoot "original-package-states.json"
if (-not (Test-Path $jsonPath)) {
    $jsonPath = Join-Path $PSScriptRoot "..\backups\original-package-states.json"
}

if (-not (Test-Path $jsonPath)) {
    Write-Error "Cannot find original-package-states.json!"
    exit 1
}

$data = Get-Content $jsonPath -Raw | ConvertFrom-Json
$count = 0
foreach ($prop in $data.PSObject.Properties) {
    $pkg = $prop.Name
    $info = $prop.Value
    $state = $info.original_state
    
    if ($state -eq "enabled" -or $state -eq "default") {
        Write-Host "Enabling $pkg..."
        & $adb -s $deviceId shell pm enable --user 0 $pkg
        $count++
    } elseif ($state -eq "disabled") {
        Write-Host "Preserving originally disabled: $pkg"
        & $adb -s $deviceId shell pm disable-user --user 0 $pkg
    }
}

Write-Host "Restoration complete. Processed $count packages."
