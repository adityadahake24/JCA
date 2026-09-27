#!/usr/bin/env python3
"""Generates JCA_UserStories.xlsx from the YAML source data in stories/.

Run: python build_workbook.py
Requires: openpyxl, pyyaml (pip install openpyxl pyyaml)
"""
import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

import _common as c

OUT_PATH = Path(__file__).parent / "JCA_UserStories.xlsx"

# ---- Style constants (crimson/gold/cream -- the RFP-compliant palette) ----
HEADER_FILL = PatternFill("solid", fgColor="7A1620")       # crimson-deep
HEADER_FONT = Font(color="FAF6EF", bold=True, size=11)     # cream on crimson
SUBHEADER_FILL = PatternFill("solid", fgColor="F4ECDD")    # cream-warm
FOOTER_FILL = PatternFill("solid", fgColor="E3C889")       # gold-light (decorative bg only, no text on it needs AA)
FOOTER_FONT = Font(bold=True, italic=True, size=10, color="1C1410")
TITLE_FONT = Font(bold=True, size=14, color="7A1620")
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


def write_row(ws, row, values, wrap=True, bold=False, fill=None):
    for col, val in enumerate(values, start=1):
        cell = ws.cell(row=row, column=col, value=val)
        cell.alignment = WRAP if wrap else Alignment(vertical="top")
        if bold:
            cell.font = Font(bold=True)
        if fill:
            cell.fill = fill
        cell.border = THIN_BORDER


# ---------------------------------------------------------------------------
# Module sheets
# ---------------------------------------------------------------------------

MODULE_COLUMNS = [
    "ID", "User Story", "Acceptance Criteria", "Subtasks", "Surfaces",
    "Priority", "Complexity", "Phase", "Sprint", "Status",
]
MODULE_WIDTHS = [10, 42, 42, 34, 16, 10, 12, 22, 16, 10]


def build_module_sheet(wb, phase_name, module):
    title = module["sheet_name"][:31]
    ws = wb.create_sheet(title)
    write_row(ws, 1, MODULE_COLUMNS, wrap=False)
    style_header_row(ws, 1, len(MODULE_COLUMNS))

    row = 2
    for s in module["stories"]:
        write_row(ws, row, [
            s["id"],
            s["story"],
            s["acceptance_criteria"],
            "\n".join(f"- {t}" for t in s["subtasks"]),
            ", ".join(s.get("surfaces", [])),
            s.get("priority", ""),
            s.get("complexity", ""),
            phase_name,
            module["sprint"] + " (" + module["sprint_weeks"] + ")",
            s.get("status", "Ready"),
        ])
        row += 1

    # Footer row -- MedCare360-style sprint summary
    row += 1
    footer_text = (
        f"Sprint: {module['sprint']}  ·  {module['sprint_weeks']}  ·  "
        f"Sprint Complexity: {module['sprint_complexity']}  ·  "
        f"Gate: {module['gate']}"
    )
    ws.cell(row=row, column=1, value=footer_text)
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=len(MODULE_COLUMNS))
    for col in range(1, len(MODULE_COLUMNS) + 1):
        cell = ws.cell(row=row, column=col)
        cell.fill = FOOTER_FILL
        cell.font = FOOTER_FONT
        cell.alignment = WRAP

    autosize(ws, MODULE_WIDTHS)
    # generous row heights for wrapped content
    for r in range(2, row):
        ws.row_dimensions[r].height = 70
    ws.row_dimensions[row].height = 30
    return ws


# ---------------------------------------------------------------------------
# Summary sheet
# ---------------------------------------------------------------------------

def build_summary_sheet(wb, phase_modules):
    ws = wb.create_sheet("Summary", 0)
    cols = ["Module", "Phase", "Sprint(s)", "Stories", "Done", "Working", "Ready",
            "Sprint Complexity", "Duration (wks)", "Surfaces"]
    write_row(ws, 1, cols, wrap=False)
    style_header_row(ws, 1, len(cols))

    row = 2
    totals = {"stories": 0, "done": 0, "working": 0, "ready": 0, "weeks": 0}
    for phase_name, module in phase_modules:
        counts = c.module_status_counts(module)
        weeks = c.parse_week_span(module["sprint_weeks"])
        write_row(ws, row, [
            module["module"],
            phase_name,
            module["sprint"],
            len(module["stories"]),
            counts["Done"],
            counts["Working"],
            counts["Ready"],
            module["sprint_complexity"],
            weeks,
            ", ".join(c.module_surfaces(module)),
        ])
        totals["stories"] += len(module["stories"])
        totals["done"] += counts["Done"]
        totals["working"] += counts["Working"]
        totals["ready"] += counts["Ready"]
        totals["weeks"] += weeks
        row += 1

    write_row(ws, row, [
        "TOTAL", "", "", totals["stories"], totals["done"], totals["working"],
        totals["ready"], "", totals["weeks"], "",
    ], bold=True, fill=SUBHEADER_FILL)

    row += 2
    ws.cell(row=row, column=1, value="Team shape: 6-8 people (1 PM/BA, 1 designer, 2 backend, 2 web/admin, 2 React Native, 1 QA), parallel surface tracks. Cadence: 2-week sprints, relative labelling.")
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=len(cols))
    ws.cell(row=row, column=1).alignment = WRAP
    ws.cell(row=row, column=1).font = Font(italic=True, size=9)

    row += 1
    roadmap = c.load_roadmap()
    ws.cell(row=row, column=1, value=roadmap["kickoff_note"].strip())
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=len(cols))
    ws.cell(row=row, column=1).alignment = WRAP
    ws.cell(row=row, column=1).font = Font(italic=True, size=9)
    ws.row_dimensions[row].height = 60

    autosize(ws, [26, 22, 14, 10, 8, 10, 8, 16, 14, 30])
    for r in range(2, row - 1):
        ws.row_dimensions[r].height = 20
    return ws


