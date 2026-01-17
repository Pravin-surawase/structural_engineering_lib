# Security Best Practices - Part 2/2

**(Continued from part1.md)**

## 5. Data Privacy & Confidentiality

### 5.1 Data Privacy Principles

**Principle 1: No Data Collection**

The library should NOT:
- ❌ Send telemetry data to external servers
- ❌ Track usage analytics
- ❌ Phone home with design data
- ❌ Store user credentials

**Why:** Design data is confidential. Engineers' project data must stay local.

**Implementation:**
```python
# ❌ BAD - Sends data to external server
def design_beam(beam_data: dict) -> BeamDesignResult:
    # Track usage
    requests.post('https://api.company.com/analytics', json=beam_data)

    # Design logic
    result = calculate_design(beam_data)
    return result

# ✅ GOOD - Pure local computation
def design_beam(beam_data: dict) -> BeamDesignResult:
    # No external calls
    # No data collection
    result = calculate_design(beam_data)
    return result
```

### 5.2 Sensitive Data Handling

**If library must handle sensitive data:**

**Pattern 1: Memory Clearing**
```python
import gc

def process_confidential_design(design_data: dict):
    """Process confidential data with memory cleanup."""
    try:
        result = calculate_design(design_data)
        return result
    finally:
        # Clear sensitive data from memory
        design_data.clear()
        gc.collect()
```

**Pattern 2: File Encryption (if saving locally)**
```python
from cryptography.fernet import Fernet

def save_design(design_data: dict, file_path: str, key: bytes):
    """Save design with encryption."""
    import json

    # Serialize
    json_data = json.dumps(design_data)

    # Encrypt
    f = Fernet(key)
    encrypted = f.encrypt(json_data.encode())

    # Save
    with open(file_path, 'wb') as f:
        f.write(encrypted)

def load_design(file_path: str, key: bytes) -> dict:
    """Load encrypted design."""
    with open(file_path, 'rb') as f:
        encrypted = f.read()

    # Decrypt
    f = Fernet(key)
    decrypted = f.decrypt(encrypted)

    # Deserialize
    import json
    return json.loads(decrypted.decode())
```

### 5.3 Logging Security

**Risk:** Logs may contain sensitive data.

**Secure Logging Pattern:**
```python
import logging

def design_beam(beam_data: dict) -> BeamDesignResult:
    # ❌ BAD - Logs full design data
    logging.info(f"Designing beam: {beam_data}")

    # ✅ GOOD - Logs only metadata
    logging.info(f"Designing beam: span={beam_data['span_mm']}mm")

    # ✅ BETTER - Redact sensitive info
    safe_data = {k: v for k, v in beam_data.items()
                 if k not in ['project_name', 'client_id']}
    logging.debug(f"Design parameters: {safe_data}")

    result = calculate_design(beam_data)
    return result
```

---

## 6. Supply Chain Security

### 6.1 GitHub Actions Security

**Secure CI/CD Workflow:**

**.github/workflows/ci.yml:**
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    # Pin runner OS version
    container:
      image: python:3.11-slim

    permissions:
      contents: read  # Minimal permissions

    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false  # Don't persist GitHub token

      - name: Install dependencies
        run: |
          # Use specific versions, not 'latest'
          pip install --no-cache-dir -r requirements-dev.txt

      - name: Run security scan
        run: pip-audit

      - name: Run tests
        run: pytest
```

**Security Best Practices:**
- ✅ Pin action versions (`@v4` not `@main`)
- ✅ Minimal permissions
- ✅ Don't persist credentials
- ✅ Use specific container versions

### 6.2 Secrets Management

**Never commit secrets:**

**.gitignore:**
```
# Secrets
*.key
*.pem
secrets.json
.env

# Credentials
credentials.txt
api_keys.txt
```

**Use Environment Variables:**
```python
import os

# ✅ GOOD - From environment
API_KEY = os.environ.get('STRUCTURAL_LIB_API_KEY')

