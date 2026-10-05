#!/usr/bin/env python3
"""Adds 'Feature Matrix' and 'Gantt' sheets to the front of JCA_UserStories_v2.xlsx.

The xlsx is hand-edited and is the source of truth, so this script opens it in
place instead of regenerating it (build_workbook_v2.py would overwrite edits).
Re-running is safe: any existing Feature Matrix / Gantt sheets are replaced.

Run: python add_feature_sheets.py      (requires openpyxl)
"""
from datetime import date
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.formatting.rule import FormulaRule, CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

from build_workbook_v2 import (
    HEADER_FILL, HEADER_FONT, MODULE_FILL, MODULE_FONT, THIN_BORDER, WRAP_CENTER,
    autosize, style_header_row, write_title,
)

XLSX = Path(__file__).parent / "JCA_UserStories_v2.xlsx"
PROJECT_START = date(2026, 10, 5)
DEFAULT_WEEKS = 2
N_WEEKS = 104

PHASE_SHEETS = ["Phase 0 — Foundation", "Phase 1 — v1.0", "Phase 2 — v1.5", "Phase 3 — v2.0"]
PHASE_LABELS = ["Phase 0 — Foundation", "Phase 1 — v1.0", "Phase 2 — v1.5", "Phase 3 — v2.0"]

# (Guest / non-logged-in, Logged-in user, Admin utility)
Y, N = "Yes", "No"
ACCESS = {
    "Design Review": (Y, Y, Y),
    "Cloud Architecture & Platform Setup": (Y, Y, Y),
    "Data Migration Planning": (N, Y, Y),
    "Payment Provider Setup": (Y, Y, Y),
    "App Delivery Platform Enrollment": (Y, Y, N),
    "Auth, Identity & RBAC": (Y, Y, Y),
    "Home & Panchang": (Y, Y, Y),
    "Calendar & Events": (Y, Y, Y),
    "Content & Newsletter": (Y, Y, Y),
    "Payments & Billing Infrastructure": (Y, Y, Y),
    "Admin — Shell, Dashboards & Members": (N, N, Y),
    "Donations & Causes": (Y, Y, Y),
    "Recurring Giving & Subscriptions": (N, Y, Y),
    "Membership, Family & Dues": (Y, Y, Y),
    "Sponsorships & Religious Calendar": (N, Y, Y),
    "Community Feed & Moderation": (N, Y, Y),
    "Notifications & Messaging": (N, Y, Y),
    "Pathshala": (N, Y, Y),
    "Volunteers & Seva": (N, Y, Y),
    "Live Darshan": (Y, Y, Y),
    "Admin — Governance & Operations": (N, N, Y),
    "Public Web & SEO": (Y, N, Y),
    "Localization & Accessibility": (Y, Y, Y),
    "Security, Testing & QA": (Y, Y, Y),
    "Store & Launch Readiness": (Y, Y, N),
    "Governance & Documents": (N, Y, Y),
    "Library, Jinvani & Lectures": (Y, Y, Y),
    "Directory, Travel & Facility Booking": (N, Y, Y),
    "Recognition Programs": (Y, Y, Y),
    "Youth & YJA": (N, Y, Y),
    "Past Events & Gallery": (Y, Y, Y),
    "Reports & Analytics v2": (N, N, Y),
    "Hindi & Gujarati Localization": (Y, Y, Y),
    "v1.5 Hardening & Release": (Y, Y, Y),
    "Jain Philosophy Module": (Y, Y, Y),
    "JCA Cares": (N, Y, Y),
    "v2.0 Hardening & Release": (Y, Y, Y),
    "AI Chat (contingent workstream)": (N, Y, Y),
}

GREEN = DifferentialStyle(fill=PatternFill("solid", bgColor="D9EAD3"), font=Font(color="274E13", bold=True))
RED = DifferentialStyle(fill=PatternFill("solid", bgColor="F4CCCC"), font=Font(color="990000", bold=True))
INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")
PHASE_ROW_FILL = PatternFill("solid", fgColor="F4ECDD")
# (feature bar, phase-summary bar)
BAR_COLORS = [("6C7A89", "34495E"), ("B03A48", "7A1620"), ("E0B64A", "A67C00"), ("4DB6AC", "00796B")]
CENTER = Alignment(horizontal="center", vertical="center")

