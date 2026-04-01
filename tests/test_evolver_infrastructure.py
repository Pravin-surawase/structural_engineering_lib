"""Tests for evolver infrastructure scripts (TASK-800).

Covers 6 modules:
  - scripts/_lib/scoring.py — composite_score, grade, dimension weights
  - scripts/_lib/agent_registry.py — discover_agents, parse_frontmatter, is_safety_critical
  - scripts/_lib/agent_data.py — save/load session, scorecard, pending evolutions
  - scripts/agent_scorer.py — auto_score_agent, validate_score
  - scripts/agent_drift_detector.py — detect_commit_drift, detect_file_drift, drift_score
  - scripts/agent_compliance_checker.py — check_compliance, rule_applies_to_agent, check_* funcs
"""

import json
import sys
import pytest
from pathlib import Path
from unittest.mock import patch

# Add scripts to path so _lib is importable as a package
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))


# ---------------------------------------------------------------------------
# scoring.py
# ---------------------------------------------------------------------------


class TestScoringLib:
    """Tests for scripts/_lib/scoring.py"""

    def test_dimensions_weights_sum_approximately_one(self):
        """Active weights (non-zero) should sum close to 1.0."""
        from _lib.scoring import DIMENSIONS

        total = sum(DIMENSIONS.values())
        assert total == pytest.approx(1.0, abs=0.02)

    def test_structural_overrides_sum_approximately_one(self):
        """Structural weight overrides should also sum close to 1.0."""
        from _lib.scoring import STRUCTURAL_WEIGHT_OVERRIDES

        total = sum(STRUCTURAL_WEIGHT_OVERRIDES.values())
        assert total == pytest.approx(1.0, abs=0.02)

    def test_composite_score_all_perfect(self):
        """All 10s -> composite ~ 10.0."""
        from _lib.scoring import DIMENSIONS, composite_score

        scores = {dim: 10.0 for dim in DIMENSIONS}
        assert composite_score(scores) == pytest.approx(10.0, abs=0.01)

    def test_composite_score_all_zero(self):
        """All 0s -> composite ~ 0.0."""
        from _lib.scoring import DIMENSIONS, composite_score

        scores = {dim: 0.0 for dim in DIMENSIONS}
        assert composite_score(scores) == pytest.approx(0.0, abs=0.01)

    def test_composite_score_with_none_values(self):
        """None values should be skipped, weights renormalized."""
        from _lib.scoring import composite_score

        scores = {
            "task_completion": 10.0,
            "code_quality": None,
            "terminal_efficiency": None,
            "context_utilization": None,
            "pipeline_compliance": None,
            "error_rate": None,
            "instruction_adherence": None,
            "handoff_quality": None,
            "regression_avoidance": None,
            "engineering_accuracy": None,
        }
        # Only task_completion is scored -> composite = 10.0
        assert composite_score(scores) == pytest.approx(10.0, abs=0.01)

    def test_composite_score_all_none(self):
        """All None values -> composite = 0.0 (zero weight)."""
        from _lib.scoring import DIMENSIONS, composite_score

        scores = {dim: None for dim in DIMENSIONS}
        assert composite_score(scores) == 0.0

    def test_composite_score_structural_agent_override(self):
        """structural-engineer gets boosted engineering_accuracy (25% vs 15%)."""
        from _lib.scoring import DIMENSIONS, composite_score

        # Give engineering_accuracy 10 and everything else 0
        scores = {dim: 0.0 for dim in DIMENSIONS}
        scores["engineering_accuracy"] = 10.0

        normal = composite_score(scores, agent_name="backend")
        structural = composite_score(scores, agent_name="structural-engineer")

        # Structural agent weights engineering_accuracy at 0.25 vs 0.15
        assert structural > normal

    def test_composite_score_structural_math_also_overridden(self):
        """structural-math also uses STRUCTURAL_WEIGHT_OVERRIDES."""
        from _lib.scoring import DIMENSIONS, composite_score

        scores = {dim: 0.0 for dim in DIMENSIONS}
        scores["engineering_accuracy"] = 10.0

        normal = composite_score(scores, agent_name="frontend")
        structural = composite_score(scores, agent_name="structural-math")

        assert structural > normal

    def test_composite_score_normal_agent(self):
        """Non-structural agent uses default weights."""
        from _lib.scoring import DIMENSIONS, composite_score

        scores = {dim: 5.0 for dim in DIMENSIONS}
        result = composite_score(scores, agent_name="frontend")
        assert result == pytest.approx(5.0, abs=0.01)

    def test_grade_excellent(self):
        """>= 9.0 -> 'Excellent'."""
        from _lib.scoring import grade

        assert grade(9.5) == "Excellent"
        assert grade(10.0) == "Excellent"

    def test_grade_good(self):
        """>= 7.0 -> 'Good'."""
        from _lib.scoring import grade

        assert grade(7.5) == "Good"
        assert grade(8.9) == "Good"

    def test_grade_needs_improvement(self):
        """>= 5.0 -> 'Needs Improvement'."""
        from _lib.scoring import grade

        assert grade(5.0) == "Needs Improvement"
        assert grade(6.9) == "Needs Improvement"

    def test_grade_critical(self):
        """< 5.0 -> 'Critical'."""
        from _lib.scoring import grade

        assert grade(4.9) == "Critical"
        assert grade(0.0) == "Critical"

    def test_grade_boundary_9(self):
        """Exactly 9.0 -> 'Excellent'."""
        from _lib.scoring import grade

        assert grade(9.0) == "Excellent"

    def test_grade_boundary_7(self):
        """Exactly 7.0 -> 'Good'."""
        from _lib.scoring import grade

        assert grade(7.0) == "Good"

    def test_grade_boundary_5(self):
        """Exactly 5.0 -> 'Needs Improvement'."""
        from _lib.scoring import grade

        assert grade(5.0) == "Needs Improvement"

    def test_auto_and_manual_dimensions_are_disjoint(self):
        """AUTO_SCORED_DIMENSIONS and MANUAL_DIMENSIONS should not overlap."""
        from _lib.scoring import AUTO_SCORED_DIMENSIONS, MANUAL_DIMENSIONS

        overlap = AUTO_SCORED_DIMENSIONS & MANUAL_DIMENSIONS
        assert overlap == set(), f"Overlap: {overlap}"


