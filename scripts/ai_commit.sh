#!/bin/bash
# AI-friendly wrapper for safe commits and pushes
# This script ensures ALL commits from AI agents use the safe workflow
#
# Usage:
#   ./scripts/ai_commit.sh "commit message"
#   ./scripts/ai_commit.sh "commit message" --dry-run  # Preview only
#   ./scripts/ai_commit.sh "commit message" --force    # Bypass PR check (for batching)
#   ./scripts/ai_commit.sh --help

set -e  # Exit on any error

# Mark that we're running from automation (for pre-push hook bypass)
export AI_COMMIT_ACTIVE=1

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
DIM='\033[2m'

# Parse flags
DRY_RUN=false
FORCE=false
PUSH_ONLY=false
AMEND=false
PREVIEW=false
UNDO=false
SIGNOFF=false
STATUS=false
BRANCH_MODE=false
BRANCH_TASK_ID=""
BRANCH_DESCRIPTION=""
FINISH_MODE=false
FINISH_DESCRIPTION=""
PR_CHECK=false
CONTINUE_PR=""
COMMIT_MSG=""

i=0
args=("$@")
while [[ $i -lt ${#args[@]} ]]; do
    arg="${args[$i]}"
    case "$arg" in
        --status) STATUS=true ;;
        --branch)
            BRANCH_MODE=true
            i=$((i+1)); BRANCH_TASK_ID="${args[$i]:-}"
            i=$((i+1)); BRANCH_DESCRIPTION="${args[$i]:-}"
            ;;
        --finish)
            FINISH_MODE=true
            # Optional: next arg is description (if it doesn't start with --)
            if [[ $((i+1)) -lt ${#args[@]} && ! "${args[$((i+1))]}" == --* ]]; then
                i=$((i+1)); FINISH_DESCRIPTION="${args[$i]}"
            fi
            ;;
        --pr-check) PR_CHECK=true ;;
        --continue)
            i=$((i+1)); CONTINUE_PR="${args[$i]:-}"
            ;;
        --dry-run) DRY_RUN=true ;;
        --force|-f) FORCE=true ;;
        --push|--push-only) PUSH_ONLY=true ;;
        --amend) AMEND=true ;;
        --preview) PREVIEW=true ;;
        --undo) UNDO=true ;;
        --signoff|-s) SIGNOFF=true ;;
        --help|-h)
            echo "Usage: ai_commit.sh \"commit message\" [--dry-run] [--force] [--push] [--amend] [--preview] [--undo] [--signoff]"
            echo ""
            echo "Options:"
            echo "  --dry-run    Preview what would happen without committing"
            echo "  --force      Bypass PR requirement check (for batching work)"
            echo "  --push       Push already-committed changes (no new commit)"
            echo "  --amend      Amend the last commit (add staged changes to it)"
            echo "  --preview    Show staged changes diff without committing"
            echo "  --undo       Undo last commit (soft reset, keeps changes staged)"
            echo "  --signoff    Add Signed-off-by line (DCO compliance)"
            echo "  --status     Show project status (branch, files, PRs, stashes)"
            echo "  --branch TASK-XXX \"desc\"  Create task branch for PR workflow"
            echo "  --finish [\"desc\"]  Finish current PR: CI poll + merge + cleanup"
            echo "  --continue PR_NUM  Resume interrupted --finish for existing PR"
            echo "  --pr-check   Check if PR is required for current changes"
            echo "  --help       Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./scripts/ai_commit.sh \"docs: update guide\""
            echo "  ./scripts/ai_commit.sh \"feat: add feature\" --dry-run"
            echo "  ./scripts/ai_commit.sh \"feat: batch work\" --force"
            echo "  ./scripts/ai_commit.sh --push          # Push existing commits"
            echo "  ./scripts/ai_commit.sh --amend          # Amend last commit + push"
            echo "  ./scripts/ai_commit.sh \"msg\" --preview  # Preview changes only"
            echo "  ./scripts/ai_commit.sh --undo           # Undo last commit"
            echo "  ./scripts/ai_commit.sh \"msg\" --signoff  # Add DCO sign-off"
            echo "  ./scripts/ai_commit.sh --status         # Project status overview"
            echo "  ./scripts/ai_commit.sh --branch TASK-123 \"add feature\"  # Create task branch"
            echo "  ./scripts/ai_commit.sh --finish         # Finish current PR"
            echo "  ./scripts/ai_commit.sh --pr-check       # Check if PR required"
            exit 0
            ;;
        *) [[ -z "$COMMIT_MSG" ]] && COMMIT_MSG="$arg" ;;
    esac
    i=$((i+1))
