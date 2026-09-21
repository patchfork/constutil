#!/bin/sh
# Update package metadata and the lockfile without installing or publishing.
set -eu

usage() {
    cat <<'EOF'
Usage: sh scripts/bump-version.sh [--dry-run] major|minor|patch|VERSION

Examples:
  sh scripts/bump-version.sh patch
  sh scripts/bump-version.sh --dry-run minor
  sh scripts/bump-version.sh 1.2.0

Requires uv with the `uv version` command. Updates pyproject.toml and uv.lock.
Does not commit, tag, or publish. --dry-run previews without changing files.
EOF
}

dry_run=false
if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    usage
    exit 0
fi
if [ "${1:-}" = "--dry-run" ]; then
    dry_run=true
    shift
fi
if [ "$#" -ne 1 ]; then
    usage >&2
    exit 2
fi

case "$1" in
    major|minor|patch) set -- --bump "$1" ;;
    [0-9]*) ;; # uv validates and normalizes explicit Python package versions.
    *) usage >&2; exit 2 ;;
esac
if [ "$dry_run" = true ]; then
    set -- "$@" --dry-run
fi

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec uv version --project "$repo_root" --no-sync "$@"