# ---------------------------------------------------------------------------
# agent_registry.py
# ---------------------------------------------------------------------------


class TestAgentRegistry:
    """Tests for scripts/_lib/agent_registry.py"""

    def setup_method(self):
        """Clear agent cache between tests."""
        import _lib.agent_registry as agent_registry

        agent_registry._AGENT_CACHE = None

    def test_discover_agents_finds_agents(self):
        """Should find agents from .github/agents/."""
        from _lib.agent_registry import discover_agents

        agents = discover_agents()
        assert len(agents) > 0

    def test_discover_agents_includes_known_agents(self):
        """Should include well-known agents like backend, frontend, tester."""
        from _lib.agent_registry import discover_agents

        agents = discover_agents()
        # Agent names: backend.agent.md -> "backend"
        for name in ["backend", "frontend", "tester"]:
            assert name in agents, f"Missing agent: {name}"

    def test_agent_info_has_required_fields(self):
        """Each AgentInfo should have name, description, tools, model, md_path."""
        from _lib.agent_registry import discover_agents

        agents = discover_agents()
        for name, info in agents.items():
            assert info.name == name
            assert isinstance(info.description, str)
            assert isinstance(info.tools, list)
            assert isinstance(info.model, str)
            assert isinstance(info.md_path, Path)
            assert isinstance(info.is_safety_critical, bool)

    def test_safety_critical_agents(self):
        """structural-engineer and structural-math should be safety-critical."""
        from _lib.agent_registry import is_safety_critical

        assert is_safety_critical("structural-engineer") is True
        assert is_safety_critical("structural-math") is True

    def test_non_safety_critical_agents(self):
        """frontend, backend, ops etc. should NOT be safety-critical."""
        from _lib.agent_registry import is_safety_critical

        for name in ["frontend", "backend", "ops", "tester", "doc-master"]:
            assert is_safety_critical(name) is False

    def test_get_agent_names_sorted(self):
        """Should return sorted list."""
        from _lib.agent_registry import get_agent_names

        names = get_agent_names()
        assert names == sorted(names)
        assert len(names) > 0

    def test_get_agent_info_existing(self):
        """Should return AgentInfo for known agent."""
        from _lib.agent_registry import get_agent_info

        info = get_agent_info("tester")
        assert info is not None
        assert info.name == "tester"

    def test_get_agent_info_nonexistent(self):
        """Should return None for unknown agent."""
        from _lib.agent_registry import get_agent_info

        assert get_agent_info("nonexistent-agent-xyz") is None

    def test_parse_frontmatter_valid(self):
        """YAML frontmatter should parse correctly."""
        from _lib.agent_registry import _parse_frontmatter

        content = (
            "---\n"
            'description: "Test agent"\n'
            "tools: ['search', 'editFiles']\n"
            "model: Claude Opus 4.6 (copilot)\n"
            "---\n"
            "\n"
            "# Test Agent\n"
        )
        metadata = _parse_frontmatter(content)
        assert metadata["description"] == "Test agent"
        assert metadata["model"] == "Claude Opus 4.6 (copilot)"
        assert "search" in metadata["tools"]

    def test_parse_frontmatter_empty(self):
        """Content without frontmatter should return empty dict."""
        from _lib.agent_registry import _parse_frontmatter

        metadata = _parse_frontmatter("# Just a heading\nNo frontmatter here.")
        assert metadata == {}

    def test_discover_agents_caches_results(self):
        """Second call should return cached results."""
        from _lib.agent_registry import discover_agents

        agents1 = discover_agents()
        agents2 = discover_agents()
        assert agents1 is agents2  # Same object = cached


