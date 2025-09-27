#!/usr/bin/env python3
"""
Comprehensive Test Runner for SaaS Cafeterías
=============================================

Advanced test runner with multiple execution modes, reporting, and analysis.
Provides comprehensive testing coverage for the entire application.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --fast             # Run only fast tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --security         # Run only security tests
    python run_tests.py --performance      # Run only performance tests
    python run_tests.py --coverage         # Run with coverage report
    python run_tests.py --verbose          # Verbose output
    python run_tests.py --parallel         # Run tests in parallel
    python run_tests.py --report           # Generate detailed report
"""

import os
import sys
import subprocess
import argparse
import time
import json
from datetime import datetime
from pathlib import Path

class TestRunner:
    """Advanced test runner with comprehensive features."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_dir = self.project_root / "tests"
        self.reports_dir = self.project_root / "test_reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Test markers and their descriptions
        self.test_markers = {
            "unit": "Unit tests - fast, isolated component tests",
            "integration": "Integration tests - component interaction tests",
            "e2e": "End-to-end tests - complete workflow tests",
            "security": "Security tests - vulnerability and protection tests",
            "performance": "Performance tests - speed and load tests",
            "api": "API tests - endpoint and interface tests",
            "database": "Database tests - model and query tests",
            "auth": "Authentication tests - login and authorization tests",
            "business": "Business logic tests - domain logic tests",
            "smoke": "Smoke tests - basic functionality verification",
            "regression": "Regression tests - prevent breaking changes",
            "critical": "Critical tests - essential functionality",
            "slow": "Slow tests - long-running tests",
            "fast": "Fast tests - quick execution tests"
        }
    
    def parse_arguments(self):
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(
            description="Comprehensive Test Runner for SaaS Cafeterías",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self._get_examples()
        )
        
        # Test selection options
        parser.add_argument("--all", action="store_true", default=True,
                          help="Run all tests (default)")
        parser.add_argument("--unit", action="store_true",
                          help="Run only unit tests")
        parser.add_argument("--integration", action="store_true", 
                          help="Run only integration tests")
        parser.add_argument("--e2e", action="store_true",
                          help="Run only end-to-end tests")
        parser.add_argument("--security", action="store_true",
                          help="Run only security tests")
        parser.add_argument("--performance", action="store_true",
                          help="Run only performance tests")
        parser.add_argument("--api", action="store_true",
                          help="Run only API tests")
        parser.add_argument("--database", action="store_true",
                          help="Run only database tests")
        parser.add_argument("--auth", action="store_true",
                          help="Run only authentication tests")
        parser.add_argument("--business", action="store_true",
                          help="Run only business logic tests")
        parser.add_argument("--smoke", action="store_true",
                          help="Run only smoke tests")
        parser.add_argument("--regression", action="store_true",
                          help="Run only regression tests")
        parser.add_argument("--critical", action="store_true",
                          help="Run only critical tests")
        parser.add_argument("--fast", action="store_true",
                          help="Run only fast tests")
        parser.add_argument("--slow", action="store_true",
                          help="Run only slow tests")
        
        # Execution options
        parser.add_argument("--parallel", "-p", action="store_true",
                          help="Run tests in parallel")
        parser.add_argument("--workers", "-w", type=int, default=4,
                          help="Number of parallel workers (default: 4)")
        parser.add_argument("--verbose", "-v", action="store_true",
                          help="Verbose output")
        parser.add_argument("--quiet", "-q", action="store_true",
                          help="Quiet output")
        parser.add_argument("--maxfail", type=int, default=5,
                          help="Maximum number of failures before stopping")
        
        # Coverage options
        parser.add_argument("--coverage", "-c", action="store_true",
                          help="Generate coverage report")
        parser.add_argument("--coverage-html", action="store_true",
                          help="Generate HTML coverage report")
        parser.add_argument("--coverage-xml", action="store_true",
                          help="Generate XML coverage report")
        parser.add_argument("--coverage-fail-under", type=int, default=85,
                          help="Fail if coverage is below threshold (default: 85)")
        
        # Reporting options
        parser.add_argument("--report", "-r", action="store_true",
                          help="Generate detailed test report")
        parser.add_argument("--json-report", action="store_true",
                          help="Generate JSON test report")
        parser.add_argument("--html-report", action="store_true",
                          help="Generate HTML test report")
        parser.add_argument("--junit-xml", action="store_true",
                          help="Generate JUnit XML report")
        
        # Filter options
        parser.add_argument("--keyword", "-k", type=str,
                          help="Run tests matching keyword expression")
        parser.add_argument("--file", "-f", type=str,
                          help="Run tests from specific file")
        parser.add_argument("--exclude", "-x", type=str, action="append",
                          help="Exclude tests matching pattern")
        
        # Environment options
        parser.add_argument("--env", type=str, default="test",
                          help="Test environment (default: test)")
        parser.add_argument("--database-url", type=str,
                          help="Override database URL for tests")
        parser.add_argument("--redis-url", type=str,
                          help="Override Redis URL for tests")
        
        # Debug options
        parser.add_argument("--debug", action="store_true",
                          help="Enable debug mode")
        parser.add_argument("--pdb", action="store_true",
                          help="Drop into PDB on failures")
        parser.add_argument(
    "--capture",
    choices=["fd", "sys", "no", "tee-sys"],
    default="fd",
    help="Capture mode for stdout/stderr (default: fd)"
)
        # Utility options
        parser.add_argument("--install-deps", action="store_true",
                          help="Install test dependencies before running")
        parser.add_argument("--check-deps", action="store_true",
                          help="Check test dependencies")
        parser.add_argument("--list-tests", action="store_true",
                          help="List available tests without running")
        parser.add_argument("--list-markers", action="store_true",
                          help="List available test markers")
        
        return parser.parse_args()
    
    def _get_examples(self):
        """Get example usage strings."""
        return """
