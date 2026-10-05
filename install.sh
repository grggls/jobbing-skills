#!/bin/bash
# jobbing-skills installer for macOS (and Linux with Homebrew).
#
# Run it from anywhere. It needs nothing installed first:
#
#   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/grggls/jobbing-skills/main/install.sh)"
#
# It installs Homebrew (if missing), git, Python 3.14, and uv; downloads
# jobbing-skills into ~/Documents/jobbing-skills; installs the `jobbing`
# command; and sets up PATH for you. Safe to run again (that is also how
# you update).
#
# Options (append after the URL as: ... install.sh)" -- --no-browser):
#   --no-browser   skip the headless browser (job-board fetching won't work)
#   --dev          also install test/lint tools and the pre-commit hook
#
# Environment overrides:
#   JOBBING_DIR    install location (default: ~/Documents/jobbing-skills)
#   JOBBING_REPO   git URL to clone (default: the GitHub repo)

set -euo pipefail

REPO_URL="${JOBBING_REPO:-https://github.com/grggls/jobbing-skills.git}"
INSTALL_DIR="${JOBBING_DIR:-$HOME/Documents/jobbing-skills}"
DEV=0
BROWSER=1
for arg in "$@"; do
    case "$arg" in
        --dev) DEV=1 ;;
        --no-browser) BROWSER=0 ;;
        --) ;;
        *) echo "Unknown option: $arg" >&2; exit 2 ;;
    esac
done

