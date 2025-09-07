#!/usr/bin/env python3
"""
Code formatting and linting script for Solar Analysis API

This script provides comprehensive code formatting and linting using:
- pylint: Code analysis and quality checks
- black: Code formatting
- isort: Import sorting
- flake8: Style guide enforcement
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
SOURCE_DIRS = ["src/", "tests/", "scripts/"]


def run_command(command, description="", check=True):
    """Run a shell command and handle errors."""
    print(f"📋 {description}")
    print(f"🔧 Running: {' '.join(command)}")

    try:
        result = subprocess.run(
            command, cwd=PROJECT_ROOT, capture_output=True, text=True, check=check
        )

        if result.stdout:
            print(result.stdout)

        if result.stderr and result.returncode != 0:
            print(f"❌ Error: {result.stderr}", file=sys.stderr)
            return False

        print(f"✅ {description} completed successfully\n")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        if e.stderr:
            print(f"Error output: {e.stderr}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {command[0]}")
        print(f"💡 Install with: pip install {command[0]}")
        return False


def install_dependencies():
    """Install required formatting and linting tools."""
    dependencies = [
        "pylint>=2.17.0",
        "black>=23.0.0",
        "isort>=5.12.0",
        "flake8>=6.0.0",
        "mypy>=1.0.0",
    ]

    print("📦 Installing formatting and linting dependencies...")
    for dep in dependencies:
        success = run_command(
            ["pip", "install", dep], f"Installing {dep.split('>=')[0]}", check=False
        )
        if not success:
            print(f"⚠️  Failed to install {dep}, continuing...")


def format_with_black(fix=False):
    """Format code with Black."""
    command = ["black"]
    if not fix:
        command.append("--check")
        command.append("--diff")

    command.extend(SOURCE_DIRS)

    return run_command(
        command,
        "Formatting code with Black" if fix else "Checking Black formatting",
        check=fix,
    )


def sort_imports_with_isort(fix=False):
    """Sort imports with isort."""
    command = ["isort"]
    if not fix:
        command.append("--check-only")
        command.append("--diff")

    command.extend(SOURCE_DIRS)

    return run_command(
        command,
        "Sorting imports with isort" if fix else "Checking import sorting",
        check=fix,
    )


def lint_with_flake8():
    """Check code style with flake8."""
    return run_command(
        ["flake8"] + SOURCE_DIRS, "Checking code style with flake8", check=False
    )


def analyze_with_pylint():
    """Analyze code with pylint."""
    return run_command(
        ["pylint"] + SOURCE_DIRS, "Analyzing code with pylint", check=False
    )


def type_check_with_mypy():
    """Type check with mypy."""
    return run_command(["mypy"] + SOURCE_DIRS, "Type checking with mypy", check=False)


def generate_pylint_report():
    """Generate detailed pylint report."""
    report_file = PROJECT_ROOT / "reports" / "pylint_report.txt"
    report_file.parent.mkdir(exist_ok=True)

    command = [
        "pylint",
        "--output-format=text",
        f"--reports=y",
        "--score=y",
    ] + SOURCE_DIRS

    print(f"📊 Generating detailed pylint report to {report_file}")

    try:
        with open(report_file, "w") as f:
            result = subprocess.run(
                command, cwd=PROJECT_ROOT, stdout=f, stderr=subprocess.PIPE, text=True
            )

        if result.stderr:
            print(f"Warning: {result.stderr}")

        print(f"✅ Pylint report saved to {report_file}")
        return True

    except Exception as e:
        print(f"❌ Failed to generate pylint report: {e}")
        return False


def main():
    """Main function to handle command line arguments and run formatters."""
    parser = argparse.ArgumentParser(
        description="Format and lint Solar Analysis API code"
    )

    parser.add_argument(
        "--install", action="store_true", help="Install required dependencies"
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check formatting/linting without fixing (default)",
    )

    parser.add_argument(
        "--fix", action="store_true", help="Fix formatting issues automatically"
    )

    parser.add_argument(
        "--report", action="store_true", help="Generate detailed pylint report"
    )

    parser.add_argument(
        "--tool",
        choices=["black", "isort", "flake8", "pylint", "mypy"],
        help="Run only specific tool",
    )

    args = parser.parse_args()

    # Change to project root
    os.chdir(PROJECT_ROOT)
    print(f"🚀 Running formatters from: {PROJECT_ROOT}")

    # Install dependencies if requested
    if args.install:
        install_dependencies()
        return

    # Generate report if requested
    if args.report:
        generate_pylint_report()
        return

    # Determine if we should fix issues
    should_fix = args.fix and not args.check

    success_count = 0
    total_count = 0

    # Run specific tool or all tools
    if args.tool:
        total_count = 1
        if args.tool == "black":
            success_count += format_with_black(should_fix)
        elif args.tool == "isort":
            success_count += sort_imports_with_isort(should_fix)
        elif args.tool == "flake8":
            success_count += lint_with_flake8()
        elif args.tool == "pylint":
            success_count += analyze_with_pylint()
        elif args.tool == "mypy":
            success_count += type_check_with_mypy()
    else:
        # Run all tools
        tools = [
            ("Black formatting", lambda: format_with_black(should_fix)),
            ("Import sorting", lambda: sort_imports_with_isort(should_fix)),
            ("Flake8 linting", lint_with_flake8),
            ("Pylint analysis", analyze_with_pylint),
            ("MyPy type checking", type_check_with_mypy),
        ]

        for tool_name, tool_func in tools:
            total_count += 1
            print(f"\n{'=' * 60}")
            print(f"🔍 Running {tool_name}")
            print("=" * 60)

            if tool_func():
                success_count += 1
            else:
                print(f"⚠️  {tool_name} found issues")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {success_count}/{total_count}")
    print(f"❌ With issues: {total_count - success_count}/{total_count}")

    if success_count == total_count:
        print("🎉 All checks passed!")
        sys.exit(0)
    else:
        print("⚠️  Some checks found issues. Review the output above.")
        if not should_fix:
            print("💡 Run with --fix to automatically fix formatting issues")
        sys.exit(1)


if __name__ == "__main__":
    main()
