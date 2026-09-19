#!/usr/bin/env bash
SCRIPT_PATH="$(realpath -- "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd)"
cd "$SCRIPT_DIR" || exit 1
source venv/bin/activate
python3 build.py "$@"