bold() { printf '\n\033[1m%s\033[0m\n' "$*"; }
ok()   { printf '  \033[0;32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[1;33m!\033[0m %s\n' "$*"; }
fail() { printf '\n\033[0;31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

echo "jobbing-skills installer"
echo "Install folder: $INSTALL_DIR"

# --- 1. Homebrew --------------------------------------------------------------

find_brew() {
    local candidate
    for candidate in "$(command -v brew 2>/dev/null || true)" \
        /opt/homebrew/bin/brew /usr/local/bin/brew /home/linuxbrew/.linuxbrew/bin/brew; do
        if [[ -n "$candidate" && -x "$candidate" ]]; then
            echo "$candidate"
            return 0
        fi
    done
    return 1
}

bold "1/6  Homebrew"
if BREW="$(find_brew)"; then
    ok "Homebrew found ($BREW)"
else
    echo "  Homebrew is not installed. Installing it now."
    echo "  It may ask for your Mac password (the one you use to log in)."
    echo "  Nothing shows on screen while you type it. That is normal."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    BREW="$(find_brew)" || fail "Homebrew did not install. Scroll up for its error message."
    ok "Homebrew installed"
fi
eval "$("$BREW" shellenv)"

# --- 2. git, Python, uv -------------------------------------------------------

bold "2/6  git, Python 3.14, uv"
for formula in git python@3.14 uv; do
    if brew list --formula "$formula" >/dev/null 2>&1; then
        ok "$formula already installed"
    else
        brew install --quiet "$formula"
        ok "$formula installed"
    fi
done

# --- 3. jobbing-skills --------------------------------------------------------

bold "3/6  jobbing-skills"
SCRIPT_DIR=""
if [[ -n "${BASH_SOURCE[0]:-}" && -f "${BASH_SOURCE[0]}" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

if [[ -n "$SCRIPT_DIR" && -f "$SCRIPT_DIR/pyproject.toml" && -d "$SCRIPT_DIR/.claude/skills" ]]; then
    # Run from inside a clone: install that clone.
    INSTALL_DIR="$SCRIPT_DIR"
    ok "Using this folder ($INSTALL_DIR)"
elif [[ -d "$INSTALL_DIR/.git" ]]; then
    git -C "$INSTALL_DIR" pull --ff-only --quiet
    ok "Updated $INSTALL_DIR"
elif [[ -e "$INSTALL_DIR" && -n "$(ls -A "$INSTALL_DIR" 2>/dev/null)" ]]; then
    fail "$INSTALL_DIR exists and is not a jobbing-skills download. Move it away, or set JOBBING_DIR to another folder."
else
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone --quiet "$REPO_URL" "$INSTALL_DIR"
    ok "Downloaded to $INSTALL_DIR"
fi
cd "$INSTALL_DIR"

# --- 4. The jobbing command ---------------------------------------------------

bold "4/6  The jobbing command"
EXTRAS="browser"
[[ "$BROWSER" == 0 ]] && EXTRAS=""
[[ "$DEV" == 1 ]] && EXTRAS="${EXTRAS:+$EXTRAS,}dev"
SPEC="."
[[ -n "$EXTRAS" ]] && SPEC=".[$EXTRAS]"

[[ -x .venv/bin/python ]] || uv venv --quiet --python 3.14 .venv
uv pip install --quiet --python .venv/bin/python -e "$SPEC"
ok "Installed"

if [[ "$BROWSER" == 1 ]]; then
    echo "  Downloading the headless browser (about 100 MB)..."
    .venv/bin/python -m playwright install chromium >/dev/null
    ok "Headless browser installed"
fi
if [[ "$DEV" == 1 ]]; then
    .venv/bin/pre-commit install >/dev/null
    ok "pre-commit hook installed"
fi

# --- 5. PATH (so Terminal and Claude can find `jobbing` and `brew`) -----------

bold "5/6  Shell setup"
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
ln -sf "$INSTALL_DIR/.venv/bin/jobbing" "$BIN_DIR/jobbing"

BEGIN_MARK="# >>> jobbing-skills >>>"
END_MARK="# <<< jobbing-skills <<<"
BLOCK="$BEGIN_MARK
# Added by the jobbing-skills installer. Safe to keep.
eval \"\$($BREW shellenv)\"
export PATH=\"\$HOME/.local/bin:\$PATH\"
$END_MARK"

# Write the block to the files your shell reads at start-up. Create a file
# if it does not exist. Replace an old block instead of adding a second one.
profiles=("$HOME/.zprofile" "$HOME/.zshrc")
case "${SHELL:-}" in
    */bash) profiles+=("$HOME/.bash_profile" "$HOME/.bashrc") ;;
esac
for profile in "${profiles[@]}"; do
    touch "$profile"
    if grep -qF "$BEGIN_MARK" "$profile"; then
        tmp="$(mktemp)"
        awk -v b="$BEGIN_MARK" -v e="$END_MARK" '
            $0 == b {skip = 1; next}
            $0 == e {skip = 0; next}
            !skip {print}
        ' "$profile" > "$tmp"
        cat "$tmp" > "$profile"
        rm -f "$tmp"
    fi
    printf '\n%s\n' "$BLOCK" >> "$profile"
    ok "Updated ${profile/#$HOME/~}"
done

# Check it the way a new Terminal window would.
login_shell="${SHELL:-/bin/zsh}"
[[ -x "$login_shell" ]] || login_shell=/bin/zsh
if env -i HOME="$HOME" USER="${USER:-}" SHELL="$login_shell" TERM=dumb \
    "$login_shell" -lic 'command -v jobbing' >/dev/null 2>&1; then
    ok "New Terminal windows will find the jobbing command"
else
    warn "Could not confirm PATH in a new shell. If 'jobbing' is not found, use: $INSTALL_DIR/.venv/bin/jobbing"
fi

# --- 6. Your private files ----------------------------------------------------

bold "6/6  Your files"
"$INSTALL_DIR/.venv/bin/jobbing" init | sed 's/^/  /'

if command -v claude >/dev/null 2>&1 || [[ -d "/Applications/Claude.app" ]]; then
    ok "Claude found"
else
    warn "Claude is not installed. Get the Claude app: https://claude.ai/download"
fi

cat <<EOF

────────────────────────────────────────────────────────────────
 Done. jobbing-skills is in: $INSTALL_DIR

 Next:
  1. Open the Claude app. Go to Settings → Connectors and connect Notion.
  2. In the Claude app, open the Code tab and choose the folder
     $INSTALL_DIR
     (or in Terminal: cd "$INSTALL_DIR" && claude)
  3. Say: "Help me fill in CONTEXT.md from my CV" and paste your CV.
  4. Say: "Set up my Notion tracker".
  5. Paste a job posting and say: "Analyze this job".
────────────────────────────────────────────────────────────────
EOF