# ---------------------------------------------------------------------------
# Roadmap sheet
# ---------------------------------------------------------------------------

def build_roadmap_sheet(wb):
    ws = wb.create_sheet("Phase & Sprint Roadmap")
    roadmap = c.load_roadmap()
    phases_by_key = {p["key"]: p for p in roadmap["phases"]}

    cols = ["Sprint", "Phase", "Weeks", "Modules in Flight", "Sprint Goal", "Complexity", "Gate / Demo"]
    write_row(ws, 1, cols, wrap=False)
    style_header_row(ws, 1, len(cols))

    row = 2
    current_phase = None
    for sprint in roadmap["sprints"]:
        phase = phases_by_key[sprint["phase"]]
        if phase["name"] != current_phase:
            ws.cell(row=row, column=1, value=f"{phase['name']}  —  {phase['sprint_range']}, {phase['week_range']}")
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=len(cols))
            c1 = ws.cell(row=row, column=1)
            c1.fill = SUBHEADER_FILL
            c1.font = Font(bold=True, italic=True, color="7A1620")
            c1.alignment = WRAP
            row += 1
            ws.cell(row=row, column=1, value=phase["goal"])
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=len(cols))
            ws.cell(row=row, column=1).alignment = WRAP
            ws.cell(row=row, column=1).font = Font(italic=True, size=9)
            row += 1
            current_phase = phase["name"]

        write_row(ws, row, [
            sprint["id"],
            phase["name"].split("—")[0].strip(),
            sprint["weeks"],
            ", ".join(sprint["modules"]),
            sprint["goal"],
            sprint["complexity"],
            sprint["gate"],
        ])
        row += 1

    autosize(ws, [10, 18, 22, 40, 46, 12, 40])
    for r in range(2, row):
        ws.row_dimensions[r].height = 45
    return ws


# ---------------------------------------------------------------------------
# Tech Decisions sheet
# ---------------------------------------------------------------------------

def build_decisions_sheet(wb):
    ws = wb.create_sheet("Tech Decisions")
    decisions = c.load_decisions()
    cols = ["Decision", "Fixed by User", "Options Considered", "Offense (case for)",
            "Defence (risk / case against)", "Recommendation", "Blocks Sprint"]
    write_row(ws, 1, cols, wrap=False)
    style_header_row(ws, 1, len(cols))

    row = 2
    for d in decisions:
        write_row(ws, row, [
            d["decision"],
            "Yes" if d.get("fixed_by_user") else "No",
            d["options"],
            d["offense"].strip(),
            d["defence"].strip(),
            d["recommendation"],
            d["blocks_sprint"],
        ])
        row += 1

    autosize(ws, [24, 12, 30, 46, 46, 34, 14])
    for r in range(2, row):
        ws.row_dimensions[r].height = 110
    return ws


# ---------------------------------------------------------------------------
# Discovery sheet
# ---------------------------------------------------------------------------

def build_discovery_sheet(wb):
    ws = wb.create_sheet("Discovery & Open Items")
    items = c.load_discovery()
    cols = ["ID", "Item", "Source", "Open Question", "Recommendation", "Owner", "Resolve By"]
    write_row(ws, 1, cols, wrap=False)
    style_header_row(ws, 1, len(cols))

    row = 2
    for it in items:
        write_row(ws, row, [
            it["id"], it["item"], it["source"], it["question"],
            it["recommendation"], it["owner"], it["resolve_by_sprint"],
        ])
        row += 1

    autosize(ws, [10, 26, 22, 40, 44, 26, 14])
    for r in range(2, row):
        ws.row_dimensions[r].height = 80
    return ws


# ---------------------------------------------------------------------------
# DB Schema sheet
# ---------------------------------------------------------------------------

