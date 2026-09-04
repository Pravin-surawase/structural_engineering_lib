---
owner: Main Agent
status: active
last_updated: 2026-09-04
doc_type: reference
phase_id: PF9
---

# PF9 runtime and delivery research source

**Audience:** library/product owners and implementers. **Decision date:**
2026-09-04. **Scope:** runtime, host, package and deployment choices for native
Python/.NET structural libraries and the Windows Excel/ETABS product. Formula
correctness, product pricing and implementation are outside this research.

## Direct decision

Use CPython 3.11–3.14 for the compatibility period, .NET 10 LTS for the new
.NET libraries and managed Windows add-in, Excel-DNA 1.9.0, Windows 11 x64 and
64-bit Microsoft 365 Excel as the primary product target. Certify ETABS
23.3.1.4563/API 2.16.0.0 first because it is both installed and already bound to
repository evidence. Every release candidate still needs the PF8 installed
acceptance; this research does not turn the target matrix into a passed host.

## Evidence and implications

Microsoft lists .NET 10 as active LTS through 14 November 2028 and requires
supported installations to stay current on patches. The repository already
pins SDK 10.0.400 and the machine currently has runtime 10.0.11, so the first
implementation can retain the established target while separating SDK pinning
from current runtime servicing. [Official .NET support policy](https://dotnet.microsoft.com/en-us/platform/support/policy).

Excel-DNA 1.9 explicitly supports `net10.0-windows`, but it requires the
matching .NET Desktop Runtime and states that only one .NET/CoreCLR major
runtime can load in an Excel process. This makes .NET 10 suitable for the
controlled upcoming project, with an installer preflight for runtime and other
add-ins. It is not evidence of universal compatibility on arbitrary customer
machines. The first release remains managed and framework-dependent; NativeAOT
or a .NET Framework adapter needs a separate compatibility packet.
[Excel-DNA .NET runtime support](https://excel-dna.net/docs/guides-basic/dotnet-runtime-support/),
[Excel-DNA 1.9 release notes](https://excel-dna.net/docs/release-notes-1-9/).

Microsoft installs 64-bit Microsoft 365 by default and recommends it for large
data and add-in workloads. Office and add-in bitness must match. Microsoft also
shows Microsoft 365 Apps and Office LTSC 2024 supported on Windows 11, while
Windows 10 passed general support and Office LTSC 2021 ends support in October
2026. Therefore Windows 11 plus 64-bit Microsoft 365 Excel is primary; Office
LTSC 2024 x64 is a secondary target only after its own installed acceptance.
[Choose 64- or 32-bit Office](https://support.microsoft.com/en-us/office/lifecycle/officeinstall/choose-between-the-64-bit-or-32-bit-version-of-office),
[Office/Windows support matrix](https://learn.microsoft.com/en-us/lifecycle/office-windows-configuration-matrix).

CSI lists ETABS 23.3.0/23.3.1 as released on 2 July 2026 and explicitly adds
.NET 10 COM-client support. The current machine/repository evidence identifies
ETABS 23.3.1.4563 and API assembly 2.16.0.0. The first adapter claim is limited
to that exact tested product/API/runtime tuple; other ETABS versions may still
exchange the portable snapshot but require a new signature and E5 acceptance
packet before live support. [CSI ETABS enhancements](https://www.csiamerica.com/products/etabs/enhancements).

Python 3.14 is a stable bugfix branch, 3.13 is also in bugfix support, and 3.12
and 3.11 receive security fixes through October 2028 and October 2027
respectively. The existing package advertises 3.11–3.13. Adding 3.14 to the
target requires the full release matrix; until that passes, it remains a PF9
target rather than a current package claim. [Python version status](https://devguide.python.org/versions/).

CSI's current product requirements specify 64-bit Windows 10/11 and at least
16 GB RAM, with 64 GB recommended for large analysis work. Since the product
target is Windows 11 and this library does not change ETABS solver speed, ETABS
benchmarks must report model size and machine resources separately from library
and workbook time. [ETABS system requirements](https://www.csiamerica.com/products/etabs/system-requirements).

## Claim-to-source ledger

| Claim | Source | Publisher | Accessed | Confidence / limitation |
| --- | --- | --- | --- | --- |
| .NET 10 active LTS through 2028-11-14 | Official .NET support policy | Microsoft | 2026-09-04 | High; patch level changes monthly |
| Excel-DNA 1.9 supports .NET 10 and needs matching Desktop Runtime | Runtime guide and 1.9 notes | Excel-DNA | 2026-09-04 | High; documents single-CoreCLR conflict risk |
| 64-bit Microsoft 365 is default and suitable for large/add-in workloads | Office bitness guide | Microsoft | 2026-09-04 | High; does not validate this XLL |
| Windows 11/M365 and LTSC 2024 are supported configurations | Office/Windows matrix | Microsoft | 2026-09-04 | High; Modern Lifecycle requires currency |
| ETABS 23.3 adds .NET 10 COM support | ETABS enhancement record | CSI | 2026-09-04 | High; live methods still need exact E5 evidence |
| Python 3.11–3.14 lifecycle states | Python version status | Python core project | 2026-09-04 | High; package dependencies still need matrix tests |
| ETABS hardware/OS requirements | ETABS system requirements | CSI | 2026-09-04 | High; product performance remains model-dependent |

The research stopped after the official sources resolved every runtime and host
decision and the local manifests/evidence fixed the exact candidate versions.
No additional source was likely to change the first controlled target. The
remaining uncertainty is empirical installed-host compatibility and performance,
which PF8/PF9 deliberately require from the implementation candidate.
