#!/usr/bin/env python3
"""Generates the five markdown docs in docs/ from the same YAML source data
that build_workbook.py reads -- so the workbook tabs and these docs cannot
drift from each other.

Run: python generate_docs.py
"""
import re
from pathlib import Path

import _common as c

DOCS_DIR = Path(__file__).parent / "docs"
FK_PATTERN = re.compile(r"(\w+)\s*->\s*(\w+)")


def write(name, content):
    path = DOCS_DIR / name
    path.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")


# ---------------------------------------------------------------------------
# 01 - Tech decisions
# ---------------------------------------------------------------------------

def build_decisions_doc():
    decisions = c.load_decisions()
    lines = [
        "# Tech Decisions — Offense / Defence",
        "",
        "Every open technology and vendor decision on this project, argued both",
        "ways. User-fixed choices (React Native for mobile, a single Python",
        "backend, an SEO-capable web framework) are recorded too, scoped to the",
        "sub-decisions still open within them. This document and the **Tech",
        "Decisions** tab in `JCA_UserStories.xlsx` are generated from the same",
        "source (`stories/decisions.yaml`) and cannot drift from each other.",
        "",
    ]
    for d in decisions:
        fixed = " *(fixed by user)*" if d.get("fixed_by_user") else ""
        lines.append(f"## {d['decision']}{fixed}")
        lines.append("")
        lines.append(f"**Options considered:** {d['options']}")
        lines.append("")
        lines.append(f"**Offense (case for):** {d['offense'].strip()}")
        lines.append("")
        lines.append(f"**Defence (risk / case against):** {d['defence'].strip()}")
        lines.append("")
        lines.append(f"**Recommendation:** {d['recommendation']}")
        lines.append("")
        lines.append(f"**Blocks:** {d['blocks_sprint']}")
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 02 - Design system
# ---------------------------------------------------------------------------

