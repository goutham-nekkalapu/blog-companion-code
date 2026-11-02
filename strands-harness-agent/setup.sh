#!/usr/bin/env bash
# Bootstrap a virtualenv and install the harness + tools.
# Usage: ./setup.sh
set -euo pipefail

cd "$(dirname "$0")"

# Strands requires Python 3.10+. Pick the first suitable interpreter we find,
# preferring an explicit $PYTHON override, then newest-to-oldest.
find_python() {
  for candidate in "${PYTHON:-}" python3.13 python3.12 python3.11 python3.10 python3; do
    [ -z "$candidate" ] && continue
    command -v "$candidate" >/dev/null 2>&1 || continue
    if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

PYTHON="$(find_python)" || {
  echo "ERROR: need Python 3.10+ but none was found." >&2
  echo "Install Python 3.10+ or set PYTHON=/path/to/python before running." >&2
  exit 1
}

echo "==> Using $("$PYTHON" --version) ($PYTHON)"
echo "==> Creating virtualenv in .venv"
"$PYTHON" -m venv .venv

echo "==> Upgrading pip"
./.venv/bin/pip install --quiet --upgrade pip

echo "==> Installing dependencies from requirements.txt"
./.venv/bin/pip install --quiet -r requirements.txt

# pytest is used by the demo task so the agent can run its own tests.
echo "==> Installing pytest (used by the demo coding task)"
./.venv/bin/pip install --quiet pytest

cat <<'EOF'

Done. Next steps:

  1. Activate the environment:
       source .venv/bin/activate

  2. Set your Anthropic API key (or copy .env.example to .env):
       export ANTHROPIC_API_KEY=sk-ant-...

  3. Run the agent:
       python agent.py
       python agent.py "Create a palindrome checker with tests and run them."

EOF