done

# Get the project root (where .git is)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")

echo -e "${YELLOW}🤖 AI Commit Workflow${NC}"
if [[ "$DRY_RUN" == "true" ]]; then
    echo -e "${BLUE}   (DRY RUN - no changes will be made)${NC}"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Early detached HEAD check — prevents all modes from running in bad state
if [[ -z "$CURRENT_BRANCH" && "$STATUS" != "true" ]]; then
    echo -e "${RED}✗ Detached HEAD state — cannot proceed${NC}"
    echo -e "${YELLOW}Fix: git checkout main${NC}"
    exit 1
fi

# Push-only mode: delegate to safe_push.sh for retry logic + divergence detection (TASK-902)
if [[ "$PUSH_ONLY" == "true" ]]; then
    echo -e "${YELLOW}→ Push-only mode: routing through safe_push.sh...${NC}"
    exec "$PROJECT_ROOT/scripts/safe_push.sh" "--push-only"
fi

# Undo mode: soft-reset the last commit (keeps changes staged)
if [[ "$UNDO" == "true" ]]; then
    echo -e "${YELLOW}→ Undo mode: soft-resetting last commit...${NC}"
    # Safety: refuse if already pushed
    git fetch origin "$CURRENT_BRANCH" --quiet 2>/dev/null || true
    LOCAL_HEAD=$(git rev-parse HEAD)
    REMOTE_HEAD=$(git rev-parse "origin/$CURRENT_BRANCH" 2>/dev/null || echo "none")
    if [[ "$REMOTE_HEAD" != "none" ]]; then
        # Check if HEAD is reachable from remote
        if git merge-base --is-ancestor HEAD "origin/$CURRENT_BRANCH" 2>/dev/null; then
            echo -e "${RED}✗ Cannot undo — this commit is already pushed to remote${NC}"
            echo -e "${YELLOW}💡 Use --amend instead to modify the pushed commit${NC}"
            exit 1
        fi
    fi
    LAST_MSG=$(git log -1 --format="%s")
    git reset --soft HEAD~1
    echo -e "${GREEN}✓ Undid commit: $LAST_MSG${NC}"
    echo -e "${GREEN}  Changes are back in your working tree (staged)${NC}"
    exit 0
fi

# Amend mode: add staged changes to the last commit and push
if [[ "$AMEND" == "true" ]]; then
    # TASK-901: Block --amend on protected branches
    if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "develop" || "$CURRENT_BRANCH" =~ ^release/ ]]; then
        echo -e "${RED}✗ Cannot --amend on protected branch '$CURRENT_BRANCH'${NC}"
        echo -e "${YELLOW}  Use a task branch: ./scripts/ai_commit.sh --branch TASK-XXX 'desc'${NC}"
        exit 1
    fi
    echo -e "${YELLOW}→ Amend mode: updating last commit...${NC}"
    git add -A
    if [[ -z $(git status --porcelain) ]] && [[ -z "$COMMIT_MSG" ]]; then
        echo -e "${GREEN}✓ Nothing to amend${NC}"
        exit 0
    fi
    if [[ -n "$COMMIT_MSG" ]]; then
        git commit --amend -m "$COMMIT_MSG"
    else
        git commit --amend --no-edit
    fi
    echo -e "${GREEN}✓ Commit amended: $(git log -1 --oneline)${NC}"
    echo "→ Pushing amended commit..."
    export SAFE_PUSH_ACTIVE=1
    if git push --force-with-lease; then
        echo -e "${GREEN}✓ Successfully pushed amended commit!${NC}"
    else
        echo -e "${RED}✗ Push failed (remote may have new commits)${NC}"
        exit 1
    fi
    exit 0
fi