def build_design_doc():
    data = c.load_tokens()
    lines = [
        "# Design System — Tokens & Palette",
        "",
        data["palette_note"].strip(),
        "",
        "## Color tokens",
        "",
        "Contrast ratios computed via the WCAG 2.1 relative-luminance formula",
        "against `--cream` (#faf6ef), verified programmatically (see",
        "`planning/build_workbook.py`'s verification pass). AA thresholds: 4.5:1",
        "normal text, 3.0:1 large text (>=24px or >=19px bold) and UI",
        "components/graphics.",
        "",
        "| Token | Value | Role | Contrast vs Cream | AA Verdict |",
        "|---|---|---|---|---|",
    ]
    for t in data["base_tokens"]:
        lines.append(f"| `{t['token']}` | `{t['value']}` | {t['role']} | {t['contrast_vs_cream']} | {t['aa_verdict']} |")

    lines += [
        "",
        "## Typography",
        "",
        "| Role | Family | Usage |",
        "|---|---|---|",
    ]
    for t in data["typography"]:
        lines.append(f"| {t['role']} | {t['family']} | {t['usage']} |")

    lines += [
        "",
        "## Spacing & shape",
        "",
        "| Token | Value |",
        "|---|---|",
    ]
    for t in data["spacing_and_shape"]:
        lines.append(f"| {t['token']} | {t['value']} |")

    lines += [
        "",
        "## Iconography",
        "",
        data["iconography_note"].strip(),
        "",
        "## Dark mode",
        "",
        data["dark_mode_scope"].strip(),
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 03 - Database schema (with Mermaid ERDs)
# ---------------------------------------------------------------------------

def parse_fks(fk_string):
    if not fk_string or fk_string.strip() in ("—", ""):
        return []
    return FK_PATTERN.findall(fk_string)


def build_schema_doc():
    domains = c.load_schema()
    lines = [
        "# Database Schema",
        "",
        "Organized into nine domains. Every table carries these cross-cutting",
        "conventions unless noted otherwise:",
        "",
        "- UUID primary key",
        "- `created_at`, `updated_at`, `created_by`, `updated_by`",
        "- `deleted_at` (soft-delete tombstone; RFP §4.4.1 — 30-day recovery window)",
        "- `version` (integer, optimistic locking; RFP §4.4.1 — multi-admin safety)",
        "- An `audit_log` entry on every INSERT/UPDATE/DELETE originating from the admin utility",
        "",
    ]

    for domain in domains:
        lines.append(f"## {domain['name']}")
        lines.append("")
        lines.append("| Table | Purpose | Key Columns | Foreign Keys | Phase |")
        lines.append("|---|---|---|---|---|")
        for t in domain["tables"]:
            lines.append(f"| `{t['table']}` | {t['purpose']} | {t['key_columns']} | {t['fks']} | {t['phase']} |")
        lines.append("")

        # Mermaid ERD for this domain
        relations = []
        table_names = {t["table"] for t in domain["tables"]}
        for t in domain["tables"]:
            for fk_col, target in parse_fks(t["fks"]):
                relations.append((t["table"], target, fk_col))
        if relations:
            lines.append("```mermaid")
            lines.append("erDiagram")
            seen = set()
            for child, parent, col in relations:
                key = (child, parent, col)
                if key in seen:
                    continue
                seen.add(key)
                child_id = child.upper()
                parent_id = parent.upper()
                lines.append(f'    {parent_id} ||--o{{ {child_id} : "{col}"')
            lines.append("```")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 04 - API contract map
# ---------------------------------------------------------------------------

def build_api_doc():
    endpoints = c.load_api_map()
    lines = [
        "# API Contract & Integration Map",
        "",
        "Representative endpoints per module (not exhaustive of every route),",
        "each traced to the tables it touches, the surfaces that call it, the",
        "minimum role required, and the story that specifies it. The full",
        "contract is published as OpenAPI 3.1 via drf-spectacular",
        "(see `API-1` in the API Contract & Integration Map module).",
        "",
        "**Versioning:** all routes are prefixed `/api/v1/`. Breaking changes",
        "require a minimum 90-day deprecation window with a `Sunset` header",
        "(see decision `API-3`).",
        "",
        "| Endpoint | Method | Tables Read | Tables Written | Surfaces | Min Role | Phase | Story |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for e in endpoints:
        lines.append(
            f"| `{e['endpoint']}` | {e['method']} | {e['tables_read']} | "
            f"{e['tables_written']} | {e['surfaces']} | {e['min_role']} | "
            f"{e['phase']} | {e['story_id']} |"
        )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 05 - Phase & sprint roadmap
# ---------------------------------------------------------------------------

def build_roadmap_doc():
    roadmap = c.load_roadmap()
    phases_by_key = {p["key"]: p for p in roadmap["phases"]}
    lines = [
        "# Phase & Sprint Roadmap",
        "",
        "Relative sprint labelling (no calendar dates) — 2-week cadence,",
        "6-8 person team with parallel surface tracks.",
        "",
        roadmap["kickoff_note"].strip(),
        "",
    ]

    current_phase = None
    for sprint in roadmap["sprints"]:
        phase = phases_by_key[sprint["phase"]]
        if phase["name"] != current_phase:
            lines.append(f"## {phase['name']} ({phase['sprint_range']}, {phase['week_range']})")
            lines.append("")
            lines.append(f"**Goal:** {phase['goal']}")
            lines.append("")
            lines.append("| Sprint | Weeks | Modules in Flight | Sprint Goal | Complexity | Gate / Demo |")
            lines.append("|---|---|---|---|---|---|")
            current_phase = phase["name"]
        lines.append(
            f"| {sprint['id']} | {sprint['weeks']} | {', '.join(sprint['modules'])} | "
            f"{sprint['goal']} | {sprint['complexity']} | {sprint['gate']} |"
        )
        # blank line + new table header if this is the last sprint of the phase
        next_idx = roadmap["sprints"].index(sprint) + 1
        is_last = next_idx >= len(roadmap["sprints"]) or roadmap["sprints"][next_idx]["phase"] != sprint["phase"]
        if is_last:
            lines.append("")

    # totals
    total_weeks = {}
    for sprint in roadmap["sprints"]:
        weeks = c.parse_week_span(sprint["weeks"])
        total_weeks[sprint["phase"]] = total_weeks.get(sprint["phase"], 0) + weeks
    lines.append("## Totals")
    lines.append("")
    lines.append("| Phase | Approx. Duration |")
    lines.append("|---|---|")
    for key, phase in phases_by_key.items():
        lines.append(f"| {phase['name']} | ~{total_weeks.get(key, 0)} weeks |")
    lines.append("")
    return "\n".join(lines)


def main():
    DOCS_DIR.mkdir(exist_ok=True)
    write("01-tech-decisions.md", build_decisions_doc())
    write("02-design-system.md", build_design_doc())
    write("03-database-schema.md", build_schema_doc())
    write("04-api-contract-map.md", build_api_doc())
    write("05-phase-sprint-roadmap.md", build_roadmap_doc())


if __name__ == "__main__":
    main()