# ❌ BAD - Hardcoded
API_KEY = "sk-1234abcd5678efgh"
```

**GitHub Secrets:**
```yaml
# .github/workflows/release.yml
- name: Publish to PyPI
  env:
    PYPI_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
  run: |
    twine upload dist/*
```

### 6.3 Vulnerability Disclosure

**Create SECURITY.md:**

```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.15.x  | :white_check_mark: |
| < 0.15  | :x:                |

## Reporting a Vulnerability

**DO NOT** open public issues for security vulnerabilities.

Instead:
1. Email: security@structural-lib.example.com
2. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
3. Allow 48 hours for response

## Security Response Process

1. Acknowledgment within 48 hours
2. Investigation & fix development (1-2 weeks)
3. Private security advisory on GitHub
4. Coordinated disclosure after fix released
5. Credit to reporter (if desired)

## Security Updates

Subscribe to security advisories:
https://github.com/owner/structural_lib/security/advisories
```

---

## 7. Security Testing

### 7.1 Static Analysis Security Testing (SAST)

**Tool: Bandit** (Python security linter)

```bash
# Install
pip install bandit

# Scan code
bandit -r structural_lib/

# Example findings:
# [B307] Use of potentially unsafe marshal.loads
# [B608] Possible SQL injection
```

**CI Integration:**
```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  bandit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
      - name: Install bandit
        run: pip install bandit
      - name: Run bandit
        run: bandit -r structural_lib/ -f json -o bandit-report.json
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: bandit-report
          path: bandit-report.json
```

### 7.2 Dependency Vulnerability Scanning

**Tool: pip-audit in CI:**

```yaml
# .github/workflows/security.yml
jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run pip-audit
        run: |
          pip install pip-audit
          pip-audit --desc
```

### 7.3 Fuzz Testing

**Goal:** Find edge cases that cause crashes or incorrect behavior.

**Tool: Hypothesis** (property-based testing with fuzzing)

```python
from hypothesis import given, strategies as st
import pytest

@given(
    span_mm=st.floats(min_value=-1e10, max_value=1e10),
    width_mm=st.floats(min_value=-1e10, max_value=1e10),
)
def test_design_beam_never_crashes(span_mm, width_mm):
    """
    Fuzz test: design_beam should never crash.
    May raise ValueError for invalid input, but never crash.
    """
    try:
        result = design_beam(span_mm=span_mm, width_mm=width_mm)
        # If succeeds, result must be valid
        assert result.ast_mm2 >= 0
    except ValueError:
        # Invalid input is acceptable
        pass
    except Exception as e:
        # Any other exception is a bug
        pytest.fail(f"Unexpected exception: {e}")
```

---

## 8. Implementation Roadmap

### 8.1 Phase 1: Input Validation (Week 1) - 4-6 hours

**Deliverables:**
- [ ] Add range validation to all numeric inputs
- [ ] Add overflow protection (max 1e15)
- [ ] Add cross-parameter validation
- [ ] Add NaN/Inf checks
- [ ] Write tests for edge cases

**Success Criteria:**
- All inputs validated at boundary
- Overflow protected
- Clear error messages

### 8.2 Phase 2: Dependency Security (Week 1) - 2-3 hours

**Deliverables:**
- [ ] Run pip-audit on current dependencies
- [ ] Fix all HIGH/CRITICAL vulnerabilities
- [ ] Set up Dependabot
- [ ] Add pip-audit to CI
- [ ] Document dependency policy

**Success Criteria:**
- Zero HIGH/CRITICAL vulnerabilities
- Automated weekly scans
- Dependabot PRs enabled

### 8.3 Phase 3: Code Signing (Week 2) - 3-4 hours

**Deliverables:**
- [ ] Set up GPG key for signing
- [ ] Sign Git tags
- [ ] Generate checksums for releases
- [ ] Document verification process
- [ ] Update release workflow

**Success Criteria:**
- All releases signed
- Checksums published
- Users can verify authenticity

### 8.4 Phase 4: Security Documentation (Week 2) - 2-3 hours

**Deliverables:**
- [ ] Create SECURITY.md
- [ ] Document security policy
- [ ] Set up security contact email
- [ ] Add security section to README
- [ ] Document vulnerability disclosure process

**Success Criteria:**
- SECURITY.md published
- Contact email active
- Process documented

---

## 9. Security Checklist

### 9.1 Pre-Release Security Review

**Before v1.0 release, verify:**

**Input Validation:**
- [ ] All numeric inputs have range checks
- [ ] Overflow protection implemented
- [ ] String inputs use Literal types or whitelist
- [ ] File paths validated (no directory traversal)
- [ ] Cross-parameter validation exists

**Dependencies:**
- [ ] pip-audit shows zero vulnerabilities
- [ ] All dependencies pinned (major.minor)
- [ ] Dependabot enabled
- [ ] No unnecessary dependencies

**Code Security:**
- [ ] No eval/exec on user input
- [ ] No subprocess with user input
- [ ] Bandit scan passes
- [ ] No hardcoded secrets

**Distribution:**
- [ ] Releases built in CI
- [ ] Git tags signed
- [ ] Checksums published
- [ ] PyPI 2FA enabled

**Documentation:**
- [ ] SECURITY.md exists
- [ ] Vulnerability disclosure process documented
- [ ] Security contact published
- [ ] Dependencies documented

**Testing:**
- [ ] Fuzz tests for public APIs
- [ ] Security test cases
- [ ] Input validation tested

---

## 10. Cost-Benefit Analysis

### 10.1 Implementation Cost

| Phase | Effort | Timeline |
|-------|--------|----------|
| Input Validation | 4-6 hours | Week 1 |
| Dependency Security | 2-3 hours | Week 1 |
| Code Signing | 3-4 hours | Week 2 |
| Documentation | 2-3 hours | Week 2 |
| **Total** | **11-16 hours** | **2 weeks** |

### 10.2 Ongoing Maintenance

- Dependency updates: 1 hour/month (automated)
- Security advisories response: 2-4 hours/incident (rare)
- **Total:** ~15 hours/year

### 10.3 Benefits

**Risk Reduction:**
- Prevent calculation errors from malicious input
- Protect against supply chain attacks
- Reduce legal liability

**Professional Confidence:**
- Engineers trust library security
- Suitable for professional use
- Meets industry standards

**ROI:**
- **Break-even:** Preventing 1 serious security incident
- **Long-term:** Trust = adoption = success

---

## 11. Recommendations

### 11.1 Immediate Actions (Before v1.0)

**Priority 1: Input Validation** (4 hours)
- Add range checks to all functions
- Add overflow protection
- Test edge cases
- **Why:** Prevents incorrect calculations

**Priority 2: Dependency Scan** (1 hour)
- Run pip-audit
- Fix HIGH/CRITICAL issues
- **Why:** Zero known vulnerabilities

### 11.2 Medium-Term (v1.0 Release)

**Priority 3: Code Signing** (3 hours)
- Sign releases
- Publish checksums
- **Why:** Authenticity verification

**Priority 4: SECURITY.md** (1 hour)
- Document security policy
- Set up contact email
- **Why:** Professional disclosure process

### 11.3 Long-Term

**Continuous Monitoring:**
- Weekly Dependabot scans
- Monthly security review
- Annual penetration testing (if budget allows)

---

## 12. Security Resources

### 12.1 Tools

**Scanning:**
- pip-audit: https://pypi.org/project/pip-audit/
- Bandit: https://bandit.readthedocs.io/
- Safety: https://pyup.io/safety/

**Testing:**
- Hypothesis: https://hypothesis.readthedocs.io/
- pytest-security: Custom security tests

**Monitoring:**
- Dependabot: GitHub built-in
- Snyk: https://snyk.io/
- GitHub Security Advisories

### 12.2 References

**Python Security:**
- OWASP Python Security: https://owasp.org/www-project-python-security/
- PyPA Security: https://packaging.python.org/guides/security/
- Python CVE Database: https://cve.mitre.org/

**Engineering Software:**
- NIST Cybersecurity Framework
- ISO 27001 (if needed)

---

## Document Control

**Version History:**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-07 | Initial research complete (parts 1-2) | Research Team |

**Next Steps:**

1. Review security findings with team
2. Prioritize implementation (input validation first)
3. Create security implementation tasks
4. Run pip-audit before v1.0
5. Complete pre-release security checklist

---

**End of Document**
**Total Length:** Parts 1-2 combined ≈ 1000 lines
**Implementation Estimate:** 11-16 hours (2 weeks)
**Priority:** HIGH (required before v1.0 public release)
