#!/usr/bin/env bash
# Copy the synthetic session.jsonl into the run's empty workspace.
set -euo pipefail
mkdir -p resources
cp "$(dirname "$0")/resources/session.jsonl" resources/
