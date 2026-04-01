#!/usr/bin/env python3
"""Temporary script to add group fields to automation-map.json. Delete after use."""

import json
from collections import OrderedDict

GROUP_MAP = {
    # Session
    "start session": "Session",
    "end session": "Session",
    "session summary": "Session",
    "sync doc numbers": "Session",
    "session handoff": "Session",
    "session check": "Session",
    "agent brief": "Session",
    "agent context": "Session",
    "preflight checks": "Session",
    # Quality
    "run all checks": "Quality",
    "check folder structure": "Quality",
    "check governance": "Quality",
    "validate imports": "Quality",
    "validate api contracts": "Quality",
    "check architecture boundaries": "Quality",
    "check circular imports": "Quality",
    "check fastapi issues": "Quality",
    "check type annotations": "Quality",
    "check doc versions": "Quality",
    "check bootstrap freshness": "Quality",
    "check instruction drift": "Quality",
    "check tasks format": "Quality",
    "check python version": "Quality",
    "check version consistency": "Quality",
    "check wip limits": "Quality",
    "check repo hygiene": "Quality",
    "check cli reference": "Quality",
    "check scripts index": "Quality",
    "check api compat": "Quality",
    "check openapi drift": "Quality",
    "validate schema snapshots": "Quality",
    "check next session brief": "Quality",
    "check root file count": "Quality",
    "governance health score": "Quality",
    "validate script references": "Quality",
    "audit error handling": "Quality",
    "audit input validation": "Quality",
    "validate streamlit session state": "Quality",
    # Git
    "commit code": "Git",
    "push code": "Git",
    "check git state": "Git",
    "recover git": "Git",
    "decide pr vs direct": "Git",
    "create pr branch": "Git",
    "finish pr": "Git",
    "pre commit check": "Git",
    "local ci": "Git",
    "install git hooks": "Git",
    "check merge state": "Git",
    "check branch safety": "Git",
    # Discovery
    "check api signatures": "Discovery",
    "discover api function": "Discovery",
    "find automation": "Discovery",
    "generate api manifest": "Discovery",
    # Docs
    "move file": "Docs",
    "delete file": "Docs",
    "create document": "Docs",
    "fix broken links": "Docs",
    "fix deleted file links": "Docs",
    "check docs": "Docs",
    "archive old files": "Docs",
    # Generation
    "generate folder index": "Generation",
    "generate all indexes": "Generation",
    "generate docs index": "Generation",
    "generate client sdks": "Generation",
    "generate error docs": "Generation",
    "generate audit report": "Generation",
    # Governance
    "agent compliance check": "Governance",
    "agent drift detection": "Governance",
    "agent scoring": "Governance",
    "agent session collect": "Governance",
    "agent feedback": "Governance",
    "agent mistakes report": "Governance",
    "repo health check": "Governance",
    "project health": "Governance",
    # Evolution
    "self evolve": "Evolution",
    "agent evolve instructions": "Evolution",
    "agent trends": "Evolution",
    # Migration
    "migrate python module": "Migration",
    "migrate react component": "Migration",
    "batch migration": "Migration",
    # Release
    "bump version": "Release",
    "release": "Release",
    # Testing
    "run tests": "Testing",
    "watch tests": "Testing",
    "benchmark api": "Testing",
    "test api parity": "Testing",
    "test import 3d pipeline": "Testing",
    "test import pipeline": "Testing",
    "test sample endpoint": "Testing",
    "test vba adapter": "Testing",
    "external cli test": "Testing",
    "create test scaffold": "Testing",
    "update test stats": "Testing",
    "test changed files": "Testing",
    # Infrastructure
    "check docker config": "Infrastructure",
    "launch dev stack": "Infrastructure",
    "format code": "Infrastructure",
    "render dxf": "Infrastructure",
    "cleanup stale branches": "Infrastructure",
    "collect diagnostics": "Infrastructure",
    "collect metrics": "Infrastructure",
    "export paper data": "Infrastructure",
    "check streamlit code": "Infrastructure",
}

with open("scripts/automation-map.json", "r") as f:
    raw = f.read()

data = json.loads(raw, object_pairs_hook=OrderedDict)

tasks = data["tasks"]
assigned = 0
unassigned = []

new_tasks = OrderedDict()
for task_name, task_info in tasks.items():
    group = GROUP_MAP.get(task_name)
    if group:
        new_info = OrderedDict()
        new_info["group"] = group
        for k, v in task_info.items():
            if k != "group":
                new_info[k] = v
        new_tasks[task_name] = new_info
        assigned += 1
    else:
        unassigned.append(task_name)
        new_tasks[task_name] = task_info

data["tasks"] = new_tasks

with open("scripts/automation-map.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"Assigned groups to {assigned}/{len(tasks)} tasks")
if unassigned:
    print(f"UNASSIGNED: {unassigned}")
else:
    print("All tasks assigned!")

# Summary by group
from collections import Counter

counts = Counter(GROUP_MAP.values())
for g, c in sorted(counts.items()):
    print(f"  {g}: {c} tasks")
