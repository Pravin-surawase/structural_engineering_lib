#!/usr/bin/env bash
# Measure AI agent navigation efficiency
# Usage:
#   ./measure_agent_navigation.sh [baseline|hierarchical] [agent_type] [task_id|pilot|all] [--trials N]

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Configuration
CONDITION="baseline"
AGENT_TYPE="gpt4_turbo"
TASK_ID="all"
TRIALS=1
DATA_DIR="docs/research/navigation_study/data/raw/${CONDITION}/${AGENT_TYPE}"

# Optional flags + positional args
POSITIONAL=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --agent)
            AGENT_TYPE="${2:-gpt4_turbo}"
            shift 2
            ;;
        --task)
            TASK_ID="${2:-all}"
            shift 2
            ;;
        --trials|--reps)
            TRIALS="${2:-1}"
            shift 2
            ;;
        --help|-h)
            echo "Usage: ./measure_agent_navigation.sh [baseline|hierarchical] [agent_type] [task_id|pilot|all] [--trials N]"
            exit 0
            ;;
        *)
            POSITIONAL+=("$1")
            shift
            ;;
    esac
done

if [[ ${#POSITIONAL[@]} -gt 0 ]]; then
    CONDITION="${POSITIONAL[0]}"
fi
if [[ ${#POSITIONAL[@]} -gt 1 ]]; then
    AGENT_TYPE="${POSITIONAL[1]}"
fi
if [[ ${#POSITIONAL[@]} -gt 2 ]]; then
    TASK_ID="${POSITIONAL[2]}"
fi

DATA_DIR="docs/research/navigation_study/data/raw/${CONDITION}/${AGENT_TYPE}"

# Task definitions (10-task pilot set)
TASK_IDS=(task01 task02 task03 task04 task05 task06 task07 task08 task09 task10)
PILOT_TASKS=(task01 task06 task09)

echo "📊 Navigation Efficiency Measurement"
echo "   Condition: ${CONDITION}"
echo "   Agent: ${AGENT_TYPE}"
echo "   Task: ${TASK_ID}"
echo "   Trials: ${TRIALS}"
echo ""

# Create output directory
mkdir -p "$DATA_DIR"

# Helpers
task_info() {
    case "$1" in
        task01) echo "Find flexure module API|docs/reference/api.md" ;;
        task02) echo "Find shear module API|docs/reference/api.md" ;;
        task03) echo "Find detailing output entry point|docs/reference/api.md" ;;
        task04) echo "Find error schema definitions|docs/reference/error-schema.md" ;;
        task05) echo "Find Streamlit validation checklist|docs/reference/streamlit-validation.md" ;;
        task06) echo "Find git workflow rules|docs/git-workflow-ai-agents.md" ;;
        task07) echo "Find agent bootstrap quick start|docs/agent-bootstrap.md" ;;
        task08) echo "Find handoff workflow steps|docs/contributing/end-of-session-workflow.md" ;;
        task09) echo "Find migration decision summary|agents/agent-9/governance/DECISION-SUMMARY.md" ;;
        task10) echo "Find automation catalog|docs/reference/automation-catalog.md" ;;
        *) echo "" ;;
    esac
}

baseline_paths() {
    case "$1" in
        task01|task02|task03) echo "docs/README.md docs/reference/README.md docs/reference/api.md" ;;
        task04) echo "docs/README.md docs/reference/README.md docs/reference/error-schema.md" ;;
        task05) echo "docs/README.md docs/reference/README.md docs/reference/streamlit-validation.md" ;;
        task06) echo "docs/README.md docs/git-workflow-ai-agents.md" ;;
        task07) echo "docs/README.md docs/agent-bootstrap.md" ;;
        task08) echo "docs/README.md docs/contributing/end-of-session-workflow.md" ;;
        task09) echo "agents/agent-9/README.md agents/agent-9/governance/DECISION-SUMMARY.md" ;;
        task10) echo "docs/README.md docs/reference/README.md docs/reference/automation-catalog.md" ;;
        *) echo "" ;;
    esac
}

hierarchical_paths() {
    case "$1" in
        task01|task02|task03) echo "docs/index.json docs/reference/index.json docs/reference/api.md" ;;
        task04) echo "docs/index.json docs/reference/index.json docs/reference/error-schema.md" ;;
        task05) echo "docs/index.json docs/reference/index.json docs/reference/streamlit-validation.md" ;;
        task06) echo "docs/index.json docs/git-workflow-ai-agents.md" ;;
        task07) echo "docs/index.json docs/agent-bootstrap.md" ;;
        task08) echo "docs/index.json docs/contributing/index.json docs/contributing/end-of-session-workflow.md" ;;
        task09) echo "agents/index.json agents/agent-9/governance/index.json agents/agent-9/governance/DECISION-SUMMARY.md" ;;
        task10) echo "docs/index.json docs/reference/index.json docs/reference/automation-catalog.md" ;;
        *) echo "" ;;
    esac
}

