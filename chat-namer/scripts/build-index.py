#!/usr/bin/env python3
"""Build the project registry the chat namer matches sessions against.

Reads a folder of markdown project files, writes index.json.
Never hand-edit the output. Re-run this instead.

Config, both optional:
  CHAT_NAMER_SOURCES  colon-separated globs   (default: ~/claude-projects/*.md)
  CHAT_NAMER_HOME     where index.json lands  (default: ~/.chat-namer)
"""
import glob
import json
import os
import re
import time

HOME = os.path.expanduser(os.environ.get("CHAT_NAMER_HOME", "~/.chat-namer"))
SOURCES = [os.path.expanduser(s) for s in os.environ.get(
    "CHAT_NAMER_SOURCES", "~/claude-projects/*.md").split(":") if s.strip()]
OUT = os.path.join(HOME, "index.json")

# First match wins, so order is the whole design here. Narrow lanes beat broad
# ones: a lane that catches a third of your projects tells you nothing at a
# glance. Add your own vocabulary to these lines.
LANES = [
    ("\U0001F3EB", "community membership classroom forum school circle"),
    ("\U0001F310", "website websites landing lp page site domain hosting vercel netlify framer"),
    ("\U0001F4E6", "skill skills kit toolkit tooling mcp plugin extension"),
    ("\U0001F9F0", "workflow workflows automation routine cron pipeline zapier n8n make"),
    ("\U0001F4E3", "ad ads campaign adset creative retargeting audience pixel"),
    ("\U0001F3AC", "video reel reels footage clip edit editing render"),
    ("\U0001F3A8", "carousel design brand banner cover graphic image logo"),
    ("✉️", "email flow flows nurture sequence newsletter inbox sms"),
    ("\U0001F4B0", "finance accounting invoice invoices payroll billing pricing tax"),
    ("\U0001F527", "infra server hosting github git sync auth access install setup migration"),
    ("\U0001F916", "agent agents autonomous loop memory bot"),
    ("\U0001F3A4", "workshop workshops event events attendee attendees talk"),
    ("\U0001F91D", "team client clients hiring hire onboarding sales pipeline crm outreach proposal"),
    ("\U0001F50D", "audit research gap scope strategy analysis review"),
]
DEFAULT_LANE = "\U0001F3AF"

# Sections for the grouped view only. The desktop app's own sidebar groups live in
# its Local Storage and no API reaches them, so those stay manual. Keep this list
# coarser than the lanes: fifteen collapsed sections is worse than seven.
GROUPS = [
    ("Builds",    "\U0001F3AF\U0001F310"),
    ("Marketing", "\U0001F4E3\U0001F3AC\U0001F3A8✉️"),
    ("Community", "\U0001F3EB\U0001F3A4\U0001F91D"),
    ("Tools",     "\U0001F4E6\U0001F9F0"),
    ("Systems",   "\U0001F916\U0001F527"),
    ("Money",     "\U0001F4B0"),
    ("Research",  "\U0001F50D"),
]

# Words too generic to identify a project, dropped before picking its token.
STOP = set("""the a an and of for to with system project build rebuild revamp
cleanup overhaul dashboard handover handoff plan spec execution batch final new
v2 v3 md 2024 2025 2026 phase""".split())

# Force a token for a project whose filename picks a bad one. slug -> TOKEN.
OVERRIDE = {}


def lane_for(words):
    for emoji, keys in LANES:
        if words & set(keys.split()):
            return emoji
    return DEFAULT_LANE


def group_for(lane):
    for name, lanes in GROUPS:
        if lane in lanes:
            return name
    return "Ungrouped"


def token_for(slug):
    if slug in OVERRIDE:
        return OVERRIDE[slug]
    for w in slug.split("-"):
        if w.lower() not in STOP and not w.isdigit() and len(w) > 2:
            return w.upper()[:12]
    return slug.split("-")[0].upper()[:12]


def band_for(pct):
    """Six-step heat ramp. None stays None so a reference doc with no checkboxes
    never shows up as stalled work. Black reads as untouched rather than failing,
    which is a different problem from a project that started and stopped."""
    if pct is None:
        return None
    if pct >= 100:
        return "✅"
    if pct >= 75:
        return "\U0001F7E2"
    if pct >= 50:
        return "\U0001F7E1"
    if pct >= 25:
        return "\U0001F7E0"
    if pct >= 1:
        return "\U0001F534"
    return "⚫"


def heading(text):
    m = re.search(r"^#\s+(.+)$", text, re.M)
    if m:
        return re.sub(r"\s*[—-].*$", "", m.group(1)).strip()[:48]
    m = re.search(r"^(?:project|title):\s*(.+)$", text, re.M)
    return m.group(1).strip()[:48] if m else ""


def main():
    os.makedirs(HOME, exist_ok=True)
    projects = []
    for path in sorted({p for src in SOURCES for p in glob.glob(src)}):
        name = os.path.basename(path)
        if name.startswith("_") or not name.endswith(".md"):
            continue
        slug = name[:-3]
        text = open(path, encoding="utf-8", errors="replace").read()
        open_n = len(re.findall(r"^\s*[-*]\s*\[[ ~]\]", text, re.M))
        done_n = len(re.findall(r"^\s*[-*]\s*\[[xX]\]", text, re.M))
        pct = round(done_n * 100 / (done_n + open_n)) if (done_n + open_n) else None
        title = heading(text)
        words = {w for w in re.split(r"[-_\s]+", (slug + " " + title).lower()) if w}
        lane = lane_for(words)
        projects.append({
            "slug": slug,
            "token": token_for(slug),
            "lane": lane,
            "group": group_for(lane),
            "display": title or slug.replace("-", " "),
            "aliases": sorted(w for w in words if w not in STOP and len(w) > 2),
            "open": open_n,
            "done": done_n,
            "pct": pct,
            "band": band_for(pct),
            "updated": time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(path))),
        })

    # Two projects sharing a token defeats the whole point of the caps block.
    # Freshest keeps the short token, the rest widen. The shared prefix still
    # clusters them in the sidebar.
    projects.sort(key=lambda p: p["updated"], reverse=True)
    seen = set()
    for p in projects:
        base = p["token"]
        if base not in seen:
            seen.add(base)
            continue
        extra = next((w.upper()[:6] for w in p["slug"].split("-")[1:]
                      if w.lower() not in STOP and len(w) > 2), None)
        p["token"] = (f"{base}-{extra}" if extra else f"{base}-2")[:14]
        seen.add(p["token"])

    json.dump({"generated": time.strftime("%Y-%m-%d %H:%M"),
               "count": len(projects), "projects": projects},
              open(OUT, "w"), indent=1, ensure_ascii=False)
    print(f"{len(projects)} projects -> {OUT}")
    if not projects:
        print(f"no project files matched {SOURCES} — every chat will be titled ❓ "
              f"until some exist, which is fine")


if __name__ == "__main__":
    main()
