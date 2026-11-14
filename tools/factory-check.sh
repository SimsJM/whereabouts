#!/bin/sh
# The checks every change to this repository must pass.
#
# Cerebro runs this on a pull request's head, after the pack's install command. Agents run it
# before they hand off, and a person can run it the same way: `sh tools/factory-check.sh`.
# It is a protected path: changing it needs the maintainer's approval in the specification.
set -eu

fail() {
    echo "check failed: $1" >&2
    exit 1
}

# 1. Retired names stay retired (decision D-01). The decision log and this script may name them.
found=$(grep -rIil "rummage" . \
    --exclude-dir=.git --exclude-dir=.venv --exclude-dir=node_modules \
    --exclude=decision-log.md --exclude=factory-check.sh || true)
[ -z "$found" ] || fail "a retired product name appears in: $(echo "$found" | tr '\n' ' ')"

# 2. Until the application exists there is nothing to build or test. Say so plainly: this is
#    not a pass of any test.
if [ ! -f pyproject.toml ]; then
    echo "No application code yet (no pyproject.toml): only the repository checks ran."
    exit 0
fi

# 3. From the first line of application code on: lint, then tests. No tests is a failure.
PY=.venv/bin/python
[ -x "$PY" ] || fail "no virtual environment: run the pack's install command first"

"$PY" -m ruff --version >/dev/null 2>&1 || fail "ruff is not installed: add it to the development requirements"
"$PY" -m ruff check . || fail "ruff found problems"

"$PY" -m pytest --version >/dev/null 2>&1 || fail "pytest is not installed: add it to the development requirements"
set +e
"$PY" -m pytest -q
status=$?
set -e
[ "$status" -ne 5 ] || fail "no tests were collected: a change to the application needs tests"
[ "$status" -eq 0 ] || fail "tests failed"

echo "All checks passed."
