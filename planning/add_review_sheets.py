#!/usr/bin/env python3
"""Adds Feature Inventory, Site Coverage and Mock Questionnaire sheets to JCA_UserStories_v2.xlsx.

- Feature Inventory: one list of independent features, Yes/No for Guest and Signed-in.
  Derived from the Guest / Member lists in add_feature_sheets.py (duplicates merged).
- Site Coverage: nyjaincenter.org site map (scraped 2026-10-07) vs. the mockup pages in the repo root.
- Mock Questionnaire: open questions for the team with a Response column to fill in.

The xlsx is hand-edited, so this opens it in place and only replaces its own three sheets.
Run: uv run --no-project --with openpyxl python add_review_sheets.py
"""
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

from add_feature_sheets import GUEST, MEMBER, CENTER, INPUT_FILL, green_red_rules
from build_workbook_v2 import (
    MODULE_FILL, MODULE_FONT, THIN_BORDER, autosize, style_header_row, write_title,
)

XLSX = Path(__file__).parent / "JCA_UserStories_v2.xlsx"
NAMES = ["Feature Inventory", "Site Coverage", "Mock Questionnaire"]
TOP = Alignment(wrap_text=True, vertical="top")
TOTAL_BORDER = Border(top=Side(style="medium", color="7A1620"))

# Member feature -> Guest feature it duplicates (merged into one row)
MERGE = {
    "Parva days": "Sacred calendar",
    "News & newsletters": "News & events feed",
    "Donate to a cause": "Guest one-time donation",
    "Jain philosophy module": "Jain philosophy intro",
    "Live Darshan": "Public live stream & aarti schedule",
}
# Guest features that stop making sense once signed in
GUEST_ONLY = {"Sign in", "Create account / register"}
RENAME = {"Guest one-time donation": "One-time donation", "Public live stream & aarti schedule": "Live darshan & aarti schedule"}


def inventory_rows():
    rows = {}  # feature -> [section, feature, desc, guest, signed_in]
    for sec, feat, desc, *_ in GUEST:
        rows[feat] = [sec, RENAME.get(feat, feat), desc, "Yes", "No" if feat in GUEST_ONLY else "Yes"]
    for sec, feat, desc, *_ in MEMBER:
        if feat in MERGE:
            continue
        rows[feat] = [sec, feat, desc, "No", "Yes"]
    return list(rows.values())


def build_inventory(wb, idx):
    ws = wb.create_sheet(NAMES[0], idx)
    ncols = 7
    r = write_title(ws, ncols, "Feature Inventory — Guest vs Signed-in",
                    "Every independent feature once. Mark Guest / Signed-in = Yes or No with the dropdowns; "
                    "'Access' updates itself (Both / Guest only / Signed-in only). Web vs App lives on the Guest / Member sheets.")
    for c, v in enumerate(["#", "Section", "Feature", "Description", "Guest", "Signed-in", "Access"], 1):
        ws.cell(r, c, v)
    style_header_row(ws, r, ncols)
    dv = DataValidation(type="list", formula1='"Yes,No"', allow_blank=False)
    ws.add_data_validation(dv)
    r += 1
    first, n, cur = r, 0, None
    for sec, feat, desc, g, s in inventory_rows():
        if sec != cur:
            cur = sec
            ws.cell(r, 1, sec)
            for c in range(1, ncols + 1):
                ws.cell(r, c).fill, ws.cell(r, c).font = MODULE_FILL, MODULE_FONT
            r += 1
        n += 1
        ws.cell(r, 1, n).alignment = CENTER
        ws.cell(r, 2, sec)
        ws.cell(r, 3, feat)
        ws.cell(r, 4, desc).alignment = Alignment(wrap_text=True, vertical="center")
        for c, v in ((5, g), (6, s)):
            ws.cell(r, c, v).alignment = CENTER
            dv.add(ws.cell(r, c))
        ws.cell(r, 7, f'=IF(AND(E{r}="Yes",F{r}="Yes"),"Both",IF(E{r}="Yes","Guest only",IF(F{r}="Yes","Signed-in only","—")))').alignment = CENTER
        for c in range(1, ncols + 1):
            ws.cell(r, c).border = THIN_BORDER
        r += 1
    last = r - 1
    for col in "EF":
        green_red_rules(ws, f"{col}{first}:{col}{last}", "Yes", "No")
    ws.cell(r, 3, "Features marked Yes").font = Font(bold=True)
    for col in "EF":
        c = ws[f"{col}{r}"]
        c.value = f'=COUNTIF({col}{first}:{col}{last},"Yes")'
        c.font, c.alignment = Font(bold=True), CENTER
    ws.cell(r + 1, 3, "Both / Guest only / Signed-in only").font = Font(bold=True)
    for col, k in zip("EFG", ("Both", "Guest only", "Signed-in only")):
        c = ws[f"{col}{r + 1}"]
        c.value = f'=COUNTIF($G{first}:$G{last},"{k}")'
        c.font, c.alignment = Font(bold=True), CENTER
    for c in range(1, ncols + 1):
        ws.cell(r, c).border = TOTAL_BORDER
    autosize(ws, [6, 24, 40, 52, 11, 11, 16])
    ws.freeze_panes = ws.cell(first, 1)


