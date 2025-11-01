"""
Unified Test Runner for CrewAI Local.

This script provides a convenient way to run different test suites.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_pytest(args: list[str]) -> int:
    """Run pytest with given arguments."""
    cmd = ["pytest"] + args
    print(f"\n🧪 Running: {' '.join(cmd)}\n")
    return subprocess.call(cmd)


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(
        description="CrewAI Local Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python tests/run_all_tests.py

  # Run only MCP tests
  python tests/run_all_tests.py --mcp

  # Run with coverage
  python tests/run_all_tests.py --coverage

  # Run specific test file
  python tests/run_all_tests.py --file tests/mcp/test_search.py

  # Run fast tests only (skip slow)
  python tests/run_all_tests.py --fast
        """
    )

    parser.add_argument(
        "--mcp",
        action="store_true",
        help="Run only MCP tool tests"
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run only integration tests"
    )
    parser.add_argument(
        "--experimental",
        action="store_true",
        help="Run only experimental tests"
    )
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run only unit tests"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage report"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip slow tests"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Run specific test file"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--failed",
        action="store_true",
        help="Run only previously failed tests"
    )

    args = parser.parse_args()

    # Build pytest arguments
    pytest_args = ["tests/"]

    # Specific test categories
    if args.mcp:
        pytest_args = ["tests/mcp/"]
    elif args.integration:
        pytest_args = ["tests/integration/"]
    elif args.experimental:
        pytest_args = ["tests/experimental/"]
    elif args.unit:
        pytest_args = ["tests/unit/"]
    elif args.file:
        pytest_args = [args.file]

    # Add options
    if args.coverage:
        pytest_args.extend([
            "--cov=src/crewai_local",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])

    if args.fast:
        pytest_args.append("-m")
        pytest_args.append("not slow")

    if args.verbose:
        pytest_args.append("-vv")

    if args.failed:
        pytest_args.append("--lf")  # Last failed

    # Print header
    print("=" * 70)
    print("🧪 CrewAI Local Test Suite v2.2")
    print("=" * 70)

    # Run tests
    exit_code = run_pytest(pytest_args)

    # Print summary
    print("\n" + "=" * 70)
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ Tests failed with exit code: {exit_code}")
    print("=" * 70)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
