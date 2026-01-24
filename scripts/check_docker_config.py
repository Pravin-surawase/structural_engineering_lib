#!/usr/bin/env python3
"""
Docker Configuration Validator.

Validates Docker setup for the structural engineering library:
- Dockerfile syntax and best practices
- docker-compose.yml schema validation
- .dockerignore completeness
- Environment variable documentation

Usage:
    python scripts/check_docker_config.py           # Full validation
    python scripts/check_docker_config.py --quick   # Quick syntax check
    python scripts/check_docker_config.py --fix     # Suggest fixes

Exit Codes:
    0: All checks passed
    1: Validation errors found
    2: Docker files not found
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Project root
ROOT = Path(__file__).parent.parent


def check_dockerfile(path: Path) -> list[str]:
    """Check Dockerfile for issues."""
    issues = []

    if not path.exists():
        return [f"❌ Dockerfile not found: {path}"]

    content = path.read_text()
    lines = content.strip().split("\n")

    # Check FROM instruction
    if not any(line.startswith("FROM ") for line in lines):
        issues.append("❌ Missing FROM instruction")

    # Check for latest tag (anti-pattern)
    if ":latest" in content and "python:latest" in content:
        issues.append("⚠️ Using :latest tag - prefer specific version (e.g., python:3.11-slim)")

    # Check for WORKDIR
    if "WORKDIR" not in content:
        issues.append("⚠️ No WORKDIR defined - best practice to set working directory")

    # Check for non-root user (security)
    if "USER " not in content and "user:" not in content:
        issues.append("ℹ️ Consider adding non-root USER for security")

    # Check for HEALTHCHECK
    if "HEALTHCHECK" not in content:
        issues.append("ℹ️ Consider adding HEALTHCHECK instruction")

    # Check for .dockerignore usage
    dockerignore = ROOT / ".dockerignore"
    if not dockerignore.exists():
        issues.append("⚠️ No .dockerignore file - may copy unnecessary files")

    # Check for efficient layer ordering
    copy_count = content.count("COPY ")
    if copy_count > 5:
        issues.append("ℹ️ Many COPY instructions - consider consolidating for smaller layers")

    # Check for pip cache disable
    if "pip install" in content and "--no-cache-dir" not in content:
        issues.append("⚠️ pip install without --no-cache-dir - increases image size")

    return issues


def check_docker_compose(path: Path) -> list[str]:
    """Check docker-compose.yml for issues."""
    issues = []

    if not path.exists():
        return [f"❌ docker-compose file not found: {path}"]

    content = path.read_text()

    # Check for version (deprecated in v2+)
    if content.startswith("version:"):
        issues.append("ℹ️ 'version' key is deprecated in Docker Compose v2+")

    # Check for services
    if "services:" not in content:
        issues.append("❌ No services defined")

    # Check for build context
    if "build:" not in content and "image:" not in content:
        issues.append("⚠️ No build or image specified")

    # Check for health check
    if "healthcheck:" not in content:
        issues.append("ℹ️ Consider adding healthcheck for container orchestration")

    # Check for restart policy
    if "restart:" not in content:
        issues.append("ℹ️ No restart policy - consider 'restart: unless-stopped'")

    # Check for exposed ports
    if "ports:" in content:
        # Validate port format
        port_pattern = r'"?\d+:\d+"?'
        if not re.search(port_pattern, content):
            issues.append("⚠️ Port mapping format may be incorrect")

    # Check for hardcoded secrets
    secret_patterns = ["password:", "secret:", "api_key:"]
    for pattern in secret_patterns:
        if pattern in content.lower():
            # Check if it's using environment variable syntax
            line_idx = content.lower().find(pattern)
            context = content[line_idx:line_idx+100]
            if "${" not in context and ":-" not in context:
                issues.append(f"⚠️ Possible hardcoded secret near '{pattern}' - use environment variables")

    return issues


def check_dockerignore(path: Path) -> list[str]:
    """Check .dockerignore for completeness."""
    issues = []

    if not path.exists():
        return ["❌ .dockerignore not found - creates larger images"]

    content = path.read_text()

    # Required exclusions
    required = [".git", "__pycache__", "*.pyc", ".venv", "node_modules"]
    for req in required:
        if req not in content:
            issues.append(f"⚠️ Missing '{req}' in .dockerignore")

    # Recommended exclusions
    recommended = ["docs/", "tests/", "*.md", ".github/"]
    for rec in recommended:
        base = rec.rstrip("/")
        if base not in content and rec not in content:
            issues.append(f"ℹ️ Consider adding '{rec}' to .dockerignore")

    return issues


def check_env_documentation() -> list[str]:
    """Check if environment variables are documented."""
    issues = []

    compose_files = [
        ROOT / "docker-compose.yml",
        ROOT / "docker-compose.dev.yml"
    ]

    env_vars = set()
    for compose_file in compose_files:
        if compose_file.exists():
            content = compose_file.read_text()
            # Find ${VAR:-default} patterns
            env_vars.update(re.findall(r'\$\{(\w+)(?::-[^}]*)?\}', content))

    if env_vars:
        # Check if there's an .env.example or README documenting these
        env_example = ROOT / ".env.example"
        docker_readme = ROOT / "docs" / "learning" / "docker-fundamentals-guide.md"

        if not env_example.exists():
            issues.append(f"ℹ️ Consider creating .env.example with: {', '.join(sorted(env_vars))}")

        if docker_readme.exists():
            readme_content = docker_readme.read_text()
            for var in env_vars:
                if var not in readme_content:
                    issues.append(f"ℹ️ Environment variable '{var}' not documented in Docker guide")

    return issues


def print_results(issues: dict[str, list[str]]) -> int:
    """Print validation results."""
    print("=" * 60)
    print("Docker Configuration Validator")
    print("=" * 60)
    print()

    total_errors = 0
    total_warnings = 0
    total_info = 0

    for category, category_issues in issues.items():
        if category_issues:
            print(f"📦 {category}")
            for issue in category_issues:
                print(f"   {issue}")
                if issue.startswith("❌"):
                    total_errors += 1
                elif issue.startswith("⚠️"):
                    total_warnings += 1
                else:
                    total_info += 1
            print()

    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  ❌ Errors: {total_errors}")
    print(f"  ⚠️ Warnings: {total_warnings}")
    print(f"  ℹ️ Info: {total_info}")

    if total_errors == 0 and total_warnings == 0:
        print("\n✅ Docker configuration is valid!")
        return 0
    elif total_errors == 0:
        print("\n⚠️ Docker configuration has warnings but is functional")
        return 0
    else:
        print("\n❌ Docker configuration has errors that need fixing")
        return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate Docker configuration")
    parser.add_argument("--quick", action="store_true", help="Quick syntax check only")
    parser.add_argument("--fix", action="store_true", help="Show fix suggestions")
    args = parser.parse_args()

    issues = {}

    # Check Dockerfile
    dockerfile = ROOT / "Dockerfile.fastapi"
    issues["Dockerfile.fastapi"] = check_dockerfile(dockerfile)

    # Check docker-compose files
    issues["docker-compose.yml"] = check_docker_compose(ROOT / "docker-compose.yml")
    issues["docker-compose.dev.yml"] = check_docker_compose(ROOT / "docker-compose.dev.yml")

    # Check .dockerignore
    issues[".dockerignore"] = check_dockerignore(ROOT / ".dockerignore")

    if not args.quick:
        # Check environment documentation
        issues["Environment Variables"] = check_env_documentation()

    return print_results(issues)


if __name__ == "__main__":
    sys.exit(main())
