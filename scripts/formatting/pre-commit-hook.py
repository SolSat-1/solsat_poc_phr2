#!/usr/bin/env python3
"""
Pre-commit hook for code quality checks

This script runs before each commit to ensure code quality.
It performs formatting checks and basic linting.
"""

import sys
import subprocess
from pathlib import Path

# Colors for output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def run_check(command, description):
    """Run a command and return success status."""
    print(f"{BLUE}🔍 {description}...{RESET}")

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, cwd=Path(__file__).parent.parent
        )

        if result.returncode == 0:
            print(f"{GREEN}✅ {description} passed{RESET}")
            return True
        else:
            print(f"{RED}❌ {description} failed{RESET}")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return False

    except FileNotFoundError:
        print(f"{YELLOW}⚠️  Command not found: {command[0]}{RESET}")
        print(f"{YELLOW}💡 Install with: pip install {command[0]}{RESET}")
        return False


def main():
    """Main pre-commit hook logic."""
    print(f"{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}🚀 Running pre-commit checks for Solar Analysis API{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")

    # Get list of Python files that are staged for commit
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
        )

        staged_files = [
            f
            for f in result.stdout.strip().split("\n")
            if f.endswith(".py")
            and (
                f.startswith("src/")
                or f.startswith("tests/")
                or f.startswith("scripts/")
            )
        ]

        if not staged_files:
            print(f"{YELLOW}ℹ️  No Python files staged for commit{RESET}")
            return True

        print(f"{BLUE}📁 Checking {len(staged_files)} staged Python files{RESET}")

    except subprocess.CalledProcessError:
        print(f"{RED}❌ Failed to get staged files{RESET}")
        return False

    # Run checks
    checks = [
        (
            [
                "python",
                "scripts/formatting/format_code.py",
                "--tool",
                "black",
                "--check",
            ],
            "Black formatting check",
        ),
        (
            [
                "python",
                "scripts/formatting/format_code.py",
                "--tool",
                "isort",
                "--check",
            ],
            "Import sorting check",
        ),
        (
            ["python", "scripts/formatting/format_code.py", "--tool", "flake8"],
            "Flake8 style check",
        ),
    ]

    success_count = 0
    total_checks = len(checks)

    for command, description in checks:
        if run_check(command, description):
            success_count += 1
        else:
            # Show helpful message for fixes
            tool = command[3]  # Extract tool name
            if tool in ["black", "isort"]:
                print(f"{YELLOW}💡 Fix with: make {tool}{RESET}")

    print(f"{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}📊 Pre-commit Summary{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")

    if success_count == total_checks:
        print(f"{GREEN}✅ All checks passed! ({success_count}/{total_checks}){RESET}")
        print(f"{GREEN}🚀 Ready to commit!{RESET}")
        return True
    else:
        print(
            f"{RED}❌ {total_checks - success_count}/{total_checks} checks failed{RESET}"
        )
        print(f"{YELLOW}💡 Fix issues before committing:{RESET}")
        print(f"{YELLOW}   - Run: make format{RESET}")
        print(f"{YELLOW}   - Or: python scripts/formatting/format_code.py --fix{RESET}")
        print(f"{YELLOW}   - Then: git add . && git commit{RESET}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
