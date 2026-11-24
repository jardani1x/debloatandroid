param (
    [Parameter(Mandatory=$true)]
    [string]$PackageName
)
$adb = "C:\Users\jun yi\AppData\Local\Microsoft\WinGet\Packages\Google.PlatformTools_Microsoft.Winget.Source_8wekyb3d8bbwe\platform-tools\adb.exe"
$deviceId = "adb-UBS1241116012667-mmsCJ7._adb-tls-connect._tcp"

Write-Host "Restoring package $PackageName on $deviceId..."
& $adb connect $deviceId
& $adb -s $deviceId shell pm enable --user 0 $PackageName
Write-Host "Verification:"
& $adb -s $deviceId shell pm list packages -d | Select-String $PackageName
