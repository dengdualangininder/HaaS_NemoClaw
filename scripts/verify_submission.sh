#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DB_PATH="$ROOT_DIR/runtime/verify_submission.db"

rm -f "$DB_PATH"
trap 'rm -f "$DB_PATH"' EXIT

cd "$ROOT_DIR"

echo "[1/4] unit tests"
python3 -m unittest discover -s tests -p 'test_*.py'

echo "[2/4] unattended offline demo"
demo_output="$(python3 main.py --db "$DB_PATH" demo --auto-answer)"
printf '%s\n' "$demo_output"

run_id="$(printf '%s\n' "$demo_output" | awk -F': ' '/^run_id:/ {print $2; exit}')"
if [[ -z "${run_id}" ]]; then
  echo "Failed to extract run_id from demo output." >&2
  exit 1
fi

echo "[3/4] final report"
python3 main.py --db "$DB_PATH" report --run-id "$run_id"

echo "[4/4] guardrail demo"
python3 main.py guardrail-demo

echo "Submission verification completed."
