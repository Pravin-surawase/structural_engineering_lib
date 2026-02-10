#!/usr/bin/env python3
"""Validate trial data JSON schema compliance."""

import json
import sys
from pathlib import Path

# Expected schema
TRIAL_SCHEMA = {
    "required_fields": [
        "trial_id",
        "timestamp",
        "condition",
        "agent_type",
        "task_id",
        "task_description",
        "ground_truth_file",
        "metrics",
        "outcome",
    ],
    "metrics_fields": [
        "time_to_complete_ms",
        "files_accessed",
        "tokens_loaded",
        "wrong_files_opened",
    ],
    "outcome_fields": ["success", "correct_file_found"],
}


def validate_trial(trial_data: dict, filename: str) -> bool:
    """Validate a single trial against schema."""
    errors = []

    # Check required top-level fields
    for field in TRIAL_SCHEMA["required_fields"]:
        if field not in trial_data:
            errors.append(f"Missing required field: {field}")

    # Check metrics fields
    if "metrics" in trial_data:
        for field in TRIAL_SCHEMA["metrics_fields"]:
            if field not in trial_data["metrics"]:
                errors.append(f"Missing metrics field: {field}")

    # Check outcome fields
    if "outcome" in trial_data:
        for field in TRIAL_SCHEMA["outcome_fields"]:
            if field not in trial_data["outcome"]:
                errors.append(f"Missing outcome field: {field}")

    if errors:
        print(f"❌ {filename}:")
        for error in errors:
            print(f"   - {error}")
        return False

    return True


def main():
    data_dir = Path("docs/research/navigation_study/data/raw")

    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        sys.exit(1)

    print("🔍 Validating trial data...")

    total = 0
    valid = 0

    for trial_file in data_dir.rglob("trial_*.json"):
        total += 1
        try:
            with open(trial_file, "r") as f:
                trial_data = json.load(f)

            if validate_trial(trial_data, trial_file.name):
                valid += 1
        except json.JSONDecodeError:
            print(f"❌ {trial_file.name}: Invalid JSON")
        except Exception as e:
            print(f"❌ {trial_file.name}: {e}")

    print("\n📊 Validation Results:")
    print(f"   Total files: {total}")
    print(f"   Valid: {valid}")
    print(f"   Invalid: {total - valid}")

    if valid == total:
        print("\n✅ All trial data is valid!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - valid} files have validation errors")
        sys.exit(1)


if __name__ == "__main__":
    main()
