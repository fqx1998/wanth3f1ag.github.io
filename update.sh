#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v hugo >/dev/null 2>&1; then
  echo "hugo is not installed or not in PATH" >&2
  exit 1
fi

hugo version
DESTINATION_DIR="${HUGO_DESTINATION:-public}"
hugo --environment production --gc --minify --cleanDestinationDir --destination "$DESTINATION_DIR"
