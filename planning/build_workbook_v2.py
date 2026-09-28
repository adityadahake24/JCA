#!/usr/bin/env python3
"""Generates JCA_UserStories_v2.xlsx — the management/planning view.

This is a trimmed-down companion to JCA_UserStories.xlsx (build_workbook.py),
built from the exact same YAML source in stories/ so the two never drift on
substance, only on how much detail is shown.

v2 drops: acceptance-criteria/subtask/priority/complexity columns, sprint and
week mapping, the DB Schema sheet, the API-to-Table-Map sheet, and the Design
Tokens & Palette sheet. Each phase becomes ONE sheet (not one sheet per
module) with just Module, User Story, and Description. Tech Decisions and
Discovery & Open Items are kept (they're decisions/open-questions content,
not dev-implementation detail) with their sprint-mapping columns dropped.

Run: python build_workbook_v2.py
Requires: openpyxl, pyyaml (pip install openpyxl pyyaml)
"""
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

import _common as c

OUT_PATH = Path(__file__).parent / "JCA_UserStories_v2.xlsx"

# ---- Style constants (same crimson/gold/cream palette as v1) ----
HEADER_FILL = PatternFill("solid", fgColor="7A1620")
HEADER_FONT = Font(color="FAF6EF", bold=True, size=11)
MODULE_FILL = PatternFill("solid", fgColor="F4ECDD")
MODULE_FONT = Font(bold=True, size=11, color="7A1620")
BAND_FILLS = [PatternFill("solid", fgColor="FFFFFF"), PatternFill("solid", fgColor="FBF8F2")]
TITLE_FONT = Font(bold=True, size=15, color="7A1620")
SUBTITLE_FONT = Font(italic=True, size=10, color="4A4038")
WRAP = Alignment(wrap_text=True, vertical="top", horizontal="left")
WRAP_CENTER = Alignment(wrap_text=True, vertical="top", horizontal="center")
THIN_BORDER = Border(bottom=Side(style="thin", color="D9CBB0"))


def style_header_row(ws: Worksheet, row: int, ncols: int):
    for col in range(1, ncols + 1):
        cell = ws.cell(row=row, column=col)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = WRAP_CENTER
    ws.freeze_panes = ws.cell(row=row + 1, column=1).coordinate


