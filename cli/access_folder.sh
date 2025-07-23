#!/bin/bash

# fpw - Folder Password Wrapper
# Simple wrapper script for the Python backend

# Get the real path of the script (resolve symlinks)
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
PYTHON_SCRIPT="$SCRIPT_DIR/main.py"

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: main.py not found in $SCRIPT_DIR"
    exit 1
fi

# Pass all arguments to the Python script
python3 "$PYTHON_SCRIPT" "$@"