Y, N = "Yes", "No"
B = "https://nyjaincenter.org"
# (menu, page, original path, built?, mockup location, notes)
COVERAGE = [
    ("News & Events", [
        ("News & Events", "/News-Events", Y, "festivals.html#news", ""),
        ("Calendar", "/Calendar", Y, "festivals.html#calendar", "Mega-menu 'See the calendar →' points to #diwali, which does not exist on the page."),
        ("Newsletters", "/Newsletters", Y, "festivals.html#newsletters", "Archive of issues listed; no real PDFs."),
        ("Email Subscription", "/Newsletters#tabs2", Y, "festivals.html#newsletters (fn-email)", "Sign-up field only; no back-end."),
    ]),
    ("Gallery", [
        ("Gallery (landing)", "/Gallery", Y, "gallery.html", ""),
        ("Photo Gallery", "/Gallery", Y, "gallery.html#photos, #albums", "Original uses Picasa/FancyBox albums."),
        ("Video Gallery", "/Gallery", N, "Link-out only: YouTube channel", "No in-site video gallery; mega-menu links to youtube.com/user/jaincenterny."),
    ]),
    ("Traditions", [
        ("Traditions (landing)", "/Traditions", Y, "worship.html", "Renamed 'Worship' in the mockup nav."),
        ("Mahavir Swami Temple", "/Traditions/Mahavir-Temple", Y, "worship.html#mahavir-temple", ""),
        ("Adinathji Temple", "/Traditions/Adinath-Temple", Y, "worship.html#adinath-temple", ""),
        ("Upashray Lecture Hall", "/Traditions/Sthanak-Upashray", Y, "worship.html#sthanak-upashray", ""),
        ("Shrimad Hall", "/Traditions/Shrimad-Rajchandra", Y, "worship.html#shrimad-rajchandra", ""),
        ("Dadawadi", "/Traditions/Dadawadi", Y, "worship.html#dadawadi", ""),
    ]),
    ("Members", [
        ("Members (landing)", "/Members", Y, "belong.html", "Renamed 'Belong' in the mockup nav."),
        ("Account Login", "/Members/Account-Login", Y, "login.html", ""),
        ("New Account", "/Members/New-Account", Y, "belong.html#account", ""),
        ("Become a Member", "/Members/Become-a-JCA-Member", Y, "belong.html#member", ""),
        ("Donate to JCA", "/Members/Donate-to-JCA", Y, "give.html#donate", "Zelle details shown; online form not built."),
        ("Matching Donation", "/Members/Matching-Donation", Y, "give.html#matching", "Explanatory text only. The original embeds the Double the Donation employer-search widget (see Mock Questionnaire Q1)."),
        ("Sponsor Bhojanshala", "/Members/Sponsor-Bhojanshala", Y, "give.html#sponsor, #bhojanshala", "No sponsor list / date picker like the original home-page Bhojanshala sponsors list."),
        ("Youth Group", "/Members/Youth-Group", Y, "belong.html#youth", ""),
        ("Senior Group", "/Members/Senior-Group", Y, "belong.html#senior", ""),
        ("Volunteer Sign Up", "/Members/Volunteer-Sign-Up", Y, "belong.html#volunteer", "Interest form."),
    ]),
    ("Education", [
        ("Education (landing)", "/Education", Y, "learn.html", "Renamed 'Learn' in the mockup nav."),
        ("Scholars", "/Education/Scholars", Y, "learn.html#scholars", ""),
        ("Lecture Series", "/Education/Lecture-Series", Y, "learn.html#lecture-series", ""),
        ("Art Gallery", "/Education/Art-Gallery", Y, "learn.html#art-gallery", ""),
        ("Temple Artwork", "/Education/Temple-Artwork", Y, "learn.html#temple-artwork", ""),
        ("Idols & Pat", "/Education/Idols--Pat", Y, "learn.html#idols-pat", ""),
        ("Ashtapad Research", "/Education/Books-at-Library", Y, "learn.html#ashtapad", ""),
        ("Pathshala Activities", "/Education/Religious-Links", Y, "belong.html#pathshala, learn.html#resources", ""),
        ("Publications & Articles", "/Education/Downloads", N, "learn.html#resources", "Placeholder: 'Coming soon'."),
        ("Library Books", "/Education/Library-Books", N, "learn.html#resources", "Description only; online catalogue 'coming soon'."),
        ("Google Virtual Tour", "/Education/Google-Virtual-Tour", Y, "gallery.html#tour", ""),
        ("Jain Websites", "/Education/Jain-Websites", Y, "learn.html#jain-websites", ""),
        ("Downloads", "/Education/Downloads2", N, "learn.html#resources", "Placeholder: 'Coming soon'."),
    ]),
    ("About Us", [
        ("About Us (landing)", "/About-Us", Y, "story.html", "Renamed 'Our Story' in the mockup nav."),
        ("About JCA", "/About-Us/About-JCA", Y, "story.html#about-jca", ""),
        ("Google Virtual Tour", "/About-Us/Google-Virtual-Tour", Y, "gallery.html#tour", "Same page as the Education link."),
        ("JCA History", "/About-Us/JCA-History", Y, "story.html#history", ""),
        ("JCA Mission", "/About-Us/JCA-Mission", Y, "story.html#mission", ""),
        ("Chairman's Message", "/About-Us/Chairmans-Message", Y, "story.html#chairman", ""),
        ("Board of Trustees", "/About-Us/Board-of-Trustees", Y, "story.html#leadership", ""),
        ("President's Message", "/About-Us/Presidents-Message", Y, "story.html#president", ""),
        ("Executive Committee", "/About-Us/Executive-Committee", Y, "story.html#executive", ""),
        ("JCA Policies / By Laws", "/About-Us/JCA-Policies-or-By-Laws", Y, "story.html#governance", "Policy cards only (Facility Use, Code of Conduct, Elections); By-Laws itself is not listed; no documents to open."),
        ("Financial Statements", "/About-Us/Financial-Statements", Y, "story.html#governance", "Card only; no statements to open."),
        ("JCA Annual Meetings", "/About-Us/JCA-Annual-Meetings", Y, "story.html#governance", "Card only; no minutes."),
        ("Contact Us", "/Contact-Us", Y, "story.html#contact", "Address, phone, e-mail, hours; no contact form."),
    ]),
    ("Footer & utility pages", [
        ("Jain Calendar", "/Jain-Calendar", N, "—", "Not in the mockup (festival calendar exists, but no separate Jain Calendar page)."),
        ("Jain Centers", "/Jain-Centers", Y, "phone.html (Jain Centers USA)", "App mockup only; not on the web mockup."),
        ("Jain Websites", "/Jain-Websites", Y, "learn.html#jain-websites", "Same page as the Education link."),
        ("Terms of Use", "/Terms-of-Use", N, "—", "No page or footer link."),
        ("Privacy Policy", "/Privacy-Policy", N, "—", "No page or footer link."),
        ("Site map", "/SiteMap", N, "—", "Not built; mega-menus and drawer cover navigation."),
    ]),
    ("Site-wide widgets", [
        ("Home: Google Calendar event list", "(home page)", N, "—", "Home page mockup does not pull a live calendar."),
        ("Home: Bhojanshala sponsors list", "(home page)", N, "—", "Not shown on the mockup home page."),
        ("Home: coupon / cover pop-up", "(home page)", N, "—", "CoverPop.js pop-up on the original."),
        ("Google Translate", "(header)", N, "—", "See Mock Questionnaire (translation vs. planned Hindi/Gujarati)."),
        ("Google site search", "(header)", N, "—", "Original loads Google CSE; no search box in the mockup."),
        ("Accessibility widget (UserWay)", "(all pages)", N, "—", "Third-party plugin cdn.userway.org/widget.js. See Mock Questionnaire Q2."),
        ("Social links", "(footer)", Y, "Footer on every page", "Facebook, Twitter, Pinterest, YouTube."),
        ("Zelle donation info", "(footer)", Y, "give.html#donate; give mega-menu", ""),
        ("Temple timings & daily aarti", "(footer)", Y, "story.html#contact; mega-menus", ""),
        ("Directions to JCA (map link)", "(footer)", Y, "story.html#contact", ""),
    ]),
]


