#!/bin/sh
# Install constutil's shared skill into the current project or your home directory.
set -eu

usage() {
    echo 'Usage: sh install-skills.sh {codex|claude|both} [--global] [--force]'
}

target=both
scope=project
force=false
if [ "$#" -gt 0 ]; then
    case "$1" in
        codex|claude|both) target=$1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) usage >&2; exit 2 ;;
    esac
fi
for option in "$@"; do
    case "$option" in
        --global) scope=global ;;
        --force) force=true ;;
        *) usage >&2; exit 2 ;;
    esac
done

root=$PWD
if [ "$scope" = global ]; then
    root=${HOME:?HOME is required for --global}
fi
# Check every requested destination before making any changes.
check_destination() {
    if [ -e "$1" ] || [ -L "$1" ]; then
        if [ -L "$1" ] || [ ! -d "$1" ]; then
            echo "Refusing non-directory or symlink destination: $1" >&2
            exit 1
        fi
        if [ "$force" != true ]; then
            echo "Already exists: $1 (use --force to update)" >&2
            exit 1
        fi
        for file in SKILL.md agents agents/openai.yaml; do
            if [ -L "$1/$file" ]; then
                echo "Refusing symlink: $1/$file" >&2
                exit 1
            fi
        done
    fi
}
case "$target" in codex|both) check_destination "$root/.agents/skills/constutil" ;; esac
case "$target" in claude|both) check_destination "$root/.claude/skills/constutil" ;; esac

staging=$(mktemp -d)
trap 'rm -rf "$staging"' EXIT
trap 'exit 1' HUP INT TERM
mkdir -p "$staging/agents"
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
source_dir="$script_dir/../skills/constutil"
if [ -f "$source_dir/SKILL.md" ] && [ -f "$source_dir/agents/openai.yaml" ]; then
    cp "$source_dir/SKILL.md" "$staging/SKILL.md"
    cp "$source_dir/agents/openai.yaml" "$staging/agents/openai.yaml"
else
    command -v curl >/dev/null 2>&1 || { echo 'curl is required' >&2; exit 1; }
    base=https://constutil.patchfork.dev/skills/constutil
    curl --fail --silent --show-error --location "$base/SKILL.md" -o "$staging/SKILL.md"
    curl --fail --silent --show-error --location "$base/agents/openai.yaml" -o "$staging/agents/openai.yaml"
fi
[ -s "$staging/SKILL.md" ] && [ -s "$staging/agents/openai.yaml" ] || {
    echo 'Skill files are empty; nothing installed.' >&2
    exit 1
}
install_to() {
    mkdir -p "$1/agents"
    cp "$staging/SKILL.md" "$1/SKILL.md"
    cp "$staging/agents/openai.yaml" "$1/agents/openai.yaml"
    echo "Installed constutil skill: $1"
}
case "$target" in codex|both) install_to "$root/.agents/skills/constutil" ;; esac
case "$target" in claude|both) install_to "$root/.claude/skills/constutil" ;; esac
echo 'Use $constutil in Codex or /constutil in Claude Code.'
