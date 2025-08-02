# Universal Controller Add-on Build Script for Windows PowerShell
# This script builds and tests the Home Assistant add-on

param(
    [switch]$Test,
    [switch]$Dev,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
Universal Controller Add-on Build Script

Usage: .\scripts\build-addon.ps1 [options]

Options:
  -Test    Run tests after building
  -Dev     Show development information
  -Help    Show this help message

Examples:
  .\scripts\build-addon.ps1                    # Basic build
  .\scripts\build-addon.ps1 -Test            # Build and test
  .\scripts\build-addon.ps1 -Dev             # Build with dev info
"@
    exit 0
}

# Colors for output (Windows PowerShell compatible)
function Write-Status { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

Write-Host "🚀 Building Universal Controller Home Assistant Add-on" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "universal_controller\config.yaml")) {
    Write-Error "config.yaml not found. Are you in the project root?"
    exit 1
}

# Step 1: Validate configuration
Write-Status "Validating add-on configuration..."
if (Get-Command node -ErrorAction SilentlyContinue) {
    if (Test-Path "package.json") {
        try {
            npm install --silent 2>$null
            node scripts\validate-config.js
        }
        catch {
            Write-Warning "Failed to run validation, continuing..."
        }
    }
    else {
        Write-Warning "Node.js found but package.json missing, skipping validation"
    }
}
else {
    Write-Warning "Node.js not found, skipping configuration validation"
}

# Step 2: Check Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is required but not installed"
    exit 1
}

$dockerVersion = docker --version
Write-Status "Docker found: $dockerVersion"

# Step 3: Build the add-on
Write-Status "Building Universal Controller add-on Docker image..."

Set-Location "universal_controller"

# Read version from config.yaml
$versionLine = Get-Content "config.yaml" | Where-Object { $_ -match "^version:" }
$version = ($versionLine -split ": ")[1].Trim('"')
$imageName = "local/universal-controller"

Write-Status "Building version: $version"

# Get build info
$buildDate = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$buildRef = try { git rev-parse --short HEAD } catch { "unknown" }

# Build the Docker image
Write-Status "Running Docker build..."
$buildArgs = @(
    "--build-arg", "BUILD_DATE=$buildDate",
    "--build-arg", "BUILD_REF=$buildRef", 
    "--build-arg", "BUILD_VERSION=$version",
    "-t", "$imageName`:$version",
    "-t", "$imageName`:latest",
    "."
)

$buildProcess = Start-Process -FilePath "docker" -ArgumentList ("build " + ($buildArgs -join " ")) -Wait -PassThru -NoNewWindow

if ($buildProcess.ExitCode -eq 0) {
    Write-Success "Docker image built successfully"
    
    # Show image details
    Write-Status "Image details:"
    docker images $imageName --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
}
else {
    Write-Error "Docker build failed"
    Set-Location ".."
    exit 1
}

Set-Location ".."

# Step 4: Test the built image (optional)
if ($Test) {
    Write-Status "Testing the built add-on..."
    
    # Run a quick test container
    Write-Status "Starting test container..."
    
    try {
        $containerId = docker run -d -p 8099:8099 -e SUPERVISOR_TOKEN="test-token" "$imageName`:latest"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Test container started: $containerId"
            
            # Wait for container to be ready
            Start-Sleep -Seconds 5
            
            # Test if the service is responding
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:8099/" -TimeoutSec 10 -ErrorAction Stop
                Write-Success "Add-on is responding on port 8099"
            }
            catch {
                Write-Warning "Add-on may not be ready yet"
            }
            
            # Show container logs
            Write-Status "Container logs:"
            $logs = docker logs $containerId
            $logs | Select-Object -Last 20 | ForEach-Object { Write-Host $_ }
            
            # Cleanup
            Write-Status "Stopping test container..."
            docker stop $containerId | Out-Null
            docker rm $containerId | Out-Null
        }
        else {
            Write-Error "Failed to start test container"
            exit 1
        }
    }
    catch {
        Write-Error "Test failed: $($_.Exception.Message)"
        exit 1
    }
}

# Step 5: Installation instructions
Write-Success "Build completed successfully!"
Write-Host ""
Write-Host "📦 Installation Instructions:" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Copy the 'universal_controller' folder to your Home Assistant add-ons directory:"
Write-Host "   /addons/universal_controller/"
Write-Host ""
Write-Host "2. Or for development with the Supervisor:"
Write-Host "   docker run -d \"
Write-Host "     --name universal-controller \"
Write-Host "     -p 8099:8099 \"
Write-Host "     -e SUPERVISOR_TOKEN=`$SUPERVISOR_TOKEN \"
Write-Host "     -e HOMEASSISTANT_URL=http://supervisor/core \"
Write-Host "     $imageName`:$version"
Write-Host ""
Write-Host "3. Access the web interface at: http://your-ha-ip:8099"
Write-Host ""
Write-Host "4. The add-on will appear in your Home Assistant sidebar as 'Universal Controller'"
Write-Host ""

# Step 6: Development notes
if ($Dev) {
    Write-Host "🔧 Development Notes:" -ForegroundColor Cyan
    Write-Host "===================="
    Write-Host ""
    Write-Host "• Source code is in: universal_controller\rootfs\app\"
    Write-Host "• Web interface: universal_controller\rootfs\app\web\"
    Write-Host "• Configuration: universal_controller\config.yaml"
    Write-Host "• Build artifacts are tagged as: $imageName`:$version"
    Write-Host ""
    Write-Host "To rebuild quickly:"
    Write-Host "  docker build -t $imageName`:dev universal_controller\"
    Write-Host ""
    Write-Host "To run in development mode:"
    Write-Host "  docker run -it --rm -p 8099:8099 $imageName`:dev"
    Write-Host ""
}

Write-Success "Universal Controller add-on is ready for installation!"
