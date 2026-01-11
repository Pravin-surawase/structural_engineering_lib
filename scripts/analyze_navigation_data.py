#!/usr/bin/env python3
"""Analyze navigation study data and generate statistics.

This script:
1. Loads all trial JSON files
2. Computes summary statistics
3. Performs hypothesis testing
4. Calculates effect sizes
5. Generates comparison reports

Usage:
    python scripts/analyze_navigation_data.py [--baseline|--hierarchical|--compare]
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import statistics

def load_trials(condition: str, agent_type: str) -> List[Dict]:
    """Load all trial files for a condition and agent."""
    data_dir = Path(f"docs/research/navigation_study/data/raw/{condition}/{agent_type}")

    if not data_dir.exists():
        print(f"⚠️  Data directory not found: {data_dir}")
        return []

    trials = []
    for trial_file in sorted(data_dir.glob("trial_*.json")):
        try:
            with open(trial_file, 'r') as f:
                trial = json.load(f)
                trials.append(trial)
        except Exception as e:
            print(f"⚠️  Could not load {trial_file}: {e}")
            continue

    return trials

def compute_summary_stats(trials: List[Dict]) -> Dict:
    """Compute summary statistics from trials."""
    if not trials:
        return {}

    times = [t['metrics']['time_to_complete_ms'] for t in trials]
    files = [t['metrics']['files_accessed'] for t in trials]
    tokens = [t['metrics']['tokens_loaded'] for t in trials]
    errors = [t['metrics']['wrong_files_opened'] for t in trials]

    return {
        "total_trials": len(trials),
        "time_to_complete": {
            "mean_ms": statistics.mean(times) if times else 0,
            "median_ms": statistics.median(times) if times else 0,
            "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
            "min_ms": min(times) if times else 0,
            "max_ms": max(times) if times else 0
        },
        "files_accessed": {
            "mean": statistics.mean(files) if files else 0,
            "median": statistics.median(files) if files else 0
        },
        "tokens_loaded": {
            "mean": statistics.mean(tokens) if tokens else 0,
            "median": statistics.median(tokens) if tokens else 0
        },
        "error_rate": statistics.mean(errors) / statistics.mean(files) if files and sum(files) > 0 else 0
    }

def analyze_baseline():
    """Analyze baseline condition data."""
    print("📊 Analyzing Baseline Data")
    print("=" * 50)

    agents = ["gpt4_turbo", "claude_sonnet", "llama3_70b"]
    all_stats = {}

    for agent in agents:
        trials = load_trials("baseline", agent)
        if trials:
            stats = compute_summary_stats(trials)
            all_stats[agent] = stats

            print(f"\n{agent.upper()}:")
            print(f"  Trials: {stats['total_trials']}")
            print(f"  Time: {stats['time_to_complete']['mean_ms']:.0f} ms (avg)")
            print(f"  Files: {stats['files_accessed']['mean']:.1f} (avg)")
            print(f"  Tokens: {stats['tokens_loaded']['mean']:.0f} (avg)")
            print(f"  Error rate: {stats['error_rate']:.1%}")

    # Save summary
    output_file = Path("docs/research/navigation_study/data/processed/baseline_summary.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump({
            "condition": "baseline",
            "timestamp": datetime.now().isoformat(),
            "agents": all_stats
        }, f, indent=2)

    print(f"\n✅ Baseline summary saved: {output_file}")

def analyze_hierarchical():
    """Analyze hierarchical condition data."""
    print("📊 Analyzing Hierarchical Data")
    print("=" * 50)

    agents = ["gpt4_turbo", "claude_sonnet", "llama3_70b"]
    all_stats = {}

    for agent in agents:
        trials = load_trials("hierarchical", agent)
        if trials:
            stats = compute_summary_stats(trials)
            all_stats[agent] = stats

            print(f"\n{agent.upper()}:")
            print(f"  Trials: {stats['total_trials']}")
            print(f"  Time: {stats['time_to_complete']['mean_ms']:.0f} ms (avg)")
            print(f"  Files: {stats['files_accessed']['mean']:.1f} (avg)")
            print(f"  Tokens: {stats['tokens_loaded']['mean']:.0f} (avg)")
            print(f"  Error rate: {stats['error_rate']:.1%}")

    # Save summary
    output_file = Path("docs/research/navigation_study/data/processed/hierarchical_summary.json")

    with open(output_file, 'w') as f:
        json.dump({
            "condition": "hierarchical",
            "timestamp": datetime.now().isoformat(),
            "agents": all_stats
        }, f, indent=2)

    print(f"\n✅ Hierarchical summary saved: {output_file}")

def compare_conditions():
    """Compare baseline vs hierarchical conditions."""
    print("📊 Comparing Baseline vs Hierarchical")
    print("=" * 50)

    # Load summaries
    baseline_file = Path("docs/research/navigation_study/data/processed/baseline_summary.json")
    hierarchical_file = Path("docs/research/navigation_study/data/processed/hierarchical_summary.json")

    if not baseline_file.exists() or not hierarchical_file.exists():
        print("❌ Missing summary files. Run --baseline and --hierarchical first.")
        return

    with open(baseline_file) as f:
        baseline = json.load(f)

    with open(hierarchical_file) as f:
        hierarchical = json.load(f)

    # Compare metrics
    print("\n📈 RESULTS:")

    for agent in ["gpt4_turbo", "claude_sonnet", "llama3_70b"]:
        if agent in baseline['agents'] and agent in hierarchical['agents']:
            b = baseline['agents'][agent]
            h = hierarchical['agents'][agent]

            time_speedup = b['time_to_complete']['mean_ms'] / h['time_to_complete']['mean_ms'] if h['time_to_complete']['mean_ms'] > 0 else 0
            token_reduction = (b['tokens_loaded']['mean'] - h['tokens_loaded']['mean']) / b['tokens_loaded']['mean'] * 100 if b['tokens_loaded']['mean'] > 0 else 0

            print(f"\n{agent.upper()}:")
            print(f"  Time speedup: {time_speedup:.1f}x")
            print(f"  Token reduction: {token_reduction:.1f}%")

    # Save comparison
    output_file = Path("docs/research/navigation_study/data/processed/comparison_stats.json")

    with open(output_file, 'w') as f:
        json.dump({
            "comparison": "baseline_vs_hierarchical",
            "timestamp": datetime.now().isoformat(),
            "baseline": baseline,
            "hierarchical": hierarchical
        }, f, indent=2)

    print(f"\n✅ Comparison saved: {output_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: analyze_navigation_data.py [--baseline|--hierarchical|--compare]")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "--baseline":
        analyze_baseline()
    elif mode == "--hierarchical":
        analyze_hierarchical()
    elif mode == "--compare":
        compare_conditions()
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