def build_coverage(wb, idx):
    ws = wb.create_sheet(NAMES[1], idx)
    ncols = 7
    r = write_title(ws, ncols, "Site Coverage — nyjaincenter.org vs. our mockup",
                    "Original site map (scraped 7 Oct 2026) compared with the mockup pages. 'In mockup?' = No means the page or content is "
                    "missing or only a placeholder. Comparison only; nothing built here.")
    for c, v in enumerate(["#", "Original menu", "Original page", "Original URL", "In mockup?", "Mockup location", "Notes"], 1):
        ws.cell(r, c, v)
    style_header_row(ws, r, ncols)
    dv = DataValidation(type="list", formula1='"Yes,No"', allow_blank=False)
    ws.add_data_validation(dv)
    r += 1
    first, n = r, 0
    for menu, items in COVERAGE:
        ws.cell(r, 1, menu)
        for c in range(1, ncols + 1):
            ws.cell(r, c).fill, ws.cell(r, c).font = MODULE_FILL, MODULE_FONT
        r += 1
        for page, path, built, loc, note in items:
            n += 1
            ws.cell(r, 1, n).alignment = Alignment(horizontal="center", vertical="top")
            ws.cell(r, 2, menu).alignment = TOP
            ws.cell(r, 3, page).alignment = TOP
            url = ws.cell(r, 4, path if path.startswith("(") else B + path)
            url.alignment = TOP
            if path.startswith("/"):
                url.hyperlink = B + path
                url.font = Font(color="0563C1", underline="single")
            cell = ws.cell(r, 5, built)
            cell.alignment = Alignment(horizontal="center", vertical="top")
            dv.add(cell)
            ws.cell(r, 6, loc).alignment = TOP
            ws.cell(r, 7, note).alignment = TOP
            for c in range(1, ncols + 1):
                ws.cell(r, c).border = THIN_BORDER
            r += 1
    last = r - 1
    green_red_rules(ws, f"E{first}:E{last}", "Yes", "No")
    ws.cell(r, 3, "Covered in mockup").font = Font(bold=True)
    ws.cell(r, 5, f'=COUNTIF(E{first}:E{last},"Yes")&" of "&COUNTA(E{first}:E{last})').font = Font(bold=True)
    ws.cell(r, 5).alignment = CENTER
    ws.cell(r + 1, 3, "Not built").font = Font(bold=True)
    ws.cell(r + 1, 5, f'=COUNTIF(E{first}:E{last},"No")').font = Font(bold=True)
    ws.cell(r + 1, 5).alignment = CENTER
    for c in range(1, ncols + 1):
        ws.cell(r, c).border = TOTAL_BORDER
    autosize(ws, [6, 20, 32, 46, 12, 38, 62])
    ws.freeze_panes = ws.cell(first, 1)