# ---------------------------------------------------------------------------
# agent_data.py
# ---------------------------------------------------------------------------


class TestAgentData:
    """Tests for scripts/_lib/agent_data.py — uses tmp_path fixture."""

    def test_ensure_dirs_creates_all(self, tmp_path):
        """Should create sessions/, trends/, drift/, backups/, paper-export/."""
        import _lib.agent_data as agent_data

        with patch.object(
            agent_data, "PERFORMANCE_DIR", tmp_path / "perf"
        ), patch.object(
            agent_data, "SESSIONS_DIR", tmp_path / "perf" / "sessions"
        ), patch.object(
            agent_data, "TRENDS_DIR", tmp_path / "perf" / "trends"
        ), patch.object(
            agent_data, "DRIFT_DIR", tmp_path / "perf" / "drift"
        ), patch.object(
            agent_data, "BACKUPS_DIR", tmp_path / "perf" / "backups"
        ), patch.object(
            agent_data, "PAPER_DIR", tmp_path / "perf" / "paper-export"
        ):
            agent_data.ensure_dirs()

        assert (tmp_path / "perf" / "sessions").is_dir()
        assert (tmp_path / "perf" / "trends").is_dir()
        assert (tmp_path / "perf" / "drift").is_dir()
        assert (tmp_path / "perf" / "backups").is_dir()
        assert (tmp_path / "perf" / "paper-export").is_dir()

    def test_save_load_session_roundtrip(self, tmp_path):
        """Save then load -> identical data."""
        import _lib.agent_data as agent_data

        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir(parents=True)
        with patch.object(agent_data, "SESSIONS_DIR", sessions_dir), patch.object(
            agent_data, "PERFORMANCE_DIR", tmp_path
        ):
            data = {"agent": "tester", "score": 8.5, "commits": []}
            agent_data.save_session("2026-04-01T14-30", data)
            loaded = agent_data.load_session("2026-04-01T14-30")

        assert loaded == data

    def test_load_session_nonexistent(self, tmp_path):
        """Should return None."""
        import _lib.agent_data as agent_data

        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir(parents=True)
        with patch.object(agent_data, "SESSIONS_DIR", sessions_dir):
            result = agent_data.load_session("nonexistent-session")

        assert result is None

    def test_list_sessions_chronological(self, tmp_path):
        """Multiple sessions -> sorted by ID."""
        import _lib.agent_data as agent_data

        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir(parents=True)
        # Create sessions in reverse order
        for sid in ["2026-04-03", "2026-04-01", "2026-04-02"]:
            (sessions_dir / f"{sid}.json").write_text(json.dumps({"id": sid}))

        with patch.object(agent_data, "SESSIONS_DIR", sessions_dir):
            result = agent_data.list_sessions()

        assert result == ["2026-04-01", "2026-04-02", "2026-04-03"]

    def test_list_sessions_empty(self, tmp_path):
        """No sessions dir -> empty list."""
        import _lib.agent_data as agent_data

        with patch.object(agent_data, "SESSIONS_DIR", tmp_path / "nonexistent"):
            result = agent_data.list_sessions()

        assert result == []

    def test_scorecard_index_roundtrip(self, tmp_path):
        """Save then load scorecard."""
        import _lib.agent_data as agent_data

        with patch.object(agent_data, "PERFORMANCE_DIR", tmp_path):
            data = {"backend": [{"score": 8.0}], "frontend": [{"score": 7.5}]}
            agent_data.save_scorecard_index(data)
            loaded = agent_data.load_scorecard_index()

        assert loaded == data

    def test_scorecard_index_empty(self, tmp_path):
        """No file -> empty dict."""
        import _lib.agent_data as agent_data

        with patch.object(agent_data, "PERFORMANCE_DIR", tmp_path / "empty"):
            result = agent_data.load_scorecard_index()

        assert result == {}

    def test_pending_evolutions_roundtrip(self, tmp_path):
        """Save then load pending evolutions."""
        import _lib.agent_data as agent_data

        with patch.object(agent_data, "PERFORMANCE_DIR", tmp_path):
            evolutions = [
                {"agent": "backend", "proposal": "Add caching"},
                {"agent": "tester", "proposal": "Coverage gates"},
            ]
            agent_data.save_pending_evolutions(evolutions)
            loaded = agent_data.load_pending_evolutions()

        assert loaded == evolutions

    def test_pending_evolutions_empty(self, tmp_path):
        """No file -> empty list."""
        import _lib.agent_data as agent_data

        with patch.object(agent_data, "PERFORMANCE_DIR", tmp_path / "empty"):
            result = agent_data.load_pending_evolutions()

        assert result == []

    def test_save_session_creates_dirs(self, tmp_path):
        """save_session should auto-create directories via ensure_dirs."""
        import _lib.agent_data as agent_data

        perf = tmp_path / "auto_create"
        with patch.object(agent_data, "PERFORMANCE_DIR", perf), patch.object(
            agent_data, "SESSIONS_DIR", perf / "sessions"
        ), patch.object(agent_data, "TRENDS_DIR", perf / "trends"), patch.object(
            agent_data, "DRIFT_DIR", perf / "drift"
        ), patch.object(
            agent_data, "BACKUPS_DIR", perf / "backups"
        ), patch.object(
            agent_data, "PAPER_DIR", perf / "paper-export"
        ):
            agent_data.save_session("test-session", {"data": True})

        assert (perf / "sessions" / "test-session.json").exists()


