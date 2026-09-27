"""Shared data-loading for build_workbook.py and generate_docs.py.

Keeping this in one place is what makes the workbook tabs and the markdown
docs incapable of drifting from each other -- both read the exact same YAML.
"""
import re
from pathlib import Path

import yaml

STORIES_DIR = Path(__file__).parent / "stories"

PHASE_FILES = [
    "phase0_foundation.yaml",
    "phase1_v1.yaml",
    "phase2_v1_5.yaml",
    "phase3_v2.yaml",
]


def _load(name):
    with open(STORIES_DIR / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_roadmap():
    return _load("roadmap.yaml")


def load_decisions():
    return _load("decisions.yaml")["decisions"]


def load_discovery():
    return _load("discovery.yaml")["items"]


def load_tokens():
    return _load("tokens.yaml")


def load_schema():
    return _load("schema.yaml")["domains"]


def load_api_map():
    return _load("api_map.yaml")["endpoints"]


def load_all_phases():
    """Returns a list of phase dicts, each with a 'modules' list, in order."""
    return [_load(name) for name in PHASE_FILES]


def all_modules():
    """Flat list of (phase_key, phase_name, module_dict) across all phases."""
    out = []
    for phase in load_all_phases():
        for module in phase["modules"]:
            out.append((phase["phase_key"], phase["phase_name"], module))
    return out


def parse_week_span(weeks_str):
    """'Weeks 7-8' -> 2. 'Weeks 1-4' -> 4. Falls back to 2 if unparseable."""
    nums = re.findall(r"(\d+)", weeks_str)
    if len(nums) >= 2:
        return int(nums[-1]) - int(nums[0]) + 1
    return 2


def module_surfaces(module):
    surf = set()
    for s in module["stories"]:
        surf.update(s.get("surfaces", []))
    order = ["iOS", "Android", "Web", "Admin", "Backend"]
    return [s for s in order if s in surf]


def module_status_counts(module):
    counts = {"Ready": 0, "Working": 0, "Done": 0}
    for s in module["stories"]:
        counts[s.get("status", "Ready")] = counts.get(s.get("status", "Ready"), 0) + 1
    return counts
