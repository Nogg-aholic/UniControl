# Universal Controller Version Management Script
param(
    [Parameter(Mandatory=$false)]
    [string]$Version
)

function Update-Version {
    param([string]$NewVersion)
    
    Write-Host "🚀 Updating version to $NewVersion" -ForegroundColor Green
    
    # Update VERSION file
    Set-Content -Path "VERSION" -Value $NewVersion
    Write-Host "✅ Updated VERSION: $NewVersion" -ForegroundColor Green
    
    # Update manifest.json
    $manifestPath = "custom_components\universal_controller\manifest.json"
    $manifest = Get-Content $manifestPath | ConvertFrom-Json
    $manifest.version = $NewVersion
    $manifest | ConvertTo-Json -Depth 10 | Set-Content $manifestPath
    Write-Host "✅ Updated manifest.json: $NewVersion" -ForegroundColor Green
    
    # Update const.py
    $constPath = "custom_components\universal_controller\const.py"
    $constContent = Get-Content $constPath
    for ($i = 0; $i -lt $constContent.Length; $i++) {
        if ($constContent[$i] -match '^VERSION = ') {
            $constContent[$i] = "VERSION = `"$NewVersion`""
            break
        }
    }
    Set-Content -Path $constPath -Value $constContent
    Write-Host "✅ Updated const.py: $NewVersion" -ForegroundColor Green
    
    # Update __init__.py
    $initPath = "custom_components\universal_controller\__init__.py"
    $initContent = Get-Content $initPath
    for ($i = 0; $i -lt $initContent.Length; $i++) {
        if ($initContent[$i] -match '^__version__ = ') {
            $initContent[$i] = "__version__ = `"$NewVersion`""
            break
        }
    }
    Set-Content -Path $initPath -Value $initContent
    Write-Host "✅ Updated __init__.py: $NewVersion" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "✅ Version updated successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. git add ." -ForegroundColor White
    Write-Host "2. git commit -m 'Bump version to $NewVersion'" -ForegroundColor White
    Write-Host "3. git tag v$NewVersion" -ForegroundColor White
    Write-Host "4. git push origin master --tags" -ForegroundColor White
}

function Get-CurrentVersion {
    if (Test-Path "VERSION") {
        return Get-Content "VERSION" -Raw | ForEach-Object { $_.Trim() }
    }
    return "0.0.0"
}

# Main script
if (-not $Version) {
    $current = Get-CurrentVersion
    Write-Host "Current version: $current" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\version.ps1 -Version <new_version>" -ForegroundColor Yellow
    Write-Host "Example: .\version.ps1 -Version 1.1.0" -ForegroundColor Yellow
    exit
}

# Basic version validation
if ($Version -notmatch '^\d+\.\d+\.\d+') {
    Write-Host "❌ Invalid version format. Use semantic versioning (e.g., 1.0.0)" -ForegroundColor Red
    exit 1
}

Update-Version -NewVersion $Version
