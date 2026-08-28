# Security Policy

## Supported versions

StructLib is an Alpha project. Security fixes are prepared on the current
`main` branch and, when separately authorized, published in a new immutable
version. Older tags and prereleases are not rebuilt or silently replaced.

| Version | Security status |
|---|---|
| Current `main` | Receives security fixes and required checks |
| `0.24.0a1` | Immutable public Alpha; evaluate with its exact published evidence |
| Earlier versions | No routine security updates |

This policy is not a stable-API promise, a release authorization, or an
engineering-use approval.

## Report a vulnerability privately

Use GitHub's private vulnerability-reporting flow for this repository:

1. Open the repository's **Security** tab.
2. Choose **Advisories** and **Report a vulnerability**.
3. Include the affected version or commit, package origin, reproduction steps,
   impact, and any proposed mitigation.

Do not disclose an unpatched vulnerability in a public issue. If private
reporting is unavailable, open a public issue containing no exploit details and
ask the maintainer to enable a private channel.

No response or remediation time is promised. The maintainer will validate the
report, preserve attribution when requested, and publish only through the
normal reviewed release process.

## Engineering-result concerns

A suspected formula, unit, applicability, validation, or result defect may be
safety-critical without being a software-security vulnerability. Report it
with exact inputs, library identity, observed output, expected engineering
outcome, and source/evidence basis. Do not submit protected standard prose or
images.

Software checks and security handling do not confer professional approval.
Every structural result remains subject to independent verification and review
by a qualified structural engineer before engineering or construction use.
