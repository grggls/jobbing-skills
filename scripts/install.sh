#!/usr/bin/env bash
# install.sh — set up Jobbing on macOS or Linux. Safe to run again.
#
# Usage: scripts/install.sh [--dev] [--no-browser]
#   --dev         also install test/lint tools and the pre-commit hook
#   --no-browser  skip Playwright + Chromium (jobbing browse / scan fetch
#                 will not work; everything else will)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DEV=0
BROWSER=1
for arg in "$@"; do
    case "$arg" in
        --dev) DEV=1 ;;
        --no-browser) BROWSER=0 ;;
        *) echo "Unknown option: $arg" >&2; exit 2 ;;
    esac
done

ok()   { printf '\033[0;32m✓\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!\033[0m %s\n' "$*"; }
fail() { printf '\033[0;31m✗\033[0m %s\n' "$*" >&2; exit 1; }

echo "Jobbing setup — $REPO_ROOT"
echo

# 1. Python environment ------------------------------------------------------
# requires-python >= 3.14. macOS ships 3.9, so prefer uv, which fetches a
# suitable Python by itself.

EXTRAS="browser"
[[ "$BROWSER" == 0 ]] && EXTRAS=""
[[ "$DEV" == 1 ]] && EXTRAS="${EXTRAS:+$EXTRAS,}dev"
SPEC="."
[[ -n "$EXTRAS" ]] && SPEC=".[$EXTRAS]"

if command -v uv >/dev/null 2>&1; then
    [[ -x .venv/bin/python ]] || uv venv --quiet --python 3.14 .venv
    uv pip install --quiet --python .venv/bin/python -e "$SPEC"
    ok "Python package installed with uv"
else
    PY=""
    for cand in python3.14 python3; do
        if command -v "$cand" >/dev/null 2>&1 &&
           "$cand" -c 'import sys; sys.exit(sys.version_info < (3, 14))'; then
            PY="$cand"; break
        fi
    done
    if [[ -z "$PY" ]]; then
        fail "Need Python 3.14+ or uv. Install uv: 'brew install uv' (or see https://docs.astral.sh/uv/), then run this script again."
    fi
    [[ -x .venv/bin/python ]] || "$PY" -m venv .venv
    .venv/bin/pip install --quiet --upgrade pip
    .venv/bin/pip install --quiet -e "$SPEC"
    ok "Python package installed with $PY"
fi

# 2. Headless browser ----------------------------------------------------------

if [[ "$BROWSER" == 1 ]]; then
    .venv/bin/python -m playwright install chromium >/dev/null
    ok "Chromium installed for jobbing browse / scan fetch"
else
    warn "Skipped Playwright (--no-browser)"
fi

# 3. Put `jobbing` on PATH ---------------------------------------------------
# Claude Code runs commands in a plain shell without the venv, so the CLI
# must be on PATH. Link it into ~/.local/bin.

BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
ln -sf "$REPO_ROOT/.venv/bin/jobbing" "$BIN_DIR/jobbing"
if command -v jobbing >/dev/null 2>&1 && [[ "$(command -v jobbing)" == "$BIN_DIR/jobbing" ]]; then
    ok "jobbing is on PATH ($BIN_DIR/jobbing)"
else
    warn "$BIN_DIR is not on your PATH. Add this line to ~/.zshrc (or ~/.bashrc), then open a new terminal:"
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

# 4. Dev hook ----------------------------------------------------------------

if [[ "$DEV" == 1 ]]; then
    .venv/bin/pre-commit install >/dev/null
    ok "pre-commit hook installed"
fi

# 5. Workspace files ---------------------------------------------------------

echo
JOBBING_HOME="${JOBBING_HOME:-$REPO_ROOT}" "$REPO_ROOT/.venv/bin/jobbing" init
echo

# 6. Tools the user installs -------------------------------------------------

if command -v claude >/dev/null 2>&1; then
    ok "Claude Code found"
else
    warn "Claude Code not found. Install it: https://claude.com/claude-code"
fi

cat <<EOF

Next steps
  1. Fill in CONTEXT.md (your profile). Claude can help: paste your CV into
     Claude and ask it to fill in the template.
  2. Replace the example links in BOOKMARKS.md with your job boards.
  3. Connect Notion to Claude: in the Claude app, Settings -> Connectors ->
     Notion (in Claude Code you can also type /mcp).
  4. Start Claude Code in this folder and say "set up my Notion tracker":
       cd "$REPO_ROOT" && claude
EOF
