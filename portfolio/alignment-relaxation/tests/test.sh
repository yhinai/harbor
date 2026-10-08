#!/bin/bash
set -euo pipefail
task_test_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
exec python3 -I "$task_test_dir/grade.py"