# (topic, question, context)
QUESTIONS = [
    ("Matching donation",
     "What is matching donation, and how are we going to implement it in the new website and app?",
     "Today /Members/Matching-Donation explains employer matching and embeds the Double the Donation employer-search widget "
     "(\"Matching Gift and Volunteer Grant information provided by Double the Donation\"). The mockup (give.html#matching) has the text only. "
     "Options: keep the third-party embed, link out to it, or build our own flow (employer lookup + match request). Who owns the account?"),
    ("Accessibility",
     "The original site has an accessibility icon that opens settings (contrast, larger text, hide images). It is a separate plugin, not part of JCA's own pages. "
     "Is it necessary for us to implement this ourselves in the new site and app?",
     "The plugin is UserWay (cdn.userway.org/widget.js). If not required, a WCAG 2.1 AA build plus browser / OS settings covers most needs. "
     "If required: keep a third-party widget, or build our own settings panel (font size, contrast, hide images)? Mobile app would rely on OS accessibility settings."),
    ("Translation & language",
     "The original site uses a Google Translate widget. Do we keep an automatic translate option, or rely on our planned Hindi and Gujarati localization?",
     "Original loads /Frontend/Scripts/GoogleTranslater.js. Not in the mockup. Roadmap has Hindi/Gujarati as a Phase 2 item."),
    ("Search",
     "Does the new site need site-wide search?",
     "The original has a Google Custom Search box. The mockup has none."),
    ("Home page widgets",
     "Should the new home page show the live calendar list, the weekly Bhojanshala sponsors list and the pop-up banner that the current home page has?",
     "Original home page loads HomePageGoogleCalendarList.js, HomePageBhojanshalaSponsorsList.js and CoverPop.js (pop-up)."),
    ("Legacy pages",
     "Do the Jain Calendar, Jain Centers, Terms of Use, Privacy Policy and Site map pages carry over? Who provides the Terms / Privacy text?",
     "All five exist on the original footer. Not built in the web mockup (Jain Centers exists in the app mockup only)."),
    ("Placeholder content",
     "Who supplies the content for Publications & Articles, Downloads, Library Books catalogue, By-Laws, Financial Statements and Annual Meeting minutes?",
     "These pages are 'coming soon' or text-only in the mockup (see Site Coverage sheet, rows marked No)."),
]