# ---------------------------------------------------------------------------
# agent_scorer.py
# ---------------------------------------------------------------------------


class TestAgentScorer:
    """Tests for scripts/agent_scorer.py"""

    def test_auto_score_full_session(self):
        """Full session data -> all 5 auto dimensions scored."""
        from agent_scorer import auto_score_agent

        session_data = {
            "terminal_commands": [
                {"cmd": "pytest", "prescribed": True},
                {"cmd": "ls", "prescribed": False},
            ],
            "commits": [{"message": "feat: add test"}],
            "test_results": {"passed": 10, "failed": 0},
            "files_changed": {
                "Python/structural_lib/codes/is456/flexure.py": "modified",
                "docs/TASKS.md": "modified",
            },
            "collection_timestamp": "2026-04-01T14:30:00",
        }

        scores = auto_score_agent(session_data, "backend")

        assert scores["terminal_efficiency"] is not None
        assert scores["pipeline_compliance"] is not None
        assert scores["error_rate"] is not None
        assert scores["engineering_accuracy"] is not None

    def test_auto_score_terminal_efficiency(self):
        """Terminal efficiency = prescribed/total * 10."""
        from agent_scorer import auto_score_agent

        session_data = {
            "terminal_commands": [
                {"cmd": "pytest", "prescribed": True},
                {"cmd": "pytest", "prescribed": True},
                {"cmd": "ls", "prescribed": False},
                {"cmd": "cat", "prescribed": False},
            ],
            "commits": [],
            "test_results": {},
            "files_changed": {},
        }

        scores = auto_score_agent(session_data, "tester")
        # 2/4 prescribed = 0.5 * 10 = 5.0
        assert scores["terminal_efficiency"] == pytest.approx(5.0, abs=0.01)

    def test_auto_score_missing_terminal_data(self):
        """No terminal commands -> terminal_efficiency defaults to 7.0."""
        from agent_scorer import auto_score_agent

        session_data = {
            "commits": [],
            "test_results": {},
            "files_changed": {},
        }

        scores = auto_score_agent(session_data, "backend")
        assert scores["terminal_efficiency"] == 7.0

    def test_auto_score_perfect_tests(self):
        """100% test pass rate -> error_rate = 10.0."""
        from agent_scorer import auto_score_agent

        session_data = {
            "commits": [],
            "test_results": {"passed": 50, "failed": 0},
            "files_changed": {},
        }

        scores = auto_score_agent(session_data, "tester")
        assert scores["error_rate"] == pytest.approx(10.0, abs=0.01)

    def test_auto_score_partial_test_failure(self):
        """80% pass rate -> error_rate = 8.0."""
        from agent_scorer import auto_score_agent

        session_data = {
            "commits": [],
            "test_results": {"passed": 8, "failed": 2},
            "files_changed": {},
        }

        scores = auto_score_agent(session_data, "tester")
        assert scores["error_rate"] == pytest.approx(8.0, abs=0.01)

    def test_auto_score_no_tests(self):
        """No test_results -> error_rate is None."""
        from agent_scorer import auto_score_agent

        session_data = {
            "commits": [],
            "test_results": {},
            "files_changed": {},
        }

        scores = auto_score_agent(session_data, "backend")
        assert scores["error_rate"] is None

    def test_auto_score_engineering_accuracy_structural_perfect(self):
        """Structural changes + all tests pass -> 9.0."""
        from agent_scorer import auto_score_agent

        session_data = {
            "commits": [],
            "test_results": {"passed": 10, "failed": 0},
            "files_changed": {
                "Python/structural_lib/codes/is456/flexure.py": "modified",
            },
        }

        scores = auto_score_agent(session_data, "backend")
        assert scores["engineering_accuracy"] == 9.0

    def test_auto_score_engineering_accuracy_no_structural(self):
        """No structural changes -> engineering_accuracy is None."""
        from agent_scorer import auto_score_agent

        session_data = {
            "commits": [],
            "test_results": {"passed": 10, "failed": 0},
            "files_changed": {"react_app/src/App.tsx": "modified"},
        }

        scores = auto_score_agent(session_data, "frontend")
        assert scores["engineering_accuracy"] is None

    def test_validate_score_valid(self):
        """0, 5, 10 -> no error."""
        from agent_scorer import validate_score

        # These should not raise / sys.exit
        validate_score(0.0, "test")
        validate_score(5.0, "test")
        validate_score(10.0, "test")

    def test_validate_score_none(self):
        """None -> no error (None is allowed)."""
        from agent_scorer import validate_score

        validate_score(None, "test")  # Should not raise

    def test_validate_score_negative(self):
        """-1 -> sys.exit(1)."""
        from agent_scorer import validate_score

        with pytest.raises(SystemExit):
            validate_score(-1.0, "test")

    def test_validate_score_above_ten(self):
        """11 -> sys.exit(1)."""
        from agent_scorer import validate_score

        with pytest.raises(SystemExit):
            validate_score(11.0, "test")


