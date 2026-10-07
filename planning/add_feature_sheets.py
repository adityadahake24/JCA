#!/usr/bin/env python3
"""Adds Guest / Member / Admin feature tables, RBAC and Gantt sheets to the front of JCA_UserStories_v2.xlsx.

Features come from the product sections in the mockups (website nav, phone app tabs, admin nav),
not from the phase modules. Web/App Yes/No and RBAC levels are proposed defaults; edit via dropdowns.

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




Y, N = "Yes", "No"
SHEETS = {"Guest": "Guest Features", "Member": "Member Features", "Admin": "Admin Utility"}
AUD_LABELS = {"Guest": "Guest (not logged in)", "Member": "Logged-in Member", "Admin": "Admin Utility"}

# (section, feature, description, web, app, schedule key)
GUEST = [
    ("Home", "Today at the temple", "Centre hours and today's aarti schedule", Y, Y, "Home & Panchang"),
    ("Home", "Panchang / tithi", "Daily Jain panchang on the home screen", Y, Y, "Home & Panchang"),
    ("Home", "Upcoming events teaser", "Next few events with link to full calendar", Y, Y, "Home & Panchang"),
    ("Home", "Latest announcements", "Pinned and recent temple announcements", Y, Y, "Content & Newsletter"),
    ("Home", "Newsletter sign-up", "Monthly letter e-mail subscription", Y, N, "Content & Newsletter"),
    ("Home", "Get-the-app promo", "Store badges / QR to install the app", Y, N, "Public Web & SEO"),
    ("Our Story", "Temple history — Fifty Years", "Timeline of the temple's history", Y, N, "Public Web & SEO"),
    ("Our Story", "Five floors & temple complex", "Walk-through of each floor of the complex", Y, Y, "Public Web & SEO"),
    ("Our Story", "Building plans & construction history", "Site selection, design, contracts, plans", Y, N, "Public Web & SEO"),
    ("Our Story", "Recognition wall", "Service award recipients and lifetime supporters", Y, N, "Recognition Programs"),
    ("Our Story", "Open Books", "Financial transparency / annual reports", Y, N, "Public Web & SEO"),
    ("Our Story", "Directions & contact", "Map, getting here, contact form", Y, Y, "Public Web & SEO"),
    ("Worship", "Five traditions & shrines", "Svetambara, Digambar, Sthanak, Shrimad Rajchandra, Dadawadi", Y, Y, "Public Web & SEO"),
    ("Worship", "Visitor guidelines", "Etiquette and what to expect on a first visit", Y, Y, "Public Web & SEO"),
    ("Festivals", "Sacred calendar", "Month view of parva days and events", Y, Y, "Calendar & Events"),
    ("Festivals", "Featured festival", "Paryushan / Das Lakshan and other highlighted parvas", Y, Y, "Calendar & Events"),
    ("Festivals", "Event detail", "Event page with schedule, location, details", Y, Y, "Calendar & Events"),
    ("Festivals", "News & events feed", "Latest news posts", Y, Y, "Content & Newsletter"),
    ("Festivals", "Newsletter archive", "Past issues of the newsletter", Y, Y, "Content & Newsletter"),
    ("Learn", "Temple architecture tour", "Building dimensions and floor-by-floor tour", Y, N, "Public Web & SEO"),
    ("Learn", "Visiting Acharyas & scholars", "Visit history and photos", Y, N, "Public Web & SEO"),
    ("Learn", "Pratimas guide", "Idols and their significance", Y, Y, "Public Web & SEO"),
    ("Learn", "Pathshala overview", "Programme description and how to enrol", Y, Y, "Public Web & SEO"),
    ("Learn", "Jain philosophy intro", "Introductory teaching content", Y, Y, "Jain Philosophy Module"),
    ("Belong", "Membership types", "Plans, benefits and pricing", Y, Y, "Membership, Family & Dues"),
    ("Belong", "Create account / register", "Sign-up for a member account", Y, Y, "Auth, Identity & RBAC"),
    ("Belong", "Youth & Senior groups", "Group descriptions and contact", Y, Y, "Public Web & SEO"),
    ("Belong", "Library info", "About the library and Jinvani", Y, N, "Library, Jinvani & Lectures"),
    ("Belong", "Volunteer interest form", "Public form to express interest in volunteering", Y, N, "Volunteers & Seva"),
    ("Give", "Active causes", "Browse current fundraising causes", Y, Y, "Donations & Causes"),
    ("Give", "Bhojanshala meal sponsorship info", "Sponsor a day of meals", Y, Y, "Donations & Causes"),
    ("Give", "Guest one-time donation", "Donate without an account", Y, Y, "Donations & Causes"),
    ("Give", "Zelle & employer matching", "Alternate giving instructions", Y, N, "Donations & Causes"),
    ("Give", "JCA Cares", "Compassion programme information", Y, Y, "JCA Cares"),
    ("Give", "Where your gift goes", "Accountability breakdown of giving", Y, N, "Donations & Causes"),
    ("Gallery", "Photo albums", "Event and temple photo albums", Y, Y, "Past Events & Gallery"),
    ("Gallery", "360° virtual tour", "Google virtual tour embed", Y, Y, "Past Events & Gallery"),
    ("Live Darshan", "Public live stream & aarti schedule", "Watch darshan live", Y, Y, "Live Darshan"),
    ("Access", "Sign in", "Login with email / SSO", Y, Y, "Auth, Identity & RBAC"),
]

MEMBER = [
    ("Home", "Personal greeting & quick actions", "Personalised home with shortcuts", N, Y, "Home & Panchang"),
    ("Home", "Notifications inbox", "In-app list of reminders and wishes", N, Y, "Notifications & Messaging"),
    ("Home", "Notification preferences", "Choose channels and topics", Y, Y, "Notifications & Messaging"),
    ("Calendar & Events", "Event RSVP / registration", "Register self and family for events", Y, Y, "Calendar & Events"),
    ("Calendar & Events", "Parva days", "Personal view of parva schedule", Y, Y, "Calendar & Events"),
    ("Calendar & Events", "Past events", "Archive of attended and past events", Y, Y, "Past Events & Gallery"),
    ("Give (Daan & Dharma)", "Donate to a cause", "One-time giving with cause selection", Y, Y, "Donations & Causes"),
    ("Give (Daan & Dharma)", "Sunday sponsorship booking", "Book available Sundays", Y, Y, "Donations & Causes"),
    ("Give (Daan & Dharma)", "Saved payment methods", "Card, Apple Pay, Google Pay, ACH", Y, Y, "Payments & Billing Infrastructure"),
    ("Give (Daan & Dharma)", "Receipts & thank-you", "Receipt and acknowledgement after giving", Y, Y, "Payments & Billing Infrastructure"),
    ("Give (Daan & Dharma)", "Donation history & tax statements", "Past gifts, downloadable statements", Y, Y, "Donations & Causes"),
    ("Give (Daan & Dharma)", "Recurring seva", "Set up and manage recurring giving plans", N, Y, "Recurring Giving & Subscriptions"),
    ("Community", "Community feed", "Posts, reactions, moderation", N, Y, "Community Feed & Moderation"),
    ("Community", "News & newsletters", "Member reading view", Y, Y, "Content & Newsletter"),
    ("Community", "Volunteer & seva sign-up", "Opportunity board and sign-up", Y, Y, "Volunteers & Seva"),
    ("Community", "Youth (YJA)", "Youth group activities", Y, Y, "Youth & YJA"),
    ("Sacred & Learning", "Pathshala enrolment & teacher contact", "Term enrolment, contact teacher", Y, Y, "Pathshala"),
    ("Sacred & Learning", "Jinvani library", "Read, continue reading, lectures", Y, Y, "Library, Jinvani & Lectures"),
    ("Sacred & Learning", "Jain philosophy module", "Structured learning content", Y, Y, "Jain Philosophy Module"),
    ("Sacred & Learning", "Live Darshan", "Member live stream view", Y, Y, "Live Darshan"),
    ("Institution & Support", "Jain Centers USA & nearby veg restaurants", "Directory and travel help", Y, Y, "Directory, Travel & Facility Booking"),
    ("Institution & Support", "Facility booking", "Request halls and rooms", Y, Y, "Directory, Travel & Facility Booking"),
    ("Institution & Support", "Meeting minutes", "Governance documents for members", Y, Y, "Governance & Documents"),
    ("Institution & Support", "Service award nomination", "Nominate a person for an award", Y, Y, "Recognition Programs"),
    ("Institution & Support", "JCA Cares request", "Request or offer help", Y, Y, "JCA Cares"),
    ("Me", "Profile & account", "Edit personal details", Y, Y, "Auth, Identity & RBAC"),
    ("Me", "Membership & renewal", "View plan, renew", Y, Y, "Membership, Family & Dues"),
    ("Me", "Family & dues", "Family members and outstanding dues", Y, Y, "Membership, Family & Dues"),
    ("Me", "Digital member card", "QR member card for check-in", N, Y, "Membership, Family & Dues"),
    ("Me", "Settings & language", "App settings, language, accessibility", Y, Y, "Localization & Accessibility"),
]

_SHELL, _GOV = "Admin — Shell, Dashboards & Members", "Admin — Governance & Operations"
ADMIN = [
    ("Overview", "Dashboard", "Operational overview with role-based variants", Y, Y, _SHELL),
    ("Engagement", "Content & Announcements", "Compose, preview, pin announcements and newsletters", Y, N, "Content & Newsletter"),
    ("Engagement", "Gallery & Media", "Albums, uploads, media library", Y, N, "Past Events & Gallery"),
    ("Engagement", "Events", "Create events, calendar conflict view", Y, N, "Calendar & Events"),
    ("Engagement", "Notifications", "Segment builder, compose, send", Y, Y, "Notifications & Messaging"),
    ("Givings", "Donations & Causes", "Recent donations, cause management, reports", Y, N, "Donations & Causes"),
    ("Givings", "Issue Refund (two-actor)", "Refund with second-admin confirmation", Y, N, "Payments & Billing Infrastructure"),
    ("Givings", "Sponsors & Recognition", "Sponsor records and recognition queue", Y, N, "Sponsorships & Religious Calendar"),
    ("Givings", "Bhojanshala", "Kitchen calendar and meal sponsorships", Y, N, "Sponsorships & Religious Calendar"),
    ("People", "Members & Families", "Member 360 view, families, segments", Y, N, _SHELL),
    ("People", "Member CSV Import", "Bulk import members", Y, N, "Data Migration Planning"),
    ("People", "Dues Ledger & Aging", "Dues ledger and aging report", Y, N, "Membership, Family & Dues"),
    ("People", "Pathshala Rosters", "Terms, rosters, teacher assignments", Y, N, "Pathshala"),
    ("People", "Volunteers & Seva", "Opportunity board and sign-ups", Y, N, "Volunteers & Seva"),
    ("Operations", "Facility Booking", "Reservation requests and approvals", Y, N, "Directory, Travel & Facility Booking"),
    ("Operations", "Religious Calendar & Aarti", "Panchang and aarti schedule management", Y, N, "Sponsorships & Religious Calendar"),
    ("Operations", "Live Darshan", "Stream sources and stream health", Y, Y, "Live Darshan"),
    ("Operations", "Library & Jinvani", "Submission review and catalogue", Y, N, "Library, Jinvani & Lectures"),
    ("Operations", "Directory & Resources", "Jain centres and local resources", Y, N, "Directory, Travel & Facility Booking"),
    ("Institution", "Governance Library", "Meeting minutes and governance documents", Y, N, "Governance & Documents"),
    ("Institution", "Reports & Exports", "Growth, donation, attendance and dues reports", Y, N, "Reports & Analytics v2"),
    ("Institution", "Audit Log", "Searchable log of admin actions", Y, N, _GOV),
    ("Institution", "Roles & Permissions", "Role editor and permission preview", Y, N, "Auth, Identity & RBAC"),
    ("Institution", "Settings & Integrations", "Credentials vault, localization, SSO, trash, system health", Y, N, _GOV),
]
DATA = {"Guest": GUEST, "Member": MEMBER, "Admin": ADMIN}

ROLES = ["Member", "Family Primary", "Pathshala Parent", "Committee Member", "Treasurer",
         "Communications", "Pathshala Coordinator", "Events Coordinator", "Admin", "Super-Admin"]
LEVELS = ["None", "View", "Edit", "Approve"]


def _rbac():
    names = [f[1] for f in ADMIN]
    rb = {r: {n: "None" for n in names} for r in ROLES}

    def put(role, level, *feats):
        for f in feats:
            assert f in rb[role], f
            rb[role][f] = level

    put("Pathshala Parent", "View", "Pathshala Rosters")
    put("Committee Member", "View", "Dashboard", "Events", "Content & Announcements", "Volunteers & Seva",
        "Governance Library", "Reports & Exports")
    put("Committee Member", "Edit", "Events", "Volunteers & Seva")
    put("Treasurer", "View", "Reports & Exports", "Members & Families", "Audit Log")
    put("Treasurer", "Approve", "Donations & Causes", "Issue Refund (two-actor)", "Dues Ledger & Aging",
        "Sponsors & Recognition")
    put("Communications", "View", "Events")
    put("Communications", "Edit", "Gallery & Media", "Notifications")
    put("Communications", "Approve", "Content & Announcements")
    put("Pathshala Coordinator", "View", "Members & Families")
    put("Pathshala Coordinator", "Edit", "Pathshala Rosters")
    put("Events Coordinator", "Edit", "Events", "Religious Calendar & Aarti", "Facility Booking",
        "Live Darshan", "Bhojanshala")
    put("Admin", "Edit", *[n for n in names if n not in ("Roles & Permissions", "Settings & Integrations")])
    put("Admin", "Approve", "Issue Refund (two-actor)")
    put("Super-Admin", "Approve", *names)
    return rb


RBAC = _rbac()
LEVEL_STYLES = {"None": ("EDEDED", "7F7F7F"), "View": ("CFE2F3", "1C4587"),
                "Edit": ("FFE599", "7F6000"), "Approve": ("D9EAD3", "274E13")}


def level_rules(ws, rng):
    for lvl, (bg, fg) in LEVEL_STYLES.items():
        ws.conditional_formatting.add(rng, CellIsRule(
            operator="equal", formula=[f'"{lvl}"'], font=Font(color=fg, bold=True),
            fill=PatternFill("solid", bgColor=bg)))


def green_red_rules(ws, rng, yes, no):
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[f'"{yes}"'], font=GREEN.font, fill=GREEN.fill))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[f'"{no}"'], font=RED.font, fill=RED.fill))


def build_feature_sheet(wb, idx, aud):
    """One table per audience. Returns {feature name: row}."""
    ws = wb.create_sheet(SHEETS[aud], idx)
    ncols = 6
    blurb = {
        "Guest": "What a visitor who is not logged in can see. Decide per feature whether it ships on Web, App, or both.",
        "Member": "What a logged-in member can do (phone app tabs + Explore More). Decide per feature: Web / App.",
        "Admin": "Admin utility sections (admin console navigation). Decide per feature: Web / App. Role access is on the RBAC sheet.",
    }[aud]
    row = write_title(ws, ncols, f"{AUD_LABELS[aud]} — features by platform", blurb + " Use the Yes/No dropdowns.")
    for c, v in enumerate(["#", "Section", "Feature", "Description", "Web", "App"], 1):
        ws.cell(row, c, v)
    style_header_row(ws, row, ncols)
    dv = DataValidation(type="list", formula1='"Yes,No"', allow_blank=False)
    ws.add_data_validation(dv)
    rows, r, n, cur, first = {}, row + 1, 0, None, None
    for sec, feat, desc, web, app, _ in DATA[aud]:
        if sec != cur:
            cur = sec
            ws.cell(r, 1, sec)
            for c in range(1, ncols + 1):
                ws.cell(r, c).fill, ws.cell(r, c).font = MODULE_FILL, MODULE_FONT
            r += 1
        first = first or r
        n += 1
        ws.cell(r, 1, n).alignment = CENTER
        ws.cell(r, 2, sec)
        ws.cell(r, 3, feat)
        ws.cell(r, 4, desc).alignment = Alignment(wrap_text=True, vertical="center")
        for c, v in ((5, web), (6, app)):
            cell = ws.cell(r, c, v)
            cell.alignment = CENTER
            dv.add(cell)
        for c in range(1, ncols + 1):
            ws.cell(r, c).border = THIN_BORDER
        rows[feat] = r
        r += 1
    last = r - 1
    for col in "EF":
        green_red_rules(ws, f"{col}{first}:{col}{last}", "Yes", "No")
    ws.cell(r, 3, "Features available (Yes)").font = Font(bold=True)
    for col in "EF":
        c = ws[f"{col}{r}"]
        c.value = f'=COUNTIF({col}{first}:{col}{last},"Yes")'
        c.font, c.alignment = Font(bold=True), CENTER
    for c in range(1, ncols + 1):
        ws.cell(r, c).border = Border(top=Side(style="medium", color="7A1620"))
    autosize(ws, [6, 24, 40, 52, 10, 10])
    return rows


def build_rbac(wb, idx, arows):
    ws = wb.create_sheet("RBAC", idx)
    nf = 3 + len(ROLES)
    row = write_title(ws, nf, "RBAC — Admin Utility access by role",
                      "None = no access · View = read only · Edit = create/change · Approve = edit + sign off "
                      "(money, publishing, role changes). Change any cell with its dropdown. Features come from the Admin Utility sheet.")
    for c, v in enumerate(["#", "Section", "Admin feature"] + ROLES, 1):
        ws.cell(row, c, v)
    style_header_row(ws, row, nf)
    ws.row_dimensions[row].height = 34
    dv = DataValidation(type="list", formula1='"' + ",".join(LEVELS) + '"', allow_blank=False)
    ws.add_data_validation(dv)
    r, first = row + 1, row + 1
    for n, (sec, feat, *_rest) in enumerate(ADMIN, 1):
        ar = arows[feat]
        ws.cell(r, 1, n).alignment = CENTER
        ws.cell(r, 2, f"='Admin Utility'!B{ar}")
        ws.cell(r, 3, f"='Admin Utility'!C{ar}")
        for i, role in enumerate(ROLES):
            cell = ws.cell(r, 4 + i, RBAC[role][feat])
            cell.alignment = CENTER
            dv.add(cell)
        for c in range(1, nf + 1):
            ws.cell(r, c).border = THIN_BORDER
        r += 1
    last = r - 1
    level_rules(ws, f"D{first}:{L(nf)}{last}")
    ws.cell(r, 3, "Features with any access").font = Font(bold=True)
    for i in range(len(ROLES)):
        col = L(4 + i)
        c = ws.cell(r, 4 + i, f'=COUNTIF({col}{first}:{col}{last},"<>None")')
        c.font, c.alignment = Font(bold=True), CENTER
    for c in range(1, nf + 1):
        ws.cell(r, c).border = Border(top=Side(style="medium", color="7A1620"))
    autosize(ws, [5, 16, 32] + [13] * len(ROLES))
    ws.freeze_panes = ws.cell(row + 1, 4)


def build_gantt(wb, idx, frows):
    ws = wb.create_sheet("Gantt", idx)
    FIX = 8
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
    for c, v in enumerate(["Audience", "Section", "Feature", "Web", "App", "Start", "End", "Weeks"], 1):
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

    r, blocks = 8, {}
    for p, aud in enumerate(("Guest", "Member", "Admin")):
        pr = r
        ws.cell(r, 1, AUD_LABELS[aud])
        for c in range(1, FIX + N_WEEKS + 1):
            ws.cell(r, c).fill, ws.cell(r, c).font = PHASE_ROW_FILL, MODULE_FONT
        r += 1
        f1 = r
        for sec, feat, _d_, _w, _a, key in DATA[aud]:
            m = frows[aud][feat]
            sh = SHEETS[aud]
            ws.cell(r, 1, AUD_LABELS[aud])
            ws.cell(r, 2, sec)
            ws.cell(r, 3, feat)
            for i, col in enumerate("EF"):
                ws.cell(r, 4 + i, f"=IF('{sh}'!{col}{m}=\"Yes\",\"Y\",\"N\")").alignment = CENTER
            ws.cell(r, 6, _d(SCHEDULE[key][0]))
            ws.cell(r, 7, _d(SCHEDULE[key][1]))
            ws.cell(r, 8, f"=ROUNDUP((G{r}-F{r}+1)/7,0)").alignment = CENTER
            for c in (6, 7):
                ws.cell(r, c).number_format = "dd-mmm-yy"
                ws.cell(r, c).fill = INPUT_FILL
                ws.cell(r, c).alignment = CENTER
            for c in range(1, FIX + 1):
                ws.cell(r, c).border = THIN_BORDER
            r += 1
        f2 = r - 1
        blocks[p] = (pr, f1, f2)
        ws.cell(pr, 6, f"=MIN(F{f1}:F{f2})")
        ws.cell(pr, 7, f"=MAX(G{f1}:G{f2})")
        ws.cell(pr, 8, f"=ROUNDUP((G{pr}-F{pr}+1)/7,0)")
        for c in (6, 7):
            ws.cell(pr, c).number_format = "dd-mmm-yy"
        for c in (6, 7, 8):
            ws.cell(pr, c).alignment = CENTER
    last_row = r - 1

    w0, w1 = L(W0), last_col
    for p, (pr, f1, f2) in blocks.items():
        feat_c, phase_c = BAR_COLORS[p]
        for rng, colr, top in ((f"{w0}{f1}:{w1}{f2}", feat_c, f1), (f"{w0}{pr}:{w1}{pr}", phase_c, pr)):
            ws.conditional_formatting.add(rng, FormulaRule(
                formula=[f"AND({w0}$6<=$G{top},{w0}$6+6>=$F{top})"],
                fill=PatternFill("solid", bgColor=colr), stopIfTrue=False))
    ws.conditional_formatting.add(f"{w0}8:{w1}{last_row}", FormulaRule(
        formula=[f"AND(TODAY()>={w0}$6,TODAY()<={w0}$6+6)"],
        border=Border(left=Side(style="thin", color="C0392B"), right=Side(style="thin", color="C0392B"))))
    green_red_rules(ws, f"D8:E{last_row}", "Y", "N")
    ws.freeze_panes = ws.cell(8, W0)
    autosize(ws, [20, 22, 38, 6, 6, 11, 11, 7])


def main():
    bad = sorted({f[-1] for d in DATA.values() for f in d if f[-1] not in SCHEDULE})
    if bad:
        raise SystemExit(f"No SCHEDULE entry for: {bad}")
    wb = load_workbook(XLSX)
    for name in ["Feature Matrix", "Gantt", "RBAC", *SHEETS.values()]:
        if name in wb.sheetnames:
            del wb[name]
    frows = {}
    for i, aud in enumerate(("Guest", "Member", "Admin")):
        frows[aud] = build_feature_sheet(wb, i, aud)
    build_rbac(wb, 3, frows["Admin"])
    build_gantt(wb, 4, frows)
    wb.save(XLSX)
    print(f"Sheets: {wb.sheetnames}")


if __name__ == "__main__":
    main()
