# Define log file
$logFile = "$env:USERPROFILE\winget_upgrade_log_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

# Fetch upgradeable software list
$upgradeList = winget upgrade --accept-source-agreements --output json | ConvertFrom-Json

# Display list with row numbers
Write-Host "`nAvailable upgrades:`n"
$i = 1
foreach ($app in $upgradeList) {
    Write-Host ("[{0}] {1,-40} {2,-35} {3,-15} -> {4}" -f $i, $app.Name, $app.Id, $app.Version, $app.Available)
    $i++
}

# Prompt user
$userInput = Read-Host "`nEnter 'Y' to upgrade all, or '!<row number>' to skip a specific software"

# Determine skip index if applicable
$skipIndex = -1
if ($userInput -match '^!\d+$') {
    $skipIndex = [int]$userInput.Substring(1) - 1
}

# Perform upgrades
$i = 0
foreach ($app in $upgradeList) {
    if ($userInput -eq 'Y' -or ($skipIndex -ne $i)) {
        Write-Host "`nUpgrading $($app.Name) ($($app.Id))..."
        Add-Content -Path $logFile -Value "[$(Get-Date)] Upgrading $($app.Name) ($($app.Id))"
        winget upgrade --id $app.Id --accept-source-agreements --accept-package-agreements | Tee-Object -FilePath $logFile -Append
    } else {
        Write-Host "`nSkipping $($app.Name) ($($app.Id))..."
        Add-Content -Path $logFile -Value "[$(Get-Date)] Skipped $($app.Name) ($($app.Id))"
    }
    $i++
}

Write-Host "`nUpgrade process complete. Log saved to: $logFile"