def build_schema_sheet(wb):
    ws = wb.create_sheet("DB Schema")
    domains = c.load_schema()
    cols = ["Domain", "Table", "Purpose", "Key Columns", "Foreign Keys", "Phase"]
    write_row(ws, 1, cols, wrap=False)
    style_header_row(ws, 1, len(cols))

    row = 2
    for domain in domains:
        for t in domain["tables"]:
            write_row(ws, row, [
                domain["name"], t["table"], t["purpose"], t["key_columns"],
                t["fks"], t["phase"],
            ])
            row += 1

    autosize(ws, [18, 22, 46, 34, 30, 12])
    for r in range(2, row):
        ws.row_dimensions[r].height = 45
    return ws


# ---------------------------------------------------------------------------
# API map sheet
# ---------------------------------------------------------------------------

def build_api_map_sheet(wb):
    ws = wb.create_sheet("API to Table Map")
    endpoints = c.load_api_map()
    cols = ["Endpoint", "Method", "Tables Read", "Tables Written", "Surfaces", "Min Role", "Phase", "Story ID"]
    write_row(ws, 1, cols, wrap=False)
    style_header_row(ws, 1, len(cols))

    row = 2
    for e in endpoints:
        write_row(ws, row, [
            e["endpoint"], e["method"], e["tables_read"], e["tables_written"],
            e["surfaces"], e["min_role"], e["phase"], e["story_id"],
        ])
        row += 1

    autosize(ws, [30, 14, 30, 26, 18, 20, 10, 12])
    for r in range(2, row):
        ws.row_dimensions[r].height = 32
    return ws


# ---------------------------------------------------------------------------
# Design Tokens sheet
# ---------------------------------------------------------------------------

def build_tokens_sheet(wb):
    ws = wb.create_sheet("Design Tokens & Palette")
    data = c.load_tokens()
    cols = ["Token", "Value", "Role", "Contrast vs Cream", "AA Verdict", "Surfaces"]
    write_row(ws, 1, cols, wrap=False)
    style_header_row(ws, 1, len(cols))

    row = 2
    ws.cell(row=row, column=1, value=data["palette_note"].strip())
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=len(cols))
    ws.cell(row=row, column=1).alignment = WRAP
    ws.cell(row=row, column=1).font = Font(italic=True, size=9)
    ws.row_dimensions[row].height = 55
    row += 1

    for t in data["base_tokens"]:
        # color-swatch the Value cell where it's a hex color
        write_row(ws, row, [
            t["token"], t["value"], t["role"], t["contrast_vs_cream"],
            t["aa_verdict"], t["surfaces"],
        ])
        val = t["value"]
        m = re.match(r"^#([0-9a-fA-F]{6})$", val)
        if m:
            ws.cell(row=row, column=2).fill = PatternFill("solid", fgColor=m.group(1))
        row += 1

    row += 1
    ws.cell(row=row, column=1, value="Typography").font = Font(bold=True, color="7A1620")
    row += 1
    for t in data["typography"]:
        write_row(ws, row, [t["role"], t["family"], t["usage"], "", "", ""])
        row += 1

    row += 1
    ws.cell(row=row, column=1, value="Spacing & Shape").font = Font(bold=True, color="7A1620")
    row += 1
    for t in data["spacing_and_shape"]:
        write_row(ws, row, [t["token"], t["value"], "", "", "", ""])
        row += 1

    row += 1
    ws.cell(row=row, column=1, value=f"Iconography: {data['iconography_note'].strip()}")
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=len(cols))
    ws.cell(row=row, column=1).alignment = WRAP
    ws.row_dimensions[row].height = 55
    row += 1
    ws.cell(row=row, column=1, value=f"Dark mode: {data['dark_mode_scope'].strip()}")
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=len(cols))
    ws.cell(row=row, column=1).alignment = WRAP
    ws.row_dimensions[row].height = 55

    autosize(ws, [22, 14, 46, 18, 34, 24])
    return ws


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    wb = Workbook()
    wb.remove(wb.active)  # drop the default sheet; Summary is created explicitly at index 0

    modules = c.all_modules()  # (phase_key, phase_name, module)
    phase_modules = [(pn, m) for (_, pn, m) in modules]

    build_summary_sheet(wb, phase_modules)
    build_roadmap_sheet(wb)
    build_decisions_sheet(wb)
    build_discovery_sheet(wb)
    build_schema_sheet(wb)
    build_api_map_sheet(wb)
    build_tokens_sheet(wb)

    for (_, phase_name, module) in modules:
        build_module_sheet(wb, phase_name, module)

    wb.save(OUT_PATH)
    print(f"Wrote {OUT_PATH} with {len(wb.sheetnames)} sheets.")


if __name__ == "__main__":
    main()
