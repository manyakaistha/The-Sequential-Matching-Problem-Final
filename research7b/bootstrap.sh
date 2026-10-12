#!/usr/bin/env bash
# Setup only. No research module imports, simulations, tests, fits, or agent/provider calls.
set -euo pipefail
PACKAGE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
case "${1:-}" in
  "") INSTALL_DEPS=0 ;;
  --install-deps) INSTALL_DEPS=1 ;;
  *) printf '%s\n' 'Usage: bash bootstrap.sh [--install-deps]' >&2; exit 64 ;;
esac
"$PYTHON_BIN" "$PACKAGE_DIR/preflight.py" --integrity-only
if [[ ! -d "$PACKAGE_DIR/.venv" ]]; then
  "$PYTHON_BIN" -m venv "$PACKAGE_DIR/.venv"
fi
if [[ -x "$PACKAGE_DIR/.venv/bin/python" ]]; then
  VENV_PYTHON="$PACKAGE_DIR/.venv/bin/python"
elif [[ -x "$PACKAGE_DIR/.venv/Scripts/python.exe" ]]; then
  VENV_PYTHON="$PACKAGE_DIR/.venv/Scripts/python.exe"
else
  printf '%s\n' 'Virtual environment Python missing; repair manually.' >&2; exit 1
fi
if [[ "$INSTALL_DEPS" == 1 ]]; then
  "$VENV_PYTHON" -m pip install --requirement "$PACKAGE_DIR/requirements-research.lock.txt"
fi
printf '%s\n' 'Setup created/retained .venv. Research runtime is pending implementation; no experiments launched.'
if "$VENV_PYTHON" "$PACKAGE_DIR/preflight.py" --output "$PACKAGE_DIR/setup_outputs/preflight.json"; then
  printf '%s\n' 'Static/environment checks complete. This does not authorize phase execution.'
else
  STATUS=$?
  if [[ "$STATUS" != 2 ]]; then exit "$STATUS"; fi
  printf '%s\n' 'Environment prerequisites pending; see setup_outputs/preflight.json. Optional: bash bootstrap.sh --install-deps'
fi
