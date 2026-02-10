#!/bin/bash
# risk_cache.sh - File risk assessment caching library
# Reduces redundant analysis in should_use_pr.sh by caching risk scores
#
# Usage:
#   source scripts/risk_cache.sh
#   init_cache
#   risk=$(get_cached_risk "file.py") || risk=$(calculate_risk "file.py")
#   set_cached_risk "file.py" "$risk"

# Configuration
CACHE_DIR="${PROJECT_ROOT:-.}/.git/risk_cache"
CACHE_TTL=3600  # 1 hour (adjustable)
CACHE_VERSION="1.0"  # Invalidate cache when algorithm changes

# Initialize cache directory
init_cache() {
    mkdir -p "$CACHE_DIR"

    # Create version file
    if [[ ! -f "$CACHE_DIR/VERSION" ]] || [[ "$(cat "$CACHE_DIR/VERSION")" != "$CACHE_VERSION" ]]; then
        echo "$CACHE_VERSION" > "$CACHE_DIR/VERSION"
        # Clear old cache on version mismatch
        find "$CACHE_DIR" -type f ! -name "VERSION" -delete 2>/dev/null || true
    fi
}

# Generate cache key from file path and modification time
get_cache_key() {
    local file=$1

    # Get file modification time (seconds since epoch)
    local mtime
    if [[ -f "$file" ]]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            mtime=$(stat -f "%m" "$file" 2>/dev/null || echo "0")
        else
            # Linux
            mtime=$(stat -c "%Y" "$file" 2>/dev/null || echo "0")
        fi
    else
        mtime="0"
    fi

    # Generate SHA256 hash of file path + mtime
    echo "${file}:${mtime}" | shasum -a 256 | cut -d' ' -f1
}

# Check if cached risk assessment exists and is valid
get_cached_risk() {
    local file=$1
    local cache_key=$(get_cache_key "$file")
    local cache_file="${CACHE_DIR}/${cache_key}"

    # Check if cache file exists and is within TTL
    if [[ -f "$cache_file" ]]; then
        local cache_age
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            cache_age=$(($(date +%s) - $(stat -f "%m" "$cache_file")))
        else
            # Linux
            cache_age=$(($(date +%s) - $(stat -c "%Y" "$cache_file")))
        fi

        if [[ "$cache_age" -lt "$CACHE_TTL" ]]; then
            cat "$cache_file"
            return 0
        else
            # Cache expired
            rm -f "$cache_file"
        fi
    fi

    return 1
}

# Store risk assessment in cache
set_cached_risk() {
    local file=$1
    local risk=$2
    local cache_key=$(get_cache_key "$file")
    local cache_file="${CACHE_DIR}/${cache_key}"

    echo "$risk" > "$cache_file"
}

# Invalidate cache for specific file (on modification)
invalidate_cache() {
    local file=$1

    if [[ -z "$file" ]]; then
        return 0
    fi

    # Find all cache entries for this file (different mtimes)
    # Note: This is a best-effort cleanup; old entries will expire via TTL
    local file_pattern=$(echo "$file" | shasum -a 256 | cut -c1-8)
    find "$CACHE_DIR" -type f -name "${file_pattern}*" -delete 2>/dev/null || true
}

# Clean up old cache entries (run periodically)
cleanup_cache() {
    local age_days=${1:-1}  # Default: 1 day

    # Remove entries older than specified days
    find "$CACHE_DIR" -type f ! -name "VERSION" -mtime "+${age_days}" -delete 2>/dev/null || true

    # Report cleanup stats
    local cache_count=$(find "$CACHE_DIR" -type f ! -name "VERSION" | wc -l | tr -d ' ')
    echo "Cache cleanup complete. Entries remaining: $cache_count"
}

# Get cache statistics
cache_stats() {
    if [[ ! -d "$CACHE_DIR" ]]; then
        echo "Cache not initialized"
        return 1
    fi

    local total_entries=$(find "$CACHE_DIR" -type f ! -name "VERSION" | wc -l | tr -d ' ')
    local cache_size=$(du -sh "$CACHE_DIR" 2>/dev/null | cut -f1)
    local cache_version=$(cat "$CACHE_DIR/VERSION" 2>/dev/null || echo "unknown")

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Risk Cache Statistics"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Version: $cache_version"
    echo "Entries: $total_entries"
    echo "Size: $cache_size"
    echo "TTL: ${CACHE_TTL}s ($(($CACHE_TTL / 60)) minutes)"
    echo "Location: $CACHE_DIR"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Main command interface (if run directly)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-}" in
        init)
            init_cache
            echo "✓ Cache initialized: $CACHE_DIR"
            ;;
        stats)
            cache_stats
            ;;
        cleanup)
            cleanup_cache "${2:-1}"
            ;;
        invalidate)
            if [[ -z "${2:-}" ]]; then
                echo "Usage: $0 invalidate <file>"
                exit 1
            fi
            invalidate_cache "$2"
            echo "✓ Cache invalidated for: $2"
            ;;
        *)
            echo "Usage: $0 {init|stats|cleanup [days]|invalidate <file>}"
            echo ""
            echo "Commands:"
            echo "  init              - Initialize cache directory"
            echo "  stats             - Show cache statistics"
            echo "  cleanup [days]    - Remove entries older than N days (default: 1)"
            echo "  invalidate <file> - Invalidate cache for specific file"
            exit 1
            ;;
    esac
fi