get_navigation_path() {
    local task_id="$1"
    local condition="$2"
    local path_list=""

    if [[ "$condition" == "hierarchical" ]]; then
        path_list="$(hierarchical_paths "$task_id")"
    else
        path_list="$(baseline_paths "$task_id")"
    fi

    if [[ -z "$path_list" ]]; then
        IFS='|' read -r _desc truth <<< "$(task_info "$task_id")"
        path_list="$truth"
    fi

    echo "$path_list"
}

count_tokens() {
    local file="$1"
    wc -w < "$file" | tr -d ' '
}

now_ms() {
    if command -v python3 >/dev/null 2>&1; then
        python3 - <<'PY'
import time
print(int(time.time() * 1000))
PY
    else
        echo $(( $(date +%s) * 1000 ))
    fi
}

# Function to measure single task
measure_task() {
    local task_id="$1"
    local task_desc="$2"
    local ground_truth="$3"
    local rep="$4"

    echo "🔍 Task ${task_id}: ${task_desc}"

    # Generate trial ID
    local trial_id="$(date +%Y-%m-%dT%H-%M-%S)-${task_id}-${CONDITION}-${AGENT_TYPE}-rep${rep}"

    # Build navigation path
    local navigation_path
    navigation_path="$(get_navigation_path "$task_id" "$CONDITION")"

    local files_accessed=0
    local bytes_loaded=0
    local tokens_loaded=0
    local wrong_files_opened=0
    local correct_file_found=false
    local navigation_json=""

    # Start timer
    local start_time
    start_time=$(now_ms)

    for path in $navigation_path; do
        if [[ -f "$path" ]]; then
            files_accessed=$((files_accessed + 1))
            bytes_loaded=$((bytes_loaded + $(wc -c < "$path" | tr -d ' ')))
            tokens_loaded=$((tokens_loaded + $(count_tokens "$path")))
            navigation_json="${navigation_json}\"${path}\","
        else
            navigation_json="${navigation_json}\"${path} (missing)\","
        fi
    done

    if [[ " $navigation_path " == *" $ground_truth "* ]] && [[ -f "$ground_truth" ]]; then
        correct_file_found=true
    fi

    if [[ "$correct_file_found" == true ]]; then
        wrong_files_opened=$((files_accessed - 1))
    else
        wrong_files_opened=$files_accessed
    fi

    # End timer
    local end_time
    end_time=$(now_ms)
    local duration=$((end_time - start_time))

    # Generate trial data (JSONL format)
    cat > "${DATA_DIR}/trial_${trial_id}.json" <<EOF
{
  "trial_id": "${trial_id}",
  "timestamp": "$(date -Iseconds)",
  "condition": "${CONDITION}",
  "agent_type": "${AGENT_TYPE}",
  "task_id": "${task_id}",
  "task_description": "${task_desc}",
  "ground_truth_file": "${ground_truth}",
  "metrics": {
    "time_to_complete_ms": ${duration},
    "files_accessed": ${files_accessed},
    "bytes_loaded": ${bytes_loaded},
    "tokens_loaded": ${tokens_loaded},
    "wrong_files_opened": ${wrong_files_opened},
    "navigation_path": [${navigation_json%,}]
  },
  "outcome": {
    "success": ${correct_file_found},
    "correct_file_found": ${correct_file_found}
  }
}
EOF

    echo "   ✅ Trial saved: trial_${trial_id}.json"
}

# Run measurements
if [ "$TASK_ID" = "all" ]; then
    echo "📋 Running all 10 pilot tasks"
    for task_key in "${TASK_IDS[@]}"; do
        IFS='|' read -r desc truth <<< "$(task_info "$task_key")"
        for ((rep=1; rep<=TRIALS; rep++)); do
            measure_task "$task_key" "$desc" "$truth" "$rep"
        done
    done
elif [ "$TASK_ID" = "pilot" ]; then
    echo "📋 Running pilot tasks: ${PILOT_TASKS[*]}"
    for task_key in "${PILOT_TASKS[@]}"; do
        IFS='|' read -r desc truth <<< "$(task_info "$task_key")"
        for ((rep=1; rep<=TRIALS; rep++)); do
            measure_task "$task_key" "$desc" "$truth" "$rep"
        done
    done
else
    if [ -n "$(task_info "$TASK_ID")" ]; then
        IFS='|' read -r desc truth <<< "$(task_info "$TASK_ID")"
        for ((rep=1; rep<=TRIALS; rep++)); do
            measure_task "$TASK_ID" "$desc" "$truth" "$rep"
        done
    else
        echo "❌ Unknown task: $TASK_ID"
        exit 1
    fi
fi

echo ""
echo "✅ Measurement complete!"
echo "   Output: ${DATA_DIR}/"