def build_questionnaire(wb, idx):
    ws = wb.create_sheet(NAMES[2], idx)
    ncols = 7
    r = write_title(ws, ncols, "Mock Questionnaire — open questions for the team",
                    "Questions on the left; the team writes answers in the yellow Response column (plus name and date).")
    for c, v in enumerate(["#", "Topic", "Question", "Context / reference", "Response", "Responded by", "Date"], 1):
        ws.cell(r, c, v)
    style_header_row(ws, r, ncols)
    r += 1
    for n, (topic, q, ctx) in enumerate(QUESTIONS, 1):
        ws.cell(r, 1, n).alignment = Alignment(horizontal="center", vertical="top")
        ws.cell(r, 2, topic).alignment = TOP
        ws.cell(r, 3, q).alignment = TOP
        ws.cell(r, 4, ctx).alignment = TOP
        for c in (5, 6, 7):
            ws.cell(r, c).fill = INPUT_FILL
            ws.cell(r, c).alignment = TOP
        ws.cell(r, 7).number_format = "dd-mmm-yy"
        for c in range(1, ncols + 1):
            ws.cell(r, c).border = Border(bottom=Side(style="thin", color="D9CBB0"))
        ws.row_dimensions[r].height = 120
        r += 1
    autosize(ws, [5, 20, 52, 62, 52, 18, 12])


def main():
    wb = load_workbook(XLSX)
    for name in NAMES:
        if name in wb.sheetnames:
            del wb[name]
    idx = wb.sheetnames.index("Gantt") + 1
    build_inventory(wb, idx)
    build_coverage(wb, idx + 1)
    build_questionnaire(wb, idx + 2)
    wb.save(XLSX)
    print(wb.sheetnames)


if __name__ == "__main__":
    main()
