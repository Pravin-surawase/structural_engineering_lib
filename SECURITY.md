# Security Policy

**Version:** 0.16.5
**Last Updated:** 2026-01-11
**Status:** Active

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.16.x  | ✅ Active support  |
| 0.15.x  | ⚠️ Security fixes only |
| < 0.15  | ❌ Not supported   |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

1. **Do NOT** open a public GitHub issue for security vulnerabilities
2. **Email:** Contact the maintainers privately (see AUTHORS.md)
3. **Include:**
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We aim to respond within 48 hours and will keep you updated on the fix progress.

## Security Measures

### Dependency Management

- **Dependabot:** Automated weekly dependency updates
- **pip-audit:** Daily vulnerability scanning in CI
- **Safety:** Additional vulnerability database checks
- **SBOM:** Software Bill of Materials generated for each release

### Static Analysis

- **CodeQL:** Weekly deep security analysis
- **Bandit:** Python-specific security linting
- **Ruff:** Code quality and potential security issues

### Input Validation

This library includes comprehensive input validation:

- All user inputs are validated before processing
- Type checking via mypy with strict mode
- Range validation for engineering parameters
- Material grade verification against IS 456 standards

See `scripts/audit_input_validation.py` for validation coverage reports.

### Supply Chain Security

- All dependencies are from PyPI with verified signatures
- GitHub Actions use pinned versions
- SBOM available in releases for supply chain transparency

## Security Best Practices for Users

### 1. Keep Updated

Always use the latest version to benefit from security patches:

```bash
pip install --upgrade structural-lib-is456
```

### 2. Verify Inputs

Even with library validation, verify your inputs:

- Check data sources for integrity
- Validate dimensions are within expected ranges
- Cross-check material properties

### 3. Review Outputs

As stated in LICENSE_ENGINEERING.md:

- All outputs require independent verification
- Software output is not a substitute for professional review
- Licensed engineers must validate all designs

### 4. Environment Security

- Use virtual environments
- Keep Python and dependencies updated
- Review dependencies before installation

## Audit Reports

Security scan reports are available as CI artifacts:

- **pip-audit-report.md:** Dependency vulnerabilities
- **bandit-report.txt:** Static analysis findings
- **sbom.json:** Complete dependency inventory

## Changelog

| Date | Change |
|------|--------|
| 2026-01-11 | Initial security policy (TASK-274) |

---

For general security questions, open a GitHub Discussion.
