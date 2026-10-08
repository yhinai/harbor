"""Single source of truth for the current portfolio selection."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
SELECTION=json.loads((ROOT/'selected-tasks.json').read_text())
SLUGS=SELECTION['tasks']
RETAINED=[s for s in SLUGS if s!='typecheck-soundness-witness']