# Status mode: show full project state and exit
if [[ "$STATUS" == "true" ]]; then
    echo -e "${BLUE}📊 Project Status${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "Branch:    ${GREEN}$(git branch --show-current)${NC}"
    DIRTY=$(git status --porcelain | wc -l | tr -d ' ')
    echo -e "Dirty files: $DIRTY"
    AHEAD=$(git rev-list --count origin/$(git branch --show-current)..HEAD 2>/dev/null || echo "?")
    echo -e "Unpushed:  $AHEAD commit(s)"
    STASH_COUNT=$(git stash list 2>/dev/null | wc -l | tr -d ' ')
    echo -e "Stashes:   $STASH_COUNT"
    # Check for interrupted --finish (TASK-904)
    if [[ -f ".git/FINISH_STATE" ]]; then
        FINISH_PR=$(grep "^PR_NUMBER=" ".git/FINISH_STATE" | cut -d= -f2)
        FINISH_STAGE=$(grep "^STAGE=" ".git/FINISH_STATE" | cut -d= -f2)
        echo -e "${YELLOW}⚠ Interrupted --finish: PR #$FINISH_PR (stage: $FINISH_STAGE)${NC}"
        echo -e "  Resume: ./scripts/ai_commit.sh --continue $FINISH_PR"
    fi
    if command -v gh &>/dev/null; then
        echo ""
        echo "Open PRs:"
        gh pr list --author @me --limit 5 2>/dev/null || echo "  (unable to fetch)"
    fi
    exit 0
fi

# Branch mode: create task branch, delegate to create_task_pr.sh
if [[ "$BRANCH_MODE" == "true" ]]; then
    TASK_ID="$BRANCH_TASK_ID"
    BRANCH_DESC="$BRANCH_DESCRIPTION"
    if [[ -z "$TASK_ID" || -z "$BRANCH_DESC" ]]; then
        echo -e "${RED}✗ Usage: ai_commit.sh --branch TASK-XXX \"description\"${NC}"
        exit 1
    fi
    exec "$PROJECT_ROOT/scripts/create_task_pr.sh" "$TASK_ID" "$BRANCH_DESC"
fi

# Finish mode: auto-detect task ID from branch, delegate to finish_task_pr.sh
if [[ "$FINISH_MODE" == "true" ]]; then
    CURRENT_BRANCH=$(git branch --show-current)
    if [[ "$CURRENT_BRANCH" =~ ^task/(.+)$ ]]; then
        TASK_ID="${BASH_REMATCH[1]}"
    else
        echo -e "${RED}✗ Not on a task/* branch. Current: $CURRENT_BRANCH${NC}"
        echo "Create one first: ./scripts/ai_commit.sh --branch TASK-XXX \"description\""
        exit 1
    fi
    FINISH_DESC="${FINISH_DESCRIPTION:-$TASK_ID}"
    exec "$PROJECT_ROOT/scripts/finish_task_pr.sh" "$TASK_ID" "$FINISH_DESC" --wait --force
fi

