#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
BUNDLE_DIR="$DIST_DIR/haas_nemoclaw_submission"

rm -rf "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR"

cp "$ROOT_DIR/README.md" "$BUNDLE_DIR/"
cp "$ROOT_DIR/README-NEMOCLAW-HANDOFF.md" "$BUNDLE_DIR/"
cp "$ROOT_DIR/NEMOCLAW_DEMO_RUNBOOK.md" "$BUNDLE_DIR/"
cp "$ROOT_DIR/SETUP.md" "$BUNDLE_DIR/"
cp "$ROOT_DIR/DEMO.md" "$BUNDLE_DIR/"
cp "$ROOT_DIR/ARCHITECTURE.md" "$BUNDLE_DIR/"
cp "$ROOT_DIR/SAFETY.md" "$BUNDLE_DIR/"
cp "$ROOT_DIR/SUBMISSION.md" "$BUNDLE_DIR/"
cp "$ROOT_DIR/main.py" "$BUNDLE_DIR/"
cp -R "$ROOT_DIR/haas_nemoclaw" "$BUNDLE_DIR/"
cp -R "$ROOT_DIR/tests" "$BUNDLE_DIR/"
cp -R "$ROOT_DIR/scripts" "$BUNDLE_DIR/"

echo "Created submission bundle at: $BUNDLE_DIR"