def _d(s):
    d, m = s.split()
    return date(2026 if m in ("Oct", "Nov", "Dec") else 2027, {"Oct": 10, "Nov": 11, "Dec": 12, "Jan": 1}[m], int(d))


# Delivery plan: Phase 0 = 5-16 Oct; Phases 1-3 overlap within 18 Oct - 15 Jan.
# Features not listed here fall back to the 2-week chained default.
_P0 = ("5 Oct", "16 Oct")
SCHEDULE = {k: _P0 for k in (
    "Design Review", "Cloud Architecture & Platform Setup", "Data Migration Planning",
    "Payment Provider Setup", "App Delivery Platform Enrollment", "Auth, Identity & RBAC")}
SCHEDULE.update({
    # Phase 1 (largest: 18 Oct - 15 Jan)
    "Home & Panchang": ("18 Oct", "14 Nov"),
    "Calendar & Events": ("18 Oct", "7 Nov"),
    "Content & Newsletter": ("25 Oct", "14 Nov"),
    "Payments & Billing Infrastructure": ("18 Oct", "14 Nov"),
    "Admin — Shell, Dashboards & Members": ("18 Oct", "21 Nov"),
    "Donations & Causes": ("8 Nov", "5 Dec"),
    "Recurring Giving & Subscriptions": ("15 Nov", "12 Dec"),
    "Membership, Family & Dues": ("8 Nov", "5 Dec"),
    "Sponsorships & Religious Calendar": ("15 Nov", "12 Dec"),
    "Community Feed & Moderation": ("15 Nov", "19 Dec"),
    "Notifications & Messaging": ("8 Nov", "5 Dec"),
    "Pathshala": ("22 Nov", "19 Dec"),
    "Volunteers & Seva": ("22 Nov", "19 Dec"),
    "Live Darshan": ("29 Nov", "19 Dec"),
    "Admin — Governance & Operations": ("22 Nov", "26 Dec"),
    "Public Web & SEO": ("8 Nov", "5 Dec"),
    "Localization & Accessibility": ("6 Dec", "2 Jan"),
    "Security, Testing & QA": ("13 Dec", "8 Jan"),
    "Store & Launch Readiness": ("20 Dec", "15 Jan"),
    # Phase 2 (22 Nov - 15 Jan)
    "Governance & Documents": ("22 Nov", "12 Dec"),
    "Library, Jinvani & Lectures": ("29 Nov", "19 Dec"),
    "Directory, Travel & Facility Booking": ("6 Dec", "26 Dec"),
    "Recognition Programs": ("6 Dec", "19 Dec"),
    "Youth & YJA": ("13 Dec", "26 Dec"),
    "Past Events & Gallery": ("29 Nov", "12 Dec"),
    "Reports & Analytics v2": ("13 Dec", "2 Jan"),
    "Hindi & Gujarati Localization": ("20 Dec", "8 Jan"),
    "v1.5 Hardening & Release": ("27 Dec", "15 Jan"),
    # Phase 3 (13 Dec - 15 Jan)
    "Jain Philosophy Module": ("13 Dec", "2 Jan"),
    "JCA Cares": ("20 Dec", "8 Jan"),
    "AI Chat (contingent workstream)": ("20 Dec", "15 Jan"),
    "v2.0 Hardening & Release": ("3 Jan", "15 Jan"),
})


def read_features(wb):
    """[(phase_idx, module_name)] — first occurrence of each module, in sheet order."""
    out, seen = [], set()
    for p, name in enumerate(PHASE_SHEETS):
        ws = wb[name]
        for r in range(1, ws.max_row + 1):
            v = ws.cell(r, 2).value
            if isinstance(v, str) and v.strip() and v != "Module" and v not in seen:
                seen.add(v)
                out.append((p, v.strip()))
    return out


def green_red_rules(ws, rng, yes, no):
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[f'"{yes}"'], font=GREEN.font, fill=GREEN.fill))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[f'"{no}"'], font=RED.font, fill=RED.fill))


