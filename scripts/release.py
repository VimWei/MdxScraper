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

import subprocess
import sys
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Optional

# Valid bump types
VALID_BUMP_TYPES = ["patch", "minor", "major", "alpha", "beta", "rc", "dev"]


def get_project_url() -> str:
    """Get project URL from pyproject.toml"""
    try:
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
        return data.get("project", {}).get("urls", {}).get("Homepage", "")
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError):
        return ""


def get_releases_url() -> str:
    """Get project releases URL"""
    project_url = get_project_url()
    if project_url and project_url.endswith("/"):
        return f"{project_url}releases"
    elif project_url:
        return f"{project_url}/releases"
    else:
        return ""


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
    """Guardrail around staged/unstaged changes.

    - Allow unstaged changes (they won't be included in the release commit).
    - Disallow unrelated staged changes to avoid mixing content into the release commit.
      Only allow these staged paths (which the script itself stages):
        - pyproject.toml
        - uv.lock
        - docs/changelog.md
    Returns True if it's safe to proceed, otherwise False.
    """
    result = run_command("git status --porcelain", capture_output=True)
    output = result.stdout.splitlines()

    allowed_staged = {"pyproject.toml", "uv.lock", "docs/changelog.md"}
    other_staged: list[str] = []
    has_unstaged = False

    for line in output:
        # Porcelain format: XY <path>
        if not line:
            continue
        status = line[:2]
        path = line[3:].strip()
        staged_flag = status[0]
        unstaged_flag = status[1]

        if staged_flag != " ":
            # Something is staged
            if path not in allowed_staged:
                other_staged.append(path)
        if unstaged_flag != " ":
            has_unstaged = True

    if other_staged:
        print("❌ Found unrelated staged changes that could be mixed into the release commit:")
        for p in other_staged:
            print(f"   - {p}")
        print("Please commit or unstage these before releasing.")
        return False

    if has_unstaged:
        print("ℹ️  Unstaged changes detected. They will NOT be included in the release commit.")

    return True


def _git_output(cmd: str) -> str:
    """Run a git command and return stdout (empty if fails)."""
    try:
        result = run_command(cmd, check=True)
        return result.stdout.strip()
    except SystemExit:
        return ""


def _collect_commits_since_last_tag() -> list[str]:
    """Collect commit subjects since the previous tag.

    Falls back to the last 20 commits if no previous tag exists.
    """
    # Previous tag (exclude current HEAD's tag if already tagged)
    prev_tag = _git_output("git describe --tags --abbrev=0 2>NUL || true")
    rev_range = f"{prev_tag}..HEAD" if prev_tag else "HEAD~20..HEAD"
    log = _git_output(f"git log --pretty=format:%s --no-merges {rev_range}")
    subjects = [line.strip() for line in log.splitlines() if line.strip()]
    # Filter out non-essential style-only commits created during release formatting
    subjects = [s for s in subjects if s != "Style: format with isort/black"]
    return subjects


def update_changelog(new_version: str, bump_type: str) -> None:
    """Update changelog.md with new version.

    Generates the section body from recent commit messages to make entries meaningful.
    """
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

    # Build bullets from commits
    commits = _collect_commits_since_last_tag()
    if commits:
        bullets = "\n".join(f"- {c}" for c in commits)
    else:
        bullets = f"- 自动发布: {change_desc}"

    version_entry = f"""## [{new_version}] - {today}

{bullets}

"""

    # Find insertion point (after the header, before first version)
    lines = content.split("\n")
    insert_index = 0

    # Skip the header (lines starting with #)
    for i, line in enumerate(lines):
        if line.startswith("## [") and "] - " in line:
            insert_index = i
            break

    # Insert new version entry and ensure a blank line separates sections
    lines.insert(insert_index, version_entry.strip() + "\n")

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


def _stash_unstaged_if_any() -> tuple[bool, str]:
    """Stash unstaged/untracked changes keeping index. Returns (stashed, stash_name)."""
    status_lines = run_command("git status --porcelain", capture_output=True).stdout.splitlines()
    has_unstaged = any(line and line[1] != " " for line in status_lines)
    has_untracked = any(line.startswith("?? ") for line in status_lines)
    if not has_unstaged and not has_untracked:
        return False, ""
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    name = f"release-temp-{stamp}"
    # Keep index (-k), include untracked (-u)
    run_command(f"git stash push -u -k -m {name}")
    return True, name


def _pop_stash_quiet() -> None:
    # Pop latest stash quietly (ignore failures)
    run_command("git stash pop -q", check=False)


