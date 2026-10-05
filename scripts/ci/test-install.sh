#!/bin/bash
# End-to-end test of install.sh, run by .github/workflows/install.yml.
#
# Installs into an empty HOME (no shell profile files, no Documents folder)
# with a minimal environment, the way a new user's Mac looks. Then checks
# the result from fresh login shells, the way Terminal and Claude see it.
#
# Usage: scripts/ci/test-install.sh
# Env:   JOBBING_REPO  git URL or path to install from (default: this checkout)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPO="${JOBBING_REPO:-$REPO_ROOT}"
TEST_HOME="$(mktemp -d)/home"
mkdir -p "$TEST_HOME"
# Resolve symlinks (/var -> /private/var on macOS) so paths compare equal.
TEST_HOME="$(cd "$TEST_HOME" && pwd -P)"
INSTALL_DIR="$TEST_HOME/Documents/jobbing-skills"

step() { printf '\n=== %s\n' "$*"; }
fail() { printf '\nFAIL: %s\n' "$*" >&2; exit 1; }

# A clean environment: no PATH entries for Homebrew, no user profile.
clean_env=(env -i HOME="$TEST_HOME" USER="$USER" SHELL=/bin/zsh TERM=xterm-256color CI=true)
run_installer() {
    "${clean_env[@]}" PATH=/usr/bin:/bin:/usr/sbin:/sbin JOBBING_REPO="$REPO" \
        /bin/bash -c "$(cat "$REPO_ROOT/install.sh")" -- "$@"
}
login_shell() { "${clean_env[@]}" /bin/zsh -lc "$1"; }

step "Install (piped, as the README one-liner runs it)"
run_installer

step "Profile files were created with one PATH block each"
for f in .zprofile .zshrc; do
    [[ -f "$TEST_HOME/$f" ]] || fail "$f was not created"
    n="$(grep -c '>>> jobbing-skills >>>' "$TEST_HOME/$f")"
    [[ "$n" == 1 ]] || fail "$f has $n PATH blocks, expected 1"
done

step "A new interactive login shell (Terminal) finds jobbing and brew"
"${clean_env[@]}" /bin/zsh -lic 'command -v jobbing && command -v brew' ||
    fail "jobbing or brew not on PATH in a new Terminal shell"

step "A non-interactive login shell (Claude's tool shell) finds jobbing"
login_shell 'command -v jobbing' || fail "jobbing not on PATH for Claude"

step "jobbing home is the Documents folder"
home="$(login_shell 'jobbing home')"
[[ "$home" == "$INSTALL_DIR" ]] || fail "jobbing home is '$home', expected '$INSTALL_DIR'"

step "Workspace files exist"
for f in CONTEXT.md BOOKMARKS.md applications scan_results; do
    [[ -e "$INSTALL_DIR/$f" ]] || fail "$f missing"
done

step "jobbing browse fetches a page with the headless browser"
login_shell 'jobbing browse https://example.com' | grep -q '"title": "Example Domain"' ||
    fail "browse did not return Example Domain"

step "jobbing pdf makes a CV and a cover letter"
login_shell 'cd ~/Documents/jobbing-skills &&
    mkdir -p applications/Acme-Corp &&
    jobbing example > applications/Acme-Corp/Acme-Corp.json &&
    jobbing pdf "Acme Corp"'
for f in ACME-CORP-CV.pdf ACME-CORP-CL.pdf; do
    head -c 4 "$INSTALL_DIR/applications/Acme-Corp/$f" | grep -q '%PDF' || fail "$f is not a PDF"
done

step "A second run succeeds and keeps the user's files"
echo "my profile" > "$INSTALL_DIR/CONTEXT.md"
run_installer --no-browser
[[ "$(cat "$INSTALL_DIR/CONTEXT.md")" == "my profile" ]] || fail "CONTEXT.md was overwritten"
for f in .zprofile .zshrc; do
    n="$(grep -c '>>> jobbing-skills >>>' "$TEST_HOME/$f")"
    [[ "$n" == 1 ]] || fail "after re-run, $f has $n PATH blocks"
done

printf '\nPASS: install.sh end-to-end\n'