def build_matrix(wb, features):
    ws = wb.create_sheet("Feature Matrix", 0)
    ncols = 6
    row = write_title(ws, ncols, "Feature Matrix — who gets what",
                      "Which section each planned feature belongs to. Use the Yes/No dropdowns to change a cell; "
                      "colours and the Gantt update automatically.")
    cols = ["#", "Phase", "Feature", "Guest / Non-logged-in", "Logged-in User", "Admin Utility"]
    for c, v in enumerate(cols, 1):
        ws.cell(row, c, v)
    style_header_row(ws, row, ncols)
    ws.row_dimensions[row].height = 32

    dv = DataValidation(type="list", formula1='"Yes,No"', allow_blank=False)
    ws.add_data_validation(dv)

    rows = {}  # feature name -> matrix row
    r, n, cur = row + 1, 0, None
    first = last = None
    for p, name in features:
        if p != cur:
            cur = p
            ws.cell(r, 1, PHASE_LABELS[p])
            for c in range(1, ncols + 1):
                ws.cell(r, c).fill = MODULE_FILL
                ws.cell(r, c).font = MODULE_FONT
            r += 1
        n += 1
        vals = ACCESS[name]
        ws.cell(r, 1, n).alignment = CENTER
        ws.cell(r, 2, PHASE_LABELS[p])
        ws.cell(r, 3, name)
        for i, v in enumerate(vals):
            cell = ws.cell(r, 4 + i, v)
            cell.alignment = CENTER
            dv.add(cell)
        for c in range(1, ncols + 1):
            ws.cell(r, c).border = THIN_BORDER
        rows[name] = r
        first = first or r
        last = r
        r += 1

    for col in "DEF":
        green_red_rules(ws, f"{col}{first}:{col}{last}", "Yes", "No")

    ws.cell(r, 3, "Features with access (Yes)").font = Font(bold=True)
    for i, col in enumerate("DEF"):
        c = ws.cell(r, 4 + i, f'=COUNTIF({col}{first}:{col}{last},"Yes")')
        c.font = Font(bold=True)
        c.alignment = CENTER
    for c in range(1, ncols + 1):
        ws.cell(r, c).border = Border(top=Side(style="medium", color="7A1620"))

    autosize(ws, [6, 22, 42, 22, 18, 16])
    return rows


