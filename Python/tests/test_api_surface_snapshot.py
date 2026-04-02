"""Snapshot regression tests — assert minimum API surface counts.

These tests fail if scripts, agents, endpoints, or tests are accidentally removed.
Update thresholds ONLY when intentionally removing items (with PR approval).
"""

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # Python/tests/ → repo root


class TestAutomationMapSurface:
    """Ensure automation-map.json doesn't lose scripts."""

    def test_minimum_script_count(self):
        path = REPO_ROOT / "scripts" / "automation-map.json"
        assert path.exists(), "automation-map.json missing"
        data = json.loads(path.read_text())
        tasks = data.get("tasks", {})
        assert len(tasks) >= 85, f"Expected ≥85 tasks, got {len(tasks)}"

    def test_all_scripts_have_group(self):
        path = REPO_ROOT / "scripts" / "automation-map.json"
        data = json.loads(path.read_text())
        for name, task in data.get("tasks", {}).items():
            assert "group" in task, f"Task '{name}' missing group field"


class TestAgentRegistrySurface:
    """Ensure agent_registry.json doesn't lose agents."""

    def test_minimum_agent_count(self):
        path = REPO_ROOT / "agents" / "agent_registry.json"
        assert path.exists(), "agent_registry.json missing"
        data = json.loads(path.read_text())
        agents = data.get("agents", [])
        assert len(agents) >= 15, f"Expected ≥15 agents, got {len(agents)}"

    def test_required_agent_fields(self):
        path = REPO_ROOT / "agents" / "agent_registry.json"
        data = json.loads(path.read_text())
        required = {
            "name",
            "description",
            "tools",
            "permission_level",
            "skills",
            "keywords",
        }
        for agent in data.get("agents", []):
            missing = required - set(agent.keys())
            assert (
                not missing
            ), f"Agent {agent.get('name', '?')} missing fields: {missing}"

    def test_known_agents_present(self):
        path = REPO_ROOT / "agents" / "agent_registry.json"
        data = json.loads(path.read_text())
        names = {a["name"] for a in data.get("agents", [])}
        expected = {
            "orchestrator",
            "backend",
            "frontend",
            "tester",
            "reviewer",
            "ops",
            "doc-master",
        }
        missing = expected - names
        assert not missing, f"Missing expected agents: {missing}"


class TestOpenAPIBaselineSurface:
    """Ensure OpenAPI baseline doesn't lose endpoints."""

    def test_baseline_exists(self):
        path = REPO_ROOT / "fastapi_app" / "openapi_baseline.json"
        assert path.exists(), "openapi_baseline.json missing"

    def test_minimum_endpoint_count(self):
        path = REPO_ROOT / "fastapi_app" / "openapi_baseline.json"
        if not path.exists():
            pytest.skip("openapi_baseline.json not found")
        data = json.loads(path.read_text())
        paths = data.get("paths", {})
        endpoint_count = sum(len(methods) for methods in paths.values())
        assert endpoint_count >= 30, f"Expected ≥30 endpoints, got {endpoint_count}"


class TestPythonTestSurface:
    """Ensure test count doesn't decrease."""

    def test_minimum_test_file_count(self):
        test_dir = REPO_ROOT / "Python" / "tests"
        assert test_dir.exists(), "Python/tests/ missing"
        test_files = list(test_dir.glob("test_*.py"))
        assert len(test_files) >= 10, f"Expected ≥10 test files, got {len(test_files)}"

    def test_stats_file_exists(self):
        path = REPO_ROOT / "Python" / "test_stats.json"
        if path.exists():
            data = json.loads(path.read_text())
            total = data.get("total", 0)
            assert total >= 50, f"Expected ≥50 total tests in stats, got {total}"


class TestAgentMDFilesSurface:
    """Ensure all 15 agent .md files exist."""

    def test_all_agent_files_exist(self):
        agents_dir = REPO_ROOT / ".github" / "agents"
        assert agents_dir.exists(), ".github/agents/ missing"
        agent_files = list(agents_dir.glob("*.agent.md"))
        assert (
            len(agent_files) >= 15
        ), f"Expected ≥15 agent files, got {len(agent_files)}"
