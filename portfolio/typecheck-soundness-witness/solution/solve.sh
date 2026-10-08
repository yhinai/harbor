#!/bin/bash
set -euo pipefail
task_solution_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
cp "$task_solution_dir/witness.json" "${APP_DIR:-/app}/witness.json"
