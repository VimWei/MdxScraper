#!/usr/bin/env python3
"""Release script for MdxScraper

This script automates the version release process including:
- Version bumping using uv
- Changelog updates
- Git commits and tags
- Remote pushing

Usage:
    python scripts/release.py [bump_type]

    bump_type: patch, minor, major, alpha, beta, rc, dev
    Default: patch
"""

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Valid bump types
VALID_BUMP_TYPES = ["patch", "minor", "major", "alpha", "beta", "rc", "dev"]


def run_command(
    cmd: str, check: bool = True, capture_output: bool = True
) -> subprocess.CompletedProcess:
    """Run a command and return the result"""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
    if check and result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        sys.exit(1)
    return result


def get_current_version() -> str:
    """Get current version from uv"""
    result = run_command("uv version --short")
    return result.stdout.strip()


def check_git_status() -> bool:
    """Check if git working directory is clean"""
    result = run_command("git status --porcelain", capture_output=True)
    if result.stdout.strip():
        print("❌ Git working directory is not clean:")
        print(result.stdout)
        return False
    return True


def update_changelog(new_version: str, bump_type: str) -> None:
    """Update changelog.md with new version"""
    changelog_path = Path("docs/changelog.md")

    if not changelog_path.exists():
        print("⚠️  Warning: changelog.md not found")
        return

    print(f"📝 Updating changelog.md with version {new_version}")

    # Read existing content
    with open(changelog_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Generate new version entry
    today = datetime.now().strftime("%Y-%m-%d")

    # Determine change description based on bump type
    change_descriptions = {
        "patch": "修复版本更新",
        "minor": "功能版本更新",
        "major": "重大版本更新",
        "alpha": "Alpha 预发布版本",
        "beta": "Beta 预发布版本",
        "rc": "Release Candidate 版本",
        "dev": "开发版本",
    }

    change_desc = change_descriptions.get(bump_type, f"{bump_type} 版本更新")

    version_entry = f"""## [{new_version}] - {today}

- 自动发布: {change_desc}

"""

    # Find insertion point (after the header, before first version)
    lines = content.split("\n")
    insert_index = 0

    # Skip the header (lines starting with #)
    for i, line in enumerate(lines):
        if line.startswith("## [") and "] - " in line:
            insert_index = i
            break

    # Insert new version entry
    lines.insert(insert_index, version_entry.strip())

    # Write back to file
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Updated changelog.md with version {new_version}")


def run_tests() -> bool:
    """Run project tests"""
    print("🧪 Running tests...")
    try:
        result = run_command("uv run pytest", capture_output=False)
        print("✅ Tests passed")
        return True
    except SystemExit:
        print("❌ Tests failed")
        return False


def check_code_quality() -> bool:
    """Check code quality with black and isort"""
    print("🔍 Checking code quality...")

    try:
        # Check black formatting
        run_command("uv run black --check .", capture_output=False)
        print("✅ Black formatting check passed")

        # Check isort imports
        run_command("uv run isort --check-only .", capture_output=False)
        print("✅ Import sorting check passed")

        return True
    except SystemExit:
        print("❌ Code quality checks failed")
        return False


def release(bump_type: str = "patch") -> None:
    """Release a new version"""
    print(f"🚀 Starting {bump_type} release...")
    print("=" * 50)

    # Validate bump type
    if bump_type not in VALID_BUMP_TYPES:
        print(f"❌ Invalid bump type: {bump_type}")
        print(f"Valid types: {', '.join(VALID_BUMP_TYPES)}")
        sys.exit(1)

    # 1. Check git status
    print("1️⃣ Checking git status...")
    if not check_git_status():
        print("❌ Please commit or stash your changes before releasing")
        sys.exit(1)
    print("✅ Git working directory is clean")

    # 2. Run tests
    print("\n2️⃣ Running tests...")
    if not run_tests():
        print("❌ Tests failed. Please fix tests before releasing")
        sys.exit(1)

    # 3. Check code quality
    print("\n3️⃣ Checking code quality...")
    if not check_code_quality():
        print("❌ Code quality checks failed. Please fix issues before releasing")
        sys.exit(1)

    # 4. Preview version change
    print(f"\n4️⃣ Previewing version change...")
    result = run_command(f"uv version --dry-run --bump {bump_type}")
    print(f"📋 {result.stdout.strip()}")

    # 5. Confirm release
    print(f"\n5️⃣ Confirmation")
    confirm = input("🤔 Continue with release? (y/N): ")
    if confirm.lower() != "y":
        print("❌ Release cancelled")
        return

    # 6. Update version
    print(f"\n6️⃣ Updating version...")
    run_command(f"uv version --bump {bump_type}")

    # 7. Get new version
    new_version = get_current_version()
    print(f"✅ New version: {new_version}")

    # 8. Update changelog
    print(f"\n7️⃣ Updating changelog...")
    update_changelog(new_version, bump_type)

    # 9. Commit changes
    print(f"\n8️⃣ Committing changes...")
    run_command("git add pyproject.toml docs/changelog.md")
    run_command(f"git commit -m 'Bump version to {new_version}'")
    print("✅ Changes committed")

    # 10. Create tag
    print(f"\n9️⃣ Creating tag...")
    run_command(f"git tag v{new_version}")
    print(f"✅ Tag v{new_version} created")

    # 11. Push to remote
    print(f"\n🔟 Pushing to remote...")
    run_command("git push origin main --tags")
    print("✅ Pushed to remote")

    # 12. Success message
    print(f"\n🎉 Release {new_version} completed successfully!")
    print("=" * 50)
    print(f"📋 Next steps:")
    print(f"   1. Create GitHub Release: https://github.com/VimWei/MdxScraper/releases/new")
    print(f"   2. Select tag: v{new_version}")
    print(f"   3. Copy changelog content for release notes")
    print(f"   4. Publish the release")
    print("=" * 50)


def show_help() -> None:
    """Show help message"""
    print(__doc__)
    print(f"\nValid bump types:")
    for bump_type in VALID_BUMP_TYPES:
        print(f"  - {bump_type}")


def main() -> None:
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help", "help"]:
            show_help()
            return
        bump_type = sys.argv[1]
    else:
        bump_type = "patch"

    try:
        release(bump_type)
    except KeyboardInterrupt:
        print("\n❌ Release cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