# Continue mode: resume CI polling + merge for existing PR
if [[ -n "$CONTINUE_PR" ]]; then
    if [[ ! "$CONTINUE_PR" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}✗ Usage: ai_commit.sh --continue PR_NUMBER${NC}"
        exit 1
    fi
    exec "$PROJECT_ROOT/scripts/finish_task_pr.sh" --continue "$CONTINUE_PR"
fi

# PR check mode: check if PR is required
if [[ "$PR_CHECK" == "true" ]]; then
    exec "$PROJECT_ROOT/scripts/should_use_pr.sh" --explain
fi

# Check if we have uncommitted changes
if [[ -z $(git status --porcelain) ]]; then
    echo -e "${GREEN}✓ Working tree clean - nothing to commit${NC}"
    # Hint about --push if there are un-pushed commits
    git fetch origin "$CURRENT_BRANCH" --quiet 2>/dev/null || true
    LOCAL_HEAD=$(git rev-parse HEAD)
    REMOTE_HEAD=$(git rev-parse "origin/$CURRENT_BRANCH" 2>/dev/null || echo "none")
    if [[ "$LOCAL_HEAD" != "$REMOTE_HEAD" && "$REMOTE_HEAD" != "none" ]]; then
        AHEAD=$(git rev-list --count "origin/$CURRENT_BRANCH"..HEAD 2>/dev/null || echo "0")
        if [[ "$AHEAD" -gt 0 ]]; then
            echo -e "${YELLOW}💡 You have $AHEAD unpushed commit(s). Use: ./scripts/ai_commit.sh --push${NC}"
        fi
    fi
    exit 0
fi

# Get commit message (default if not provided)
if [[ -z "$COMMIT_MSG" ]]; then
    COMMIT_MSG="chore: AI-generated changes"
fi

echo "📝 Commit message: $COMMIT_MSG"
echo ""

# Stage all changes
echo "→ Staging changes..."
git add -A

# Enforce PR-first workflow decision (unless --force is used)
SHOULD_USE_PR_SCRIPT="$PROJECT_ROOT/scripts/should_use_pr.sh"
if [[ "$FORCE" == "true" ]]; then
    echo ""
    echo -e "${YELLOW}→ --force flag: Bypassing PR requirement check${NC}"
    echo "  (Use this for batching multiple commits, PR at end)"
elif [[ "$CURRENT_BRANCH" =~ ^task/ ]]; then
    echo ""
    echo -e "${GREEN}→ On task branch — PR workflow already in progress${NC}"
elif [[ -f "$SHOULD_USE_PR_SCRIPT" ]]; then
    echo ""
    echo "→ Checking whether a PR is required..."
    if ! "$SHOULD_USE_PR_SCRIPT" --explain --staged-only; then
        if [[ "$CURRENT_BRANCH" == "main" ]]; then
            echo ""
            echo -e "${RED}✗ PR required. Create a task branch first:${NC}"
            echo "  ./scripts/create_task_pr.sh TASK-XXX \"description\""
            echo ""
            echo -e "${YELLOW}TIP: Use --force to bypass for batched commits:${NC}"
            echo "  ./scripts/ai_commit.sh \"message\" --force"
            exit 1
        fi
        echo ""
        echo -e "${YELLOW}⚠ PR required (continuing on branch: $CURRENT_BRANCH)${NC}"
        echo "Remember to open/finish a PR with:"
        echo "  ./scripts/finish_task_pr.sh TASK-XXX \"description\""
    fi
fi

# Show what will be committed
echo ""
echo "Files to commit:"
git status --short
echo ""

# Preview mode: show staged diff without committing
if [[ "$PREVIEW" == "true" ]]; then
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}PREVIEW — Changes to be committed:${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    git diff --cached --stat
    echo ""
    git diff --cached --color
    echo ""
    echo -e "${GREEN}✓ Preview complete — no commit made${NC}"
    echo -e "${YELLOW}💡 Remove --preview to commit these changes${NC}"
    git reset HEAD >/dev/null 2>&1
    exit 0
fi

# Dry run mode: show what would happen and exit
if [[ "$DRY_RUN" == "true" ]]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}DRY RUN SUMMARY${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "Branch: ${GREEN}$CURRENT_BRANCH${NC}"
    echo -e "Message: ${GREEN}$COMMIT_MSG${NC}"
    echo ""
    echo "What would happen:"
    echo "  1. Stage all changes"
    echo "  2. Run pre-commit hooks"
    echo "  3. Create commit"
    echo "  4. Pull latest from remote"
    echo "  5. Push to origin"
    echo ""
    echo -e "${GREEN}✓ Dry run complete - no changes made${NC}"
    # Unstage the changes we staged for preview
    git reset HEAD >/dev/null 2>&1
    exit 0
fi

# Pre-flight: auto-format Python files to prevent CI failures
# This eliminates the #1 source of CI rework (black/ruff formatting)
STAGED_PY=$(git diff --cached --name-only --diff-filter=d | grep '\.py$' || true)
if [[ -n "$STAGED_PY" ]]; then
    echo -e "${YELLOW}→ Pre-flight: formatting Python files...${NC}"
    if [[ -f "$PROJECT_ROOT/.venv/bin/python" ]]; then
        echo "$STAGED_PY" | xargs "$PROJECT_ROOT/.venv/bin/python" -m black --quiet 2>&1 || echo -e "  ${YELLOW}⚠ black formatting had issues (non-fatal)${NC}"
        echo "$STAGED_PY" | xargs "$PROJECT_ROOT/.venv/bin/python" -m ruff check --fix --quiet 2>&1 || echo -e "  ${YELLOW}⚠ ruff fix had issues (non-fatal)${NC}"
        # Re-stage only the formatted files (not git add -A which sweeps in everything)
        echo "$STAGED_PY" | xargs git add
        echo -e "${GREEN}  ✓ Python files formatted${NC}"
    else
        echo -e "  ${YELLOW}⚠ .venv not found — skipping pre-flight formatting${NC}"
    fi
fi

# Pre-commit hooks verification
if [[ ! -f "$PROJECT_ROOT/.git/hooks/pre-commit" ]]; then
    echo -e "${YELLOW}⚠ pre-commit hooks not installed — run: pre-commit install${NC}"
fi

# Use the safe_push.sh script
SAFE_PUSH_SCRIPT="$PROJECT_ROOT/scripts/safe_push.sh"

if [[ ! -f "$SAFE_PUSH_SCRIPT" ]]; then
    echo -e "${RED}✗ ERROR: safe_push.sh not found at $SAFE_PUSH_SCRIPT${NC}"
    echo "This script requires safe_push.sh to function."
    exit 1
fi

# Make sure it's executable
chmod +x "$SAFE_PUSH_SCRIPT"

# Call safe_push.sh with the commit message
echo -e "${YELLOW}→ Running safe_push.sh workflow...${NC}"
if [[ "$SIGNOFF" == "true" ]]; then
    "$SAFE_PUSH_SCRIPT" "$COMMIT_MSG" --signoff
else
    "$SAFE_PUSH_SCRIPT" "$COMMIT_MSG"
fi

# Check exit code
if [[ $? -eq 0 ]]; then
    echo ""
    echo -e "${GREEN}✓ Successfully committed and pushed!${NC}"

    # Show commit statistics
    echo ""
    echo -e "${BLUE}📊 Commit Statistics:${NC}"
    git diff --stat HEAD~1 HEAD 2>/dev/null || true

    # Post-commit: check if doc numbers are stale (non-blocking)
    SYNC_SCRIPT="$PROJECT_ROOT/scripts/sync_numbers.py"
    VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"
    if [[ -f "$SYNC_SCRIPT" && -f "$VENV_PYTHON" ]]; then
        STALE=$("$VENV_PYTHON" "$SYNC_SCRIPT" --json 2>/dev/null | "$VENV_PYTHON" -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('updates',[])))" 2>/dev/null || echo "0")
        if [[ "$STALE" -gt 0 ]]; then
            echo -e "  ${YELLOW}⚠${NC} $STALE doc number(s) are stale — run: .venv/bin/python scripts/sync_numbers.py --fix"
        fi
    fi

    # Post-commit: check for broken links if docs/scripts were moved/renamed (non-blocking)
    LINK_SCRIPT="$PROJECT_ROOT/scripts/check_links.py"
    if [[ -f "$LINK_SCRIPT" && -f "$VENV_PYTHON" ]]; then
        # Check if any files were renamed or deleted in this commit
        MOVED=$(git diff --name-status HEAD~1 HEAD 2>/dev/null | grep -c "^[RD]" 2>/dev/null || true)
        MOVED=${MOVED:-0}
        if [[ "$MOVED" -gt 0 ]]; then
            BROKEN=$("$VENV_PYTHON" "$LINK_SCRIPT" 2>/dev/null | grep -c "BROKEN\|❌" 2>/dev/null || true)
            BROKEN=${BROKEN:-0}
            if [[ "$BROKEN" -gt 0 ]]; then
                echo -e "  ${YELLOW}⚠${NC} $BROKEN broken link(s) detected after file move — run: .venv/bin/python scripts/check_links.py --fix"
            fi
        fi
    fi

    # Task branch reminder
    if [[ "$CURRENT_BRANCH" =~ ^task/ ]]; then
        TASK_ID="${CURRENT_BRANCH#task/}"
        echo ""
        echo -e "${YELLOW}💡 On task branch — when done, finish the PR:${NC}"
        echo "  ./scripts/finish_task_pr.sh $TASK_ID 'description' --wait"
    fi

    # Stale auto-stash check (warn + offer cleanup)
    STALE_STASH_COUNT=$(git stash list 2>/dev/null | grep -c "auto-stash" || true)
    if [[ "$STALE_STASH_COUNT" -gt 3 ]]; then
        echo -e "  ${YELLOW}⚠${NC} $STALE_STASH_COUNT stale auto-stash entries"
        echo -e "  ${DIM}Review: git stash list${NC}"
        echo -e "  ${DIM}Cleanup old ones: git stash drop stash@{N}${NC}"
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo ""
    echo -e "${RED}✗ Push failed - please check the error above${NC}"
    exit 1
fi