# ---------------------------------------------------------------------------
# agent_drift_detector.py
# ---------------------------------------------------------------------------


class TestDriftDetector:
    """Tests for scripts/agent_drift_detector.py"""

    def test_drift_score_no_violations(self):
        """0 violations, 5 rules -> 1.0."""
        from agent_drift_detector import drift_score

        assert drift_score(0, 5) == 1.0

    def test_drift_score_all_violations(self):
        """5 violations, 5 rules -> 0.0."""
        from agent_drift_detector import drift_score

        assert drift_score(5, 5) == 0.0

    def test_drift_score_partial(self):
        """2 violations, 10 rules -> 0.8."""
        from agent_drift_detector import drift_score

        assert drift_score(2, 10) == pytest.approx(0.8, abs=0.01)

    def test_drift_score_zero_rules(self):
        """0 rules -> 1.0 (perfect score when no rules apply)."""
        from agent_drift_detector import drift_score

        assert drift_score(0, 0) == 1.0

    def test_drift_score_clamped_to_zero(self):
        """More violations than rules -> clamped to 0.0."""
        from agent_drift_detector import drift_score

        assert drift_score(10, 5) == 0.0

    def test_detect_commit_drift_forbidden_ops(self):
        """ops agent with 'git push' in commit -> violation."""
        from agent_drift_detector import detect_commit_drift

        commits = [{"message": "git push origin main"}]
        violations = detect_commit_drift(commits, "ops")
        assert len(violations) > 0
        assert any(v["rule_id"] == "OPS-004" for v in violations)

    def test_detect_commit_drift_forbidden_force(self):
        """ops agent with '--force' -> violation."""
        from agent_drift_detector import detect_commit_drift

        commits = [{"message": "pushed with --force flag"}]
        violations = detect_commit_drift(commits, "ops")
        assert len(violations) > 0
        assert any(v["rule_id"] == "OPS-005" for v in violations)

    def test_detect_commit_drift_clean_ops(self):
        """ops agent with clean commit -> no violations."""
        from agent_drift_detector import detect_commit_drift

        commits = [{"message": "feat: update CI pipeline"}]
        violations = detect_commit_drift(commits, "ops")
        assert len(violations) == 0

    def test_detect_commit_drift_unknown_agent(self):
        """Unknown agent -> no rules -> no violations."""
        from agent_drift_detector import detect_commit_drift

        commits = [{"message": "git push --force"}]
        violations = detect_commit_drift(commits, "nonexistent-agent")
        assert violations == []

    def test_detect_file_drift_forbidden_css(self):
        """frontend agent creating .css file -> violation."""
        from agent_drift_detector import detect_file_drift

        files = {"react_app/src/components/Widget.css": "added"}
        violations = detect_file_drift(files, "frontend")
        assert len(violations) > 0
        assert any(v["rule_id"] == "FE-003" for v in violations)

    def test_detect_file_drift_clean_frontend(self):
        """frontend agent creating .tsx file -> no violations."""
        from agent_drift_detector import detect_file_drift

        files = {"react_app/src/components/Widget.tsx": "added"}
        violations = detect_file_drift(files, "frontend")
        assert len(violations) == 0

    def test_detect_file_drift_unknown_agent(self):
        """Unknown agent -> no violations."""
        from agent_drift_detector import detect_file_drift

        files = {"any/file.css": "added"}
        violations = detect_file_drift(files, "nonexistent-agent")
        assert violations == []

    def test_detect_drift_full_analysis(self):
        """Full drift analysis returns expected structure."""
        from agent_drift_detector import detect_drift

        session_data = {
            "session_id": "2026-04-01T14-30",
            "agents_active": ["ops"],
            "commits": [{"message": "git push origin main"}],
            "files_changed": {},
        }

        result = detect_drift(session_data)
        assert "drift_events" in result
        assert "agent_drift_scores" in result
        assert "summary" in result
        assert result["summary"]["total_events"] > 0

    def test_detect_drift_agent_filter(self):
        """Agent filter limits analysis to one agent."""
        from agent_drift_detector import detect_drift

        session_data = {
            "session_id": "2026-04-01T14-30",
            "agents_active": ["ops", "frontend"],
            "commits": [{"message": "git push"}],
            "files_changed": {},
        }

        result = detect_drift(session_data, agent_filter="frontend")
        # Should only analyze frontend, not ops
        assert "ops" not in result.get("agent_drift_scores", {})

    def test_detect_commit_drift_multiple_forbidden(self):
        """ops agent commit triggering multiple rules."""
        from agent_drift_detector import detect_commit_drift

        commits = [{"message": "git add . && git commit -m 'wip' && git push --force"}]
        violations = detect_commit_drift(commits, "ops")
        # Should trigger OPS-005 (--force) at minimum
        rule_ids = {v["rule_id"] for v in violations}
        assert "OPS-005" in rule_ids

    def test_detect_commit_drift_admin_merge(self):
        """ops agent with 'gh pr merge --admin' -> CRITICAL violation."""
        from agent_drift_detector import detect_commit_drift

        commits = [{"message": "gh pr merge --admin"}]
        violations = detect_commit_drift(commits, "ops")
        assert any(v["rule_id"] == "OPS-006" for v in violations)
        assert any(v["severity"] == "CRITICAL" for v in violations)


