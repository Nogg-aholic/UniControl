#!/bin/bash
# Create GitHub release for Universal Controller

VERSION="1.1.0"
TAG="v${VERSION}"

echo "🚀 Creating GitHub release for Universal Controller v${VERSION}"

# Check if git tag exists
if git tag -l | grep -q "^${TAG}$"; then
    echo "✅ Tag ${TAG} already exists"
else
    echo "📝 Creating tag ${TAG}"
    git tag -a "${TAG}" -m "Release Universal Controller ${VERSION}"
    git push origin "${TAG}"
fi

echo ""
echo "📦 Next steps:"
echo "1. Go to: https://github.com/Nogg-aholic/UniControl/releases"
echo "2. Click 'Create a new release'"
echo "3. Choose tag: ${TAG}"
echo "4. Title: Universal Controller ${VERSION}"
echo "5. Description: See CHANGELOG.md for details"
echo "6. Upload the zip file or let GitHub auto-generate"
echo ""
echo "Or use GitHub CLI:"
echo "gh release create ${TAG} --title 'Universal Controller ${VERSION}' --notes-file CHANGELOG.md"