def _auto_fix_code_style() -> bool:
    """Attempt to auto-fix code style issues using isort + black.

    Returns True if auto-fix completed successfully, otherwise False.
    """
    print("🛠️  Attempting to auto-fix style (isort + black)...")
    try:
        run_command("uv run isort .", capture_output=False)
        run_command("uv run black .", capture_output=False)
        print("✅ Auto-fix completed")
        return True
    except SystemExit:
        print("❌ Auto-fix failed")
        return False


def check_code_quality() -> bool:
    """Check code quality on the release snapshot and optionally sync formatting.

    - Temporarily stash unstaged/untracked changes to isolate the release snapshot
    - Run checks; on failure, offer auto-fix and optional style commit
    - Restore stashed changes and optionally apply the same formatting to working tree (no commit)
    """
    print("🔍 Checking code quality...")

    # 1) Isolate release snapshot from local unstaged changes
    print("🧩 Preparing release snapshot (stash unstaged/untracked, keep index)...")
    stashed, _stash_name = _stash_unstaged_if_any()
    if stashed:
        print("🧩 Release snapshot ready (working tree now reflects what will be released)")
    else:
        print("🧩 No unstaged/untracked changes found; using current tree as release snapshot")
    try:
        try:
            run_command("uv run black --check .", capture_output=False)
            print("✅ Black formatting check passed")
            run_command("uv run isort --check-only .", capture_output=False)
            print("✅ Import sorting check passed")
            return True
        except SystemExit:
            print("❌ Code quality checks failed\n")
            try_fix = input("🔧 Auto-fix with isort+black on release snapshot? (y/N): ")
            if try_fix.lower() != "y":
                return False

            # Run auto-fix on the release snapshot
            if not _auto_fix_code_style():
                return False
            # Mandatory: create a separate Style commit for snapshot formatting
            print("\n📦 Creating 'Style: format with isort/black' commit (release snapshot)...")
            run_command("git add .")
            run_command('git commit -m "Style: format with isort/black"')
            print("📦 Style commit created on release snapshot")

            # Re-check
            try:
                run_command("uv run black --check .", capture_output=False)
                run_command("uv run isort --check-only .", capture_output=False)
                print("✅ Code quality checks passed after auto-fix")
                return True
            except SystemExit:
                print("❌ Checks still failing after auto-fix")
                return False
    finally:
        # 2) Restore user's unstaged changes and optionally sync formatting to working tree
        if stashed:
            print("\n🔁 Restoring your unstaged changes from stash...")
            _pop_stash_quiet()
            # Mandatory: sync formatting across the working tree (no commit)
            print("\n♻️  Sync formatting in working tree (no commit)...")
            run_command("uv run isort .", capture_output=False)
            run_command("uv run black .", capture_output=False)
            print("♻️  Workspace formatting synced")


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
    print("1. Checking git status...")
    if not check_git_status():
        print("❌ Please commit or stash your changes before releasing")
        sys.exit(1)
    print("✅ Git working directory is clean")

    # 2. Run tests
    print("\n2. Running tests...")
    if not run_tests():
        print("❌ Tests failed. Please fix tests before releasing")
        sys.exit(1)

    # 3. Check code quality
    print("\n3. Checking code quality...")
    if not check_code_quality():
        print("❌ Code quality checks failed. Please fix issues before releasing")
        sys.exit(1)

    # 4. Preview version change
    print(f"\n4. Previewing version change...")
    result = run_command(f"uv version --dry-run --bump {bump_type}")
    print(f"📋 {result.stdout.strip()}")

    # 5. Confirm release
    print(f"\n5. Confirmation")
    confirm = input("🤔 Continue with release? (y/N): ")
    if confirm.lower() != "y":
        print("❌ Release cancelled")
        return

    # 6. Update version
    print(f"\n6. Updating version...")
    run_command(f"uv version --bump {bump_type}")

    # 7. Get new version
    new_version = get_current_version()
    print(f"✅ New version: {new_version}")

    # 8. Update changelog
    print(f"\n7. Updating changelog...")
    update_changelog(new_version, bump_type)

    # 9. Commit changes
    print(f"\n8. Committing changes...")
    # Stage version, lockfile (if changed), and changelog together
    run_command("git add pyproject.toml uv.lock docs/changelog.md")
    # Use double quotes for Windows shell compatibility
    run_command(f'git commit -m "Bump version to {new_version}"')
    print("✅ Changes committed")

    # 10. Create tag
    print(f"\n9. Creating tag...")
    run_command(f"git tag v{new_version}")
    print(f"✅ Tag v{new_version} created")

    # 11. Push to remote
    print(f"\n10. Pushing to remote...")
    run_command("git push origin main --tags")
    print("✅ Pushed to remote")

    # 12. Success message
    print(f"\n🎉 Release {new_version} completed successfully!")
    
    # Show releases URL if available
    releases_url = get_releases_url()
    if releases_url:
        print(f"📦 View releases: {releases_url}")


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