def autosize(ws: Worksheet, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def write_title(ws, ncols, title, subtitle=None):
    ws.cell(row=1, column=1, value=title).font = TITLE_FONT
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
    row = 2
    if subtitle:
        ws.cell(row=row, column=1, value=subtitle).font = SUBTITLE_FONT
        ws.cell(row=row, column=1).alignment = WRAP
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
        ws.row_dimensions[row].height = 30
        row += 1
    row += 1
    return row


# ---------------------------------------------------------------------------
# Phase sheets — one per phase: ID | Module | User Story | Description
# ---------------------------------------------------------------------------

PHASE_COLUMNS = ["ID", "Module", "User Story", "Description"]
PHASE_WIDTHS = [10, 30, 52, 66]


def build_phase_sheet(wb, sheet_title, phase_name, phase_goal, modules):
    ws = wb.create_sheet(sheet_title)
    header_row = write_title(ws, len(PHASE_COLUMNS), phase_name, phase_goal)

    write_row_values(ws, header_row, PHASE_COLUMNS, wrap=False)
    style_header_row(ws, header_row, len(PHASE_COLUMNS))

    row = header_row + 1
    for m_idx, module in enumerate(modules):
        band = BAND_FILLS[m_idx % 2]
        module_start = row
        for s in module["stories"]:
            values = [s["id"], module["module"], s["story"], s["acceptance_criteria"]]
            for col, val in enumerate(values, start=1):
                cell = ws.cell(row=row, column=col, value=val)
                cell.alignment = WRAP
                cell.border = THIN_BORDER
                cell.fill = band
            ws.row_dimensions[row].height = 85
            row += 1
        module_end = row - 1
        # Bold the module name and vertically merge it across its story block.
        module_cell = ws.cell(row=module_start, column=2)
        module_cell.font = MODULE_FONT
        if module_end > module_start:
            ws.merge_cells(start_row=module_start, start_column=2, end_row=module_end, end_column=2)
            ws.cell(row=module_start, column=2).alignment = Alignment(wrap_text=True, vertical="top", horizontal="left")

    autosize(ws, PHASE_WIDTHS)
    return ws


def write_row_values(ws, row, values, wrap=True):
    for col, val in enumerate(values, start=1):
        cell = ws.cell(row=row, column=col, value=val)
        cell.alignment = WRAP if wrap else Alignment(vertical="top")


# ---------------------------------------------------------------------------
# Summary sheet — phase index, no sprint/week/status detail
# ---------------------------------------------------------------------------

def build_summary_sheet(wb, phase_modules):
    ws = wb.create_sheet("Summary", 0)
    ncols = 4
    row = write_title(
        ws, ncols, "JCA Platform — Build Plan (Management View)",
        "User stories grouped by phase and module. Timeline, sequencing, and sprint mapping are intentionally left out of this "
        "view and will be added once this plan is reviewed and finalized. See the companion detailed workbook for the full "
        "developer-facing breakdown (acceptance criteria, subtasks, priority, complexity, sprint plan, schema, and API map).",
    )
    cols = ["Phase", "Goal", "Modules in This Phase", "Stories"]
    write_row_values(ws, row, cols, wrap=False)
    style_header_row(ws, row, ncols)
    row += 1

    roadmap = c.load_roadmap()
    goals_by_key = {p["key"]: p["goal"] for p in roadmap["phases"]}

    for phase_key, phase_name, modules in phase_modules:
        module_names = ", ".join(m["module"] for m in modules)
        story_count = sum(len(m["stories"]) for m in modules)
        write_row_values(ws, row, [phase_name, goals_by_key.get(phase_key, ""), module_names, story_count])
        for col in range(1, ncols + 1):
            ws.cell(row=row, column=col).border = THIN_BORDER
        ws.row_dimensions[row].height = 70
        row += 1

    row += 1
    ws.cell(row=row, column=1, value=(
        "Fixed technology decisions reflected throughout this plan: a single Expo codebase builds the Web, iOS, and Android "
        "UI from one source; Payload CMS is the admin utility and content layer (the admin can edit almost everything, "
        "including landing-page content, from one place); FastAPI is the backend API. See the Tech Decisions sheet for the "
        "full rationale."
    )).font = Font(italic=True, size=9)
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
    ws.cell(row=row, column=1).alignment = WRAP
    ws.row_dimensions[row].height = 55

    autosize(ws, [24, 60, 60, 10])
    return ws


# ---------------------------------------------------------------------------
# Tech Decisions sheet — same content as v1, minus the sprint-blocking column
# ---------------------------------------------------------------------------

def build_decisions_sheet(wb):
    ws = wb.create_sheet("Tech Decisions")
    decisions = c.load_decisions()
    ncols = 5
    row = write_title(ws, ncols, "Tech Decisions", "What we're building on, why, and what the trade-off is.")
    cols = ["Decision", "Fixed by User", "Options Considered", "Why This / Risk & Mitigation", "Recommendation"]
    write_row_values(ws, row, cols, wrap=False)
    style_header_row(ws, row, ncols)
    row += 1

    for d in decisions:
        why = d["offense"].strip() + "\n\n" + d["defence"].strip()
        write_row_values(ws, row, [
            d["decision"],
            "Yes" if d.get("fixed_by_user") else "No",
            d["options"],
            why,
            d["recommendation"],
        ])
        for col in range(1, ncols + 1):
            ws.cell(row=row, column=col).border = THIN_BORDER
        ws.row_dimensions[row].height = 160
        row += 1

    autosize(ws, [26, 12, 32, 62, 40])
    return ws


# ---------------------------------------------------------------------------
# Discovery & Open Items sheet — same content as v1, minus resolve-by-sprint
# ---------------------------------------------------------------------------

def build_discovery_sheet(wb):
    ws = wb.create_sheet("Discovery & Open Items")
    items = c.load_discovery()
    ncols = 5
    row = write_title(
        ws, ncols, "Discovery & Open Items",
        "Open questions that need a JCA decision before the related build work can be considered final.",
    )
    cols = ["ID", "Item", "Open Question", "Recommendation", "Owner"]
    write_row_values(ws, row, cols, wrap=False)
    style_header_row(ws, row, ncols)
    row += 1

    for it in items:
        write_row_values(ws, row, [it["id"], it["item"], it["question"], it["recommendation"], it["owner"]])
        for col in range(1, ncols + 1):
            ws.cell(row=row, column=col).border = THIN_BORDER
        ws.row_dimensions[row].height = 85
        row += 1

    autosize(ws, [10, 26, 46, 50, 30])
    return ws


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

PHASE_SHEET_TITLES = {
    "phase0": "Phase 0 — Foundation",
    "phase1": "Phase 1 — v1.0",
    "phase2": "Phase 2 — v1.5",
    "phase3": "Phase 3 — v2.0",
}


def main():
    wb = Workbook()
    wb.remove(wb.active)

    all_phases = c.load_all_phases()
    phase_modules = [(p["phase_key"], p["phase_name"], p["modules"]) for p in all_phases]

    build_summary_sheet(wb, phase_modules)
    build_decisions_sheet(wb)
    build_discovery_sheet(wb)

    for phase_key, phase_name, modules in phase_modules:
        goal = next((p["goal"] for p in c.load_roadmap()["phases"] if p["key"] == phase_key), "")
        build_phase_sheet(wb, PHASE_SHEET_TITLES[phase_key], phase_name, goal, modules)

    wb.save(OUT_PATH)
    print(f"Wrote {OUT_PATH} with {len(wb.sheetnames)} sheets.")


if __name__ == "__main__":
    main()
