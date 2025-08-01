# Create GitHub release for Universal Controller
param(
    [string]$Version = "1.1.0"
)

$Tag = "v$Version"

Write-Host "🚀 Creating GitHub release for Universal Controller v$Version" -ForegroundColor Green

# Check if git tag exists
$existingTag = git tag -l | Where-Object { $_ -eq $Tag }
if ($existingTag) {
    Write-Host "✅ Tag $Tag already exists" -ForegroundColor Green
} else {
    Write-Host "📝 Creating tag $Tag" -ForegroundColor Yellow
    git tag -a $Tag -m "Release Universal Controller $Version"
    git push origin $Tag
}

Write-Host ""
Write-Host "📦 Next steps:" -ForegroundColor Yellow
Write-Host "1. Go to: https://github.com/Nogg-aholic/UniControl/releases" -ForegroundColor White
Write-Host "2. Click 'Create a new release'" -ForegroundColor White
Write-Host "3. Choose tag: $Tag" -ForegroundColor White
Write-Host "4. Title: Universal Controller $Version" -ForegroundColor White
Write-Host "5. Description: See CHANGELOG.md for details" -ForegroundColor White
Write-Host "6. Upload the zip file or let GitHub auto-generate" -ForegroundColor White
Write-Host ""
Write-Host "Or use GitHub CLI:" -ForegroundColor Cyan
Write-Host "gh release create $Tag --title 'Universal Controller $Version' --notes-file CHANGELOG.md" -ForegroundColor White

# Create a zip file for manual upload
Write-Host ""
Write-Host "📁 Creating zip file for manual upload..." -ForegroundColor Yellow

if (Test-Path "universal_controller-$Version.zip") {
    Remove-Item "universal_controller-$Version.zip"
}

# Create zip from custom_components directory
Compress-Archive -Path "custom_components\*" -DestinationPath "universal_controller-$Version.zip"
Write-Host "✅ Created universal_controller-$Version.zip" -ForegroundColor Green
