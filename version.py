#!/usr/bin/env python3
"""Version management script for Universal Controller."""

import json
import sys
from pathlib import Path

def update_version(new_version: str) -> None:
    """Update version in all relevant files."""
    
    # Update VERSION file
    version_file = Path("VERSION")
    version_file.write_text(new_version)
    print(f"✅ Updated VERSION: {new_version}")
    
    # Update manifest.json
    manifest_file = Path("custom_components/universal_controller/manifest.json")
    with open(manifest_file, 'r') as f:
        manifest = json.load(f)
    
    manifest["version"] = new_version
    
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"✅ Updated manifest.json: {new_version}")
    
    # Update const.py
    const_file = Path("custom_components/universal_controller/const.py")
    const_content = const_file.read_text()
    
    # Replace VERSION line
    lines = const_content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('VERSION = '):
            lines[i] = f'VERSION = "{new_version}"'
            break
    
    const_file.write_text('\n'.join(lines))
    print(f"✅ Updated const.py: {new_version}")
    
    # Update __init__.py
    init_file = Path("custom_components/universal_controller/__init__.py")
    init_content = init_file.read_text()
    
    # Replace __version__ line
    lines = init_content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('__version__ = '):
            lines[i] = f'__version__ = "{new_version}"'
            break
    
    init_file.write_text('\n'.join(lines))
    print(f"✅ Updated __init__.py: {new_version}")

def get_current_version() -> str:
    """Get current version from VERSION file."""
    version_file = Path("VERSION")
    if version_file.exists():
        return version_file.read_text().strip()
    return "0.0.0"

def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        current = get_current_version()
        print(f"Current version: {current}")
        print("Usage: python version.py <new_version>")
        print("Example: python version.py 1.1.0")
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    # Validate version format (basic)
    if not new_version.replace('.', '').replace('-', '').replace('a', '').replace('b', '').replace('rc', '').isdigit():
        print("❌ Invalid version format. Use semantic versioning (e.g., 1.0.0)")
        sys.exit(1)
    
    print(f"🚀 Updating version to {new_version}")
    update_version(new_version)
    print(f"✅ Version updated successfully!")
    print(f"")
    print(f"Next steps:")
    print(f"1. git add .")
    print(f"2. git commit -m 'Bump version to {new_version}'")
    print(f"3. git tag v{new_version}")
    print(f"4. git push origin master --tags")

if __name__ == "__main__":
    main()
