#!/bin/bash

# Universal Controller Add-on Build Script
# This script builds and tests the Home Assistant add-on

set -e

echo "🚀 Building Universal Controller Home Assistant Add-on"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "universal_controller/config.yaml" ]; then
    print_error "config.yaml not found. Are you in the project root?"
    exit 1
fi

# Step 1: Validate configuration
print_status "Validating add-on configuration..."
if command -v node >/dev/null 2>&1; then
    if [ -f "package.json" ]; then
        npm install --silent 2>/dev/null || true
        node scripts/validate-config.js
    else
        print_warning "Node.js found but package.json missing, skipping validation"
    fi
else
    print_warning "Node.js not found, skipping configuration validation"
fi

# Step 2: Check Docker
if ! command -v docker >/dev/null 2>&1; then
    print_error "Docker is required but not installed"
    exit 1
fi

print_status "Docker found: $(docker --version)"

# Step 3: Build the add-on
print_status "Building Universal Controller add-on Docker image..."

cd universal_controller

# Read version from config.yaml
VERSION=$(grep "^version:" config.yaml | cut -d' ' -f2 | tr -d '"')
IMAGE_NAME="local/universal-controller"

print_status "Building version: $VERSION"

# Build the Docker image
docker build \
    --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
    --build-arg BUILD_REF="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
    --build-arg BUILD_VERSION="$VERSION" \
    -t "$IMAGE_NAME:$VERSION" \
    -t "$IMAGE_NAME:latest" \
    .

if [ $? -eq 0 ]; then
    print_success "Docker image built successfully"
    
    # Show image details
    print_status "Image details:"
    docker images "$IMAGE_NAME" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
else
    print_error "Docker build failed"
    exit 1
fi

cd ..

# Step 4: Test the built image (optional)
if [ "$1" = "--test" ]; then
    print_status "Testing the built add-on..."
    
    # Run a quick test container
    print_status "Starting test container..."
    
    CONTAINER_ID=$(docker run -d \
        -p 8099:8099 \
        -e SUPERVISOR_TOKEN="test-token" \
        "$IMAGE_NAME:latest")
    
    if [ $? -eq 0 ]; then
        print_success "Test container started: $CONTAINER_ID"
        
        # Wait for container to be ready
        sleep 5
        
        # Test if the service is responding
        if curl -f http://localhost:8099/ >/dev/null 2>&1; then
            print_success "Add-on is responding on port 8099"
        else
            print_warning "Add-on may not be ready yet"
        fi
        
        # Show container logs
        print_status "Container logs:"
        docker logs "$CONTAINER_ID" | tail -20
        
        # Cleanup
        print_status "Stopping test container..."
        docker stop "$CONTAINER_ID" >/dev/null
        docker rm "$CONTAINER_ID" >/dev/null
        
    else
        print_error "Failed to start test container"
        exit 1
    fi
fi

# Step 5: Installation instructions
print_success "Build completed successfully!"
echo ""
echo "📦 Installation Instructions:"
echo "================================"
echo ""
echo "1. Copy the 'universal_controller' folder to your Home Assistant add-ons directory:"
echo "   /addons/universal_controller/"
echo ""
echo "2. Or for development with the Supervisor:"
echo "   docker run -d \\"
echo "     --name universal-controller \\"
echo "     -p 8099:8099 \\"
echo "     -e SUPERVISOR_TOKEN=\$SUPERVISOR_TOKEN \\"
echo "     -e HOMEASSISTANT_URL=http://supervisor/core \\"
echo "     $IMAGE_NAME:$VERSION"
echo ""
echo "3. Access the web interface at: http://your-ha-ip:8099"
echo ""
echo "4. The add-on will appear in your Home Assistant sidebar as 'Universal Controller'"
echo ""

# Step 6: Development notes
if [ "$1" = "--dev" ]; then
    echo "🔧 Development Notes:"
    echo "===================="
    echo ""
    echo "• Source code is in: universal_controller/rootfs/app/"
    echo "• Web interface: universal_controller/rootfs/app/web/"
    echo "• Configuration: universal_controller/config.yaml"
    echo "• Build artifacts are tagged as: $IMAGE_NAME:$VERSION"
    echo ""
    echo "To rebuild quickly:"
    echo "  docker build -t $IMAGE_NAME:dev universal_controller/"
    echo ""
    echo "To run in development mode:"
    echo "  docker run -it --rm -p 8099:8099 $IMAGE_NAME:dev"
    echo ""
fi

print_success "Universal Controller add-on is ready for installation!"