def build_gantt(wb, features, mrows):
    ws = wb.create_sheet("Gantt", 1)
    FIX = 8  # fixed columns A..H
    W0 = FIX + 1
    last_col = L(FIX + N_WEEKS)
    write_title(ws, FIX, "Gantt — feature timeline",
                "Edit the yellow Start / End cells (or the Project start) and the bars redraw. Dates follow the delivery plan "
                "(Phase 0: 5-16 Oct; Phases 1-3 overlap within 18 Oct - 15 Jan). Overtype any date to re-plan.")
    ws.cell(3, 2, "Project start").font = Font(bold=True)
    ws.cell(3, 3, PROJECT_START).number_format = "dd-mmm-yy"
    ws.cell(3, 3).fill = INPUT_FILL
    ws.cell(3, 3).font = Font(bold=True)
    ws.cell(3, 3).alignment = CENTER
    PS = "$C$3"

    # header rows 5 (month), 6 (week start), 7 (labels)
    hdr = ["Phase", "Feature", "Guest", "Logged-in", "Admin", "Start", "End", "Weeks"]
    for c, v in enumerate(hdr, 1):
        ws.cell(7, c, v)
    for rr in (5, 6, 7):
        for c in range(1, FIX + N_WEEKS + 1):
            cell = ws.cell(rr, c)
            cell.fill, cell.font, cell.alignment = HEADER_FILL, HEADER_FONT, CENTER
    ws.cell(6, 8, "Week of →")
    for w in range(N_WEEKS):
        c = W0 + w
        col = L(c)
        ws.cell(6, c, f"={PS}" if w == 0 else f"={L(c - 1)}6+7").number_format = "d/m"
        ws.cell(7, c, f"W{w + 1}")
        ws.cell(5, c, f'=TEXT({col}6,"mmm yy")' if w == 0 else
                f'=IF(MONTH({col}6)<>MONTH({L(c - 1)}6),TEXT({col}6,"mmm yy"),"")')
        ws.cell(5, c).alignment = Alignment(horizontal="left")
        ws.cell(6, c).font = Font(color="FAF6EF", size=7)
        ws.cell(6, c).alignment = Alignment(horizontal="center", text_rotation=90)
        ws.cell(7, c).font = Font(color="FAF6EF", size=7)
        ws.column_dimensions[col].width = 3.3
    ws.row_dimensions[6].height = 30
    ws.row_dimensions[7].height = 20

    r = 8
    prev_feat_row = None
    blocks = {}  # phase idx -> (phase_row, first_feat, last_feat)
    cur = None
    for p, name in features:
        if p != cur:
            if cur is not None:
                blocks[cur] = (blocks[cur][0], blocks[cur][1], r - 1)
            cur = p
            blocks[p] = (r, r + 1, None)
            ws.cell(r, 1, PHASE_LABELS[p])
            for c in range(1, FIX + N_WEEKS + 1):
                ws.cell(r, c).fill = PHASE_ROW_FILL
                ws.cell(r, c).font = MODULE_FONT
            r += 1
        m = mrows[name]
        ws.cell(r, 1, f"='Feature Matrix'!B{m}")
        ws.cell(r, 2, f"='Feature Matrix'!C{m}")
        for i, col in enumerate("DEF"):
            ws.cell(r, 3 + i, f"=IF('Feature Matrix'!{col}{m}=\"Yes\",\"Y\",\"N\")").alignment = CENTER
        if name in SCHEDULE:
            ws.cell(r, 6, _d(SCHEDULE[name][0]))
            ws.cell(r, 7, _d(SCHEDULE[name][1]))
        else:
            ws.cell(r, 6, f"={PS}" if prev_feat_row is None else f"=G{prev_feat_row}+1")
            ws.cell(r, 7, f"=F{r}+{DEFAULT_WEEKS * 7 - 1}")
        ws.cell(r, 8, f"=ROUNDUP((G{r}-F{r}+1)/7,0)").alignment = CENTER
        for c in (6, 7):
            ws.cell(r, c).number_format = "dd-mmm-yy"
            ws.cell(r, c).fill = INPUT_FILL
            ws.cell(r, c).alignment = CENTER
        for c in range(1, FIX + 1):
            ws.cell(r, c).border = THIN_BORDER
        prev_feat_row = r
        r += 1
    blocks[cur] = (blocks[cur][0], blocks[cur][1], r - 1)
    last_row = r - 1

    for p, (pr, f1, f2) in blocks.items():
        ws.cell(pr, 6, f"=MIN(F{f1}:F{f2})")
        ws.cell(pr, 7, f"=MAX(G{f1}:G{f2})")
        ws.cell(pr, 8, f"=ROUNDUP((G{pr}-F{pr}+1)/7,0)")
        for c in (6, 7):
            ws.cell(pr, c).number_format = "dd-mmm-yy"
        for c in (6, 7, 8):
            ws.cell(pr, c).alignment = CENTER

    # Bars: one rule per phase for feature rows, one for the phase summary row
    w0, w1 = L(W0), last_col
    for p, (pr, f1, f2) in blocks.items():
        feat_c, phase_c = BAR_COLORS[p]
        for rng, colr, top in ((f"{w0}{f1}:{w1}{f2}", feat_c, f1), (f"{w0}{pr}:{w1}{pr}", phase_c, pr)):
            ws.conditional_formatting.add(rng, FormulaRule(
                formula=[f"AND({w0}$6<=$G{top},{w0}$6+6>=$F{top})"],
                fill=PatternFill("solid", bgColor=colr), stopIfTrue=False))
    # current-week marker
    ws.conditional_formatting.add(f"{w0}8:{w1}{last_row}", FormulaRule(
        formula=[f"AND(TODAY()>={w0}$6,TODAY()<={w0}$6+6)"],
        border=Border(left=Side(style="thin", color="C0392B"), right=Side(style="thin", color="C0392B"))))
    green_red_rules(ws, f"C8:E{last_row}", "Y", "N")

    ws.freeze_panes = ws.cell(8, W0)
    autosize(ws, [20, 38, 7, 9, 7, 11, 11, 7])
    return ws


def main():
    wb = load_workbook(XLSX)
    for name in ("Feature Matrix", "Gantt"):
        if name in wb.sheetnames:
            del wb[name]
    features = read_features(wb)
    missing = [n for _, n in features if n not in ACCESS]
    if missing:
        raise SystemExit(f"No Yes/No mapping for: {missing}")
    mrows = build_matrix(wb, features)
    build_gantt(wb, features, mrows)
    wb.save(XLSX)
    print(f"Added Feature Matrix + Gantt ({len(features)} features). Sheets: {wb.sheetnames}")


if __name__ == "__main__":
    main()
