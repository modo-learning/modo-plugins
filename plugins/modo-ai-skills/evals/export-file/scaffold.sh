#!/usr/bin/env bash
# Copy the synthetic conversations.json into the run's empty workspace.
set -euo pipefail
mkdir -p resources
cp "$(dirname "$0")/resources/conversations.json" resources/