# ---------------------------------------------------------------------------
# agent_compliance_checker.py
# ---------------------------------------------------------------------------


class TestComplianceChecker:
    """Tests for scripts/agent_compliance_checker.py"""

    def test_rule_applies_to_all(self):
        """Rule with applies_to='all' -> True for any agent."""
        from agent_compliance_checker import rule_applies_to_agent

        rule = {"applies_to": "all"}
        assert rule_applies_to_agent(rule, "backend") is True
        assert rule_applies_to_agent(rule, "frontend") is True
        assert rule_applies_to_agent(rule, "any-agent") is True

    def test_rule_applies_specific_agent(self):
        """Rule for 'backend' -> True for backend, False for frontend."""
        from agent_compliance_checker import rule_applies_to_agent

        rule = {"applies_to": ["backend", "tester"]}
        assert rule_applies_to_agent(rule, "backend") is True
        assert rule_applies_to_agent(rule, "tester") is True
        assert rule_applies_to_agent(rule, "frontend") is False

    def test_check_file_modified_true(self):
        """session_data with file in files_changed -> True."""
        from agent_compliance_checker import check_file_modified

        session_data = {
            "files_changed": {"docs/TASKS.md": "modified"},
        }
        assert check_file_modified(session_data, "docs/TASKS.md") is True

    def test_check_file_modified_false(self):
        """session_data without file -> False."""
        from agent_compliance_checker import check_file_modified

        session_data = {"files_changed": {}}
        assert check_file_modified(session_data, "docs/TASKS.md") is False

    def test_check_feedback_exists_true(self, tmp_path):
        """session_data with feedback files -> True."""
        from agent_compliance_checker import check_feedback_exists

        logs_feedback = tmp_path / "logs" / "feedback"
        logs_feedback.mkdir(parents=True)
        (logs_feedback / "2026-04-01_backend.json").write_text("{}")

        with patch("agent_compliance_checker.REPO_ROOT", tmp_path):
            session_data = {"session_id": "2026-04-01T14:30"}
            assert check_feedback_exists(session_data) is True

    def test_check_feedback_exists_false(self, tmp_path):
        """No feedback files -> False."""
        from agent_compliance_checker import check_feedback_exists

        with patch("agent_compliance_checker.REPO_ROOT", tmp_path):
            session_data = {"session_id": "2026-04-01T14:30"}
            assert check_feedback_exists(session_data) is False

    def test_check_feedback_exists_no_session_id(self):
        """No session_id -> False."""
        from agent_compliance_checker import check_feedback_exists

        assert check_feedback_exists({}) is False

    def test_check_commit_format_valid(self):
        """Conventional commit 'feat(scope): message' -> True."""
        from agent_compliance_checker import check_commit_format

        session_data = {
            "commits": [
                {"message": "feat(evolver): add scoring module"},
                {"message": "fix: correct calculation"},
                {"message": "docs: update README"},
                {"message": "test(beam): add unit tests"},
            ],
        }
        assert check_commit_format(session_data) is True

    def test_check_commit_format_invalid(self):
        """'random commit message' -> False."""
        from agent_compliance_checker import check_commit_format

        session_data = {
            "commits": [{"message": "random commit message"}],
        }
        assert check_commit_format(session_data) is False

    def test_check_commit_format_empty(self):
        """No commits -> True (no violations)."""
        from agent_compliance_checker import check_commit_format

        assert check_commit_format({"commits": []}) is True

    def test_check_tests_executed_true(self):
        """session_data with passed tests -> True."""
        from agent_compliance_checker import check_tests_executed

        session_data = {"test_results": {"passed": 5, "failed": 1}}
        assert check_tests_executed(session_data) is True

    def test_check_tests_executed_false(self):
        """session_data with no tests -> False."""
        from agent_compliance_checker import check_tests_executed

        session_data = {"test_results": {}}
        assert check_tests_executed(session_data) is False

    def test_check_compliance_full(self):
        """Full session -> compliance result has expected keys."""
        from agent_compliance_checker import check_compliance

        session_data = {
            "session_id": "2026-04-01T14:30",
            "agents_active": ["backend"],
            "commits": [{"message": "feat: add feature"}],
            "test_results": {"passed": 10, "failed": 0},
            "files_changed": {
                "docs/TASKS.md": "modified",
                "docs/planning/next-session-brief.md": "modified",
            },
        }

        result = check_compliance(session_data, "backend")
        assert "compliance_results" in result
        assert "overall_compliance_rate" in result

        backend_result = result["compliance_results"].get("backend", {})
        assert "rules_checked" in backend_result
        assert "rules_passed" in backend_result
        assert "compliance_rate" in backend_result
        assert "violations" in backend_result

    def test_check_compliance_rate_calculation(self):
        """Known pass/fail -> correct rate."""
        from agent_compliance_checker import check_compliance

        # Backend with no commits, no tests, no file changes -> low compliance
        session_data = {
            "session_id": "2026-04-01T14:30",
            "agents_active": ["backend"],
            "commits": [],
            "test_results": {},
            "files_changed": {},
        }

        result = check_compliance(session_data, "backend")
        backend_result = result["compliance_results"]["backend"]
        # Rate = passed / checked
        expected_rate = (
            backend_result["rules_passed"] / backend_result["rules_checked"]
            if backend_result["rules_checked"] > 0
            else 1.0
        )
        assert backend_result["compliance_rate"] == pytest.approx(
            expected_rate, abs=0.01
        )

    def test_check_compliance_no_agents(self):
        """No agents active -> empty results."""
        from agent_compliance_checker import check_compliance

        session_data = {
            "session_id": "test",
            "agents_active": [],
        }

        result = check_compliance(session_data)
        assert result["compliance_results"] == {}
        assert result["overall_compliance_rate"] == 0.0

    def test_check_no_raw_file_ops_clean(self):
        """No doc deletions/renames -> True."""
        from agent_compliance_checker import check_no_raw_file_ops

        session_data = {"files_changed": {"docs/README.md": "modified"}}
        assert check_no_raw_file_ops(session_data) is True

    def test_check_architecture_no_changes(self):
        """No structural_lib changes -> True."""
        from agent_compliance_checker import check_architecture

        session_data = {"files_changed": {"react_app/src/App.tsx": "modified"}}
        assert check_architecture(session_data) is True

    def test_check_build_ran_no_react(self):
        """No React files changed -> True (N/A)."""
        from agent_compliance_checker import check_build_ran

        session_data = {"files_changed": {"Python/tests/test_core.py": "modified"}}
        assert check_build_ran(session_data) is True