Examples:
  python run_tests.py                           # Run all tests
  python run_tests.py --unit --fast            # Run fast unit tests only
  python run_tests.py --security --verbose     # Run security tests with verbose output
  python run_tests.py --coverage --html-report # Run with coverage and HTML report
  python run_tests.py --parallel --workers 8   # Run tests in parallel with 8 workers
  python run_tests.py --keyword "auth"         # Run tests containing 'auth' in name
  python run_tests.py --file test_api_auth.py  # Run specific test file
  python run_tests.py --smoke --critical       # Run smoke and critical tests only
  python run_tests.py --performance --slow     # Run performance tests including slow ones
  
Available Test Markers:
  unit, integration, e2e, security, performance, api, database, 
  auth, business, smoke, regression, critical, fast, slow
        """
    
    def check_dependencies(self):
        """Check if test dependencies are installed."""
        print("🔍 Checking test dependencies...")
        
        try:
            import pytest
            print(f"✅ pytest {pytest.__version__}")
        except ImportError:
            print("❌ pytest not found - run: pip install -r requirements-test.txt")
            return False
        
        optional_deps = [
            ("pytest_cov", "pytest-cov"),
            ("pytest_html", "pytest-html"),
            ("pytest_xdist", "pytest-xdist"),
            ("pytest_mock", "pytest-mock"),
            ("requests", "requests"),
            ("httpx", "httpx")
        ]
        
        missing_deps = []
        for module, package in optional_deps:
            try:
                __import__(module)
                print(f"✅ {package}")
            except ImportError:
                missing_deps.append(package)
                print(f"⚠️  {package} not found (optional)")
        
        if missing_deps:
            print(f"\n📦 Install missing dependencies: pip install {' '.join(missing_deps)}")
        
        return True
    
    def install_dependencies(self):
        """Install test dependencies."""
        print("📦 Installing test dependencies...")
        
        requirements_files = [
            "requirements-test.txt",
            "requirements.txt"
        ]
        
        for req_file in requirements_files:
            if (self.project_root / req_file).exists():
                print(f"Installing from {req_file}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", req_file
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"❌ Failed to install from {req_file}")
                    print(result.stderr)
                    return False
                else:
                    print(f"✅ Installed from {req_file}")
        
        return True
    
    def list_available_tests(self):
        """List all available tests."""
        print("📋 Available Tests:")
        print("=" * 50)
        
        cmd = [sys.executable, "-m", "pytest", "--collect-only", "-q"]
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ Failed to collect tests")
            print(result.stderr)
    
    def list_markers(self):
        """List available test markers."""
        print("🏷️  Available Test Markers:")
        print("=" * 50)
        
        for marker, description in self.test_markers.items():
            print(f"  {marker:12} - {description}")
    
    def build_pytest_command(self, args):
        """Build pytest command based on arguments."""
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add test directory
        cmd.append(str(self.test_dir))
        
        # Test selection
        markers = []
        if args.unit:
            markers.append("unit")
        if args.integration:
            markers.append("integration")
        if args.e2e:
            markers.append("e2e")
        if args.security:
            markers.append("security")
        if args.performance:
            markers.append("performance")
        if args.api:
            markers.append("api")
        if args.database:
            markers.append("database")
        if args.auth:
            markers.append("auth")
        if args.business:
            markers.append("business")
        if args.smoke:
            markers.append("smoke")
        if args.regression:
            markers.append("regression")
        if args.critical:
            markers.append("critical")
        if args.fast:
            markers.append("fast")
        if args.slow:
            markers.append("slow")
        
        if markers:
            cmd.extend(["-m", " or ".join(markers)])
        
        # Verbosity
        if args.verbose:
            cmd.append("-v")
        elif args.quiet:
            cmd.append("-q")
        
        # Parallel execution
        if args.parallel:
            cmd.extend(["-n", str(args.workers)])
        
        # Failure handling
        cmd.extend(["--maxfail", str(args.maxfail)])
        
        # Coverage
        if args.coverage or args.coverage_html or args.coverage_xml:
            cmd.extend(["--cov=backend/app"])
            cmd.extend(["--cov-report=term-missing"])
            
            if args.coverage_html:
                cmd.extend(["--cov-report=html:htmlcov"])
            if args.coverage_xml:
                cmd.extend(["--cov-report=xml:coverage.xml"])
            
            cmd.extend(["--cov-fail-under", str(args.coverage_fail_under)])
        
        # Reports
        if args.json_report:
            report_file = self.reports_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            cmd.extend(["--json-report", f"--json-report-file={report_file}"])
        
        if args.html_report:
            report_file = self.reports_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            cmd.extend(["--html", str(report_file), "--self-contained-html"])
        
        if args.junit_xml:
            report_file = self.reports_dir / f"junit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
            cmd.extend(["--junit-xml", str(report_file)])
        
        # Filters
        if args.keyword:
            cmd.extend(["-k", args.keyword])
        
        if args.file:
            # Replace test directory with specific file
            cmd = cmd[:-1]  # Remove test directory
            cmd.append(str(self.test_dir / args.file))
        
        if args.exclude:
            for pattern in args.exclude:
                cmd.extend(["--ignore-glob", f"*{pattern}*"])
        
        # Debug options
        if args.debug:
            cmd.append("--capture=no")
            cmd.append("--log-cli-level=DEBUG")
        
        if args.pdb:
            cmd.append("--pdb")
        
        cmd.extend(["--capture", args.capture])
        
        return cmd
    
    def set_environment(self, args):
        """Set environment variables for tests."""
        env_vars = {
            "TESTING": "true",
            "TEST_ENV": args.env,
            "PYTEST_CURRENT_TEST": "true"
        }
        
        if args.database_url:
            env_vars["TEST_DATABASE_URL"] = args.database_url
        
        if args.redis_url:
            env_vars["TEST_REDIS_URL"] = args.redis_url
        
        for key, value in env_vars.items():
            os.environ[key] = value
    
    def run_tests(self, cmd):
        """Execute the test command."""
        print("🚀 Running Tests...")
        print("=" * 50)
        print(f"Command: {' '.join(cmd)}")
        print("=" * 50)
        
        start_time = time.time()
        
        # Run the tests
        result = subprocess.run(cmd, cwd=self.project_root)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("=" * 50)
        print(f"⏱️  Total execution time: {duration:.2f} seconds")
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print(f"❌ Tests failed with exit code {result.returncode}")
        
        return result.returncode
    
    def generate_summary_report(self, args, exit_code, duration):
        """Generate a summary report."""
        if not args.report:
            return
        
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "duration": duration,
            "exit_code": exit_code,
            "arguments": vars(args),
            "environment": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": str(self.project_root)
            }
        }
        
        # Save JSON report
        report_file = self.reports_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📊 Summary report saved to: {report_file}")
        
        # Print summary
        print("\n📈 Test Execution Summary:")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Exit Code: {exit_code}")
        print(f"  Status: {'✅ PASSED' if exit_code == 0 else '❌ FAILED'}")
    
    def main(self):
        """Main entry point."""
        args = self.parse_arguments()
        
        # Handle utility commands
        if args.list_markers:
            self.list_markers()
            return 0
        
        if args.list_tests:
            self.list_available_tests()
            return 0
        
        if args.check_deps:
            success = self.check_dependencies()
            return 0 if success else 1
        
        if args.install_deps:
            success = self.install_dependencies()
            return 0 if success else 1
        
        # Check dependencies
        if not self.check_dependencies():
            print("❌ Dependency check failed")
            return 1
        
        # Install dependencies if requested
        if args.install_deps:
            if not self.install_dependencies():
                return 1
        
        # Set environment
        self.set_environment(args)
        
        # Build and execute command
        cmd = self.build_pytest_command(args)
        
        start_time = time.time()
        exit_code = self.run_tests(cmd)
        duration = time.time() - start_time
        
        # Generate reports
        self.generate_summary_report(args, exit_code, duration)
        
        return exit_code

if __name__ == "__main__":
    runner = TestRunner()
    exit_code = runner.main()
    sys.exit(exit_code)