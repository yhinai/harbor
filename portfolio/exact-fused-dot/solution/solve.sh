#!/bin/bash
set -euo pipefail
task_solution_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
cp "$task_solution_dir/canonical.py" "${APP_DIR:-/app}/main.py"
