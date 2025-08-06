#!/usr/bin/env python3
# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "7037bed8-d479-44e6-9198-c81f69b9d05d"
#   Timestamp: "2025-08-05T20:50:09+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则) + 自动化测试"
#   Quality_Check: "全面的测试运行器，支持不同测试级别和覆盖率报告"
# }}
# {{START_MODIFICATIONS}}
"""
Test Runner for FastMCP SSH Server

This script provides comprehensive test execution with coverage reporting,
different test levels, and detailed output formatting.

Usage:
    python tests/run_tests.py                    # Run all tests
    python tests/run_tests.py --unit             # Run only unit tests
    python tests/run_tests.py --integration      # Run only integration tests
    python tests/run_tests.py --coverage         # Run with detailed coverage
    python tests/run_tests.py --fast             # Run fast tests only
    python tests/run_tests.py --verbose          # Verbose output
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Add the python_src directory to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "python_src"))


class TestRunner:
    """Comprehensive test runner for FastMCP SSH server."""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.test_dir = self.project_root / "tests"
        self.coverage_dir = self.project_root / "htmlcov"
        self.python_src = self.project_root / "python_src"

    def run_command(
        self, cmd: list[str], capture_output: bool = False
    ) -> subprocess.CompletedProcess:
        """Run a command and return the result."""
        print(f"🔧 Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=capture_output,
                text=True,
                check=False,
            )
            return result
        except Exception as e:
            print(f"❌ Command failed: {e}")
            sys.exit(1)

    def check_dependencies(self) -> bool:
        """Check if required testing dependencies are installed."""
        print("🔍 Checking test dependencies...")

        required_packages = ["pytest", "pytest-asyncio", "pytest-cov", "pytest-mock"]

        missing_packages = []

        for package in required_packages:
            result = self.run_command(
                [sys.executable, "-c", f"import {package.replace('-', '_')}"],
                capture_output=True,
            )

            if result.returncode != 0:
                missing_packages.append(package)

        if missing_packages:
            print(f"❌ Missing required packages: {', '.join(missing_packages)}")
            print("💡 Install with: uv add --dev " + " ".join(missing_packages))
            return False

        print("✅ All test dependencies are available")
        return True

    def run_unit_tests(self, verbose: bool = False, coverage: bool = True) -> bool:
        """Run unit tests."""
        print("\n🧪 Running Unit Tests")
        print("=" * 50)

        cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(self.test_dir / "test_ssh_manager.py"),
            str(self.test_dir / "test_mcp_tools.py"),
            str(self.test_dir / "test_cli.py"),
            "-m",
            "not integration",
        ]

        if verbose:
            cmd.extend(["-v", "--tb=long"])

        if coverage:
            cmd.extend(["--cov=python_src/python_ssh_mcp", "--cov-report=term-missing"])

        result = self.run_command(cmd)
        return result.returncode == 0

    def run_integration_tests(
        self, verbose: bool = False, coverage: bool = True
    ) -> bool:
        """Run integration tests."""
        print("\n🔗 Running Integration Tests")
        print("=" * 50)

        cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(self.test_dir / "test_integration.py"),
            "-m",
            "integration or not unit",
        ]

        if verbose:
            cmd.extend(["-v", "--tb=long"])

        if coverage:
            cmd.extend(
                [
                    "--cov=python_src/python_ssh_mcp",
                    "--cov-report=term-missing",
                    "--cov-append",  # Append to existing coverage
                ]
            )

        result = self.run_command(cmd)
        return result.returncode == 0

    def run_all_tests(self, verbose: bool = False, coverage: bool = True) -> bool:
        """Run all tests."""
        print("\n🚀 Running All Tests")
        print("=" * 50)

        cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(self.test_dir),
            "--maxfail=10",  # Stop after 10 failures
        ]

        if verbose:
            cmd.extend(["-v", "--tb=long"])
        else:
            cmd.extend(["--tb=short"])

        if coverage:
            cmd.extend(
                [
                    "--cov=python_src/python_ssh_mcp",
                    "--cov-report=term-missing",
                    "--cov-report=html",
                    "--cov-fail-under=90",
                ]
            )

        result = self.run_command(cmd)
        return result.returncode == 0

    def run_fast_tests(self, verbose: bool = False) -> bool:
        """Run only fast tests (exclude slow tests)."""
        print("\n⚡ Running Fast Tests")
        print("=" * 50)

        cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(self.test_dir),
            "-m",
            "not slow",
            "--maxfail=5",
        ]

        if verbose:
            cmd.extend(["-v"])

        result = self.run_command(cmd)
        return result.returncode == 0

    def generate_coverage_report(self) -> bool:
        """Generate detailed coverage report."""
        print("\n📊 Generating Coverage Report")
        print("=" * 50)

        # Generate HTML coverage report
        cmd = [
            sys.executable,
            "-m",
            "coverage",
            "html",
            "--directory",
            str(self.coverage_dir),
        ]

        result = self.run_command(cmd)

        if result.returncode == 0:
            print(f"✅ Coverage report generated: {self.coverage_dir}/index.html")

            # Generate coverage summary
            summary_cmd = [sys.executable, "-m", "coverage", "report"]
            summary_result = self.run_command(summary_cmd)

            return summary_result.returncode == 0

        return False

    def lint_code(self) -> bool:
        """Run linting on the codebase."""
        print("\n🔍 Running Code Linting")
        print("=" * 50)

        success = True

        # Run ruff
        print("Running ruff...")
        ruff_result = self.run_command(
            [sys.executable, "-m", "ruff", "check", str(self.python_src)]
        )
        if ruff_result.returncode != 0:
            success = False

        # Run mypy
        print("Running mypy...")
        mypy_result = self.run_command(
            [sys.executable, "-m", "mypy", str(self.python_src)]
        )
        if mypy_result.returncode != 0:
            print("⚠️  MyPy found issues (not failing build)")

        return success

    def run_security_tests(self) -> bool:
        """Run security-focused tests."""
        print("\n🔒 Running Security Tests")
        print("=" * 50)

        cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(self.test_dir),
            "-m",
            "security",
            "-v",
        ]

        result = self.run_command(cmd)
        return result.returncode == 0

    def cleanup_test_artifacts(self) -> None:
        """Clean up test artifacts."""
        print("\n🧹 Cleaning up test artifacts...")

        # Remove coverage files
        for pattern in [".coverage", ".coverage.*"]:
            for file in self.project_root.glob(pattern):
                file.unlink(missing_ok=True)

        # Remove __pycache__ directories
        for cache_dir in self.project_root.rglob("__pycache__"):
            if cache_dir.is_dir():
                shutil.rmtree(cache_dir)

        # Remove pytest cache
        pytest_cache = self.project_root / ".pytest_cache"
        if pytest_cache.exists():
            shutil.rmtree(pytest_cache)

        print("✅ Test artifacts cleaned up")

    def display_summary(self, results: dict) -> None:
        """Display test run summary."""
        print("\n" + "=" * 60)
        print("📋 Test Run Summary")
        print("=" * 60)

        total_passed = 0
        total_run = 0

        for test_type, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"  {test_type:.<40} {status}")
            total_run += 1
            if passed:
                total_passed += 1

        print("-" * 60)
        print(f"Total: {total_passed}/{total_run} test suites passed")

        if total_passed == total_run:
            print("🎉 All tests passed!")
            return True
        else:
            print("❌ Some tests failed")
            return False


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(
        description="FastMCP SSH Server Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument(
        "--integration", action="store_true", help="Run only integration tests"
    )
    parser.add_argument(
        "--fast", action="store_true", help="Run only fast tests (exclude slow tests)"
    )
    parser.add_argument(
        "--security", action="store_true", help="Run only security tests"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Generate detailed coverage report"
    )
    parser.add_argument("--lint", action="store_true", help="Run code linting")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--no-coverage", action="store_true", help="Disable coverage reporting"
    )
    parser.add_argument(
        "--cleanup", action="store_true", help="Clean up test artifacts and exit"
    )

    args = parser.parse_args()

    runner = TestRunner()

    # Handle cleanup-only request
    if args.cleanup:
        runner.cleanup_test_artifacts()
        return

    print("🧪 FastMCP SSH Server Test Suite")
    print("=" * 60)

    # Check dependencies
    if not runner.check_dependencies():
        sys.exit(1)

    results = {}
    enable_coverage = not args.no_coverage

    try:
        # Run linting if requested
        if args.lint:
            results["Linting"] = runner.lint_code()

        # Run specific test suites
        if args.unit:
            results["Unit Tests"] = runner.run_unit_tests(args.verbose, enable_coverage)
        elif args.integration:
            results["Integration Tests"] = runner.run_integration_tests(
                args.verbose, enable_coverage
            )
        elif args.fast:
            results["Fast Tests"] = runner.run_fast_tests(args.verbose)
        elif args.security:
            results["Security Tests"] = runner.run_security_tests()
        else:
            # Run all tests by default
            results["All Tests"] = runner.run_all_tests(args.verbose, enable_coverage)

        # Generate coverage report if requested
        if args.coverage and enable_coverage:
            results["Coverage Report"] = runner.generate_coverage_report()

        # Display summary
        success = runner.display_summary(results)

        if not success:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️  Test run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test run failed with error: {e}")
        sys.exit(1)
    finally:
        # Always offer cleanup
        if not args.cleanup:
            print("\n💡 Run with --cleanup to remove test artifacts")


if __name__ == "__main__":
    main()
# {{END_MODIFICATIONS}}
