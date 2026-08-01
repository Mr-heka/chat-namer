#!/usr/bin/env python3
"""Render the grouped chat view: group, then project, then chats.

Reads a sessions dump on stdin (the JSON array from list_sessions) plus the
index built by build-index.py, writes groups.html and prints the path.

The desktop app's own sidebar groups are not reachable by any API, so this page
is where grouping actually happens.

Config: CHAT_NAMER_HOME (default ~/.chat-namer)
"""
import html
import json
import os
import re
import sys
import time

HOME = os.path.expanduser(os.environ.get("CHAT_NAMER_HOME", "~/.chat-namer"))
INDEX = os.path.join(HOME, "index.json")
OUT = os.path.join(HOME, "groups.html")

GROUP_ORDER = ["Builds", "Marketing", "Community", "Tools", "Systems",
               "Money", "Research", "Ungrouped"]

TITLE_RE = re.compile(
    r"^(\S+)\s+([A-Z0-9][A-Z0-9-]*)\s*(?:\((\S+?)(\d+)%\))?\s*(.*?)\s*/\s*(\d{1,2} \w{3})$")


def parse(title):
    """Split a swept title back into its parts. Unswept titles return None."""
    m = TITLE_RE.match(title.strip())
    if not m:
        return None
    lane, token, band, pct, topic, date = m.groups()
    return {"lane": lane, "token": token, "band": band,
            "pct": int(pct) if pct else None, "topic": topic, "date": date}


def project_block(token, chats, index):
    p = index.get(token, {})
    head = chats[0]
    badge = (f'<span class="badge">{head["band"]}{head["pct"]}%</span>'
             if head["pct"] is not None else "")
    kids = "".join(
        f'<li><span class="topic">{html.escape(c["topic"])}</span>'
        f'<span class="date">{html.escape(c["date"])}</span></li>'
        for c in sorted(chats, key=lambda c: c["date"], reverse=True))
    return (f'<section><h2><span class="lane">{head["lane"]}</span>'
            f'<span class="token">{html.escape(token)}</span>{badge}'
            f'<span class="count">{len(chats)}</span></h2>'
            f'<p class="slug">{html.escape(p.get("slug", "no project file"))}</p>'
            f'<ul>{kids}</ul></section>')


def main():
    sessions = json.load(sys.stdin)
    index = {p["token"]: p for p in json.load(open(INDEX))["projects"]}

    projects, unswept = {}, []
    for s in sessions:
        parts = parse(s.get("title", ""))
        if parts:
            projects.setdefault(parts["token"], []).append({**parts, **s})
        else:
            unswept.append(s)

    buckets = {}
    for token, chats in projects.items():
        buckets.setdefault(index.get(token, {}).get("group", "Ungrouped"), []) \
               .append((token, chats))

    # Least-finished project first inside each group: the thing needing attention
    # rises, which is the opposite of the sidebar and the point of this page.
    def rank(item):
        pct = item[1][0]["pct"]
        return (pct if pct is not None else 999, item[0])

    order = ([g for g in GROUP_ORDER if g in buckets] +
             sorted(g for g in buckets if g not in GROUP_ORDER))

    rows = []
    for g in order:
        n = sum(len(c) for _, c in buckets[g])
        rows.append(f'<h1 class="grp">{html.escape(g)}'
                    f'<span class="gcount">{n} chat{"s" if n > 1 else ""}</span></h1>')
        rows += [project_block(t, c, index) for t, c in sorted(buckets[g], key=rank)]

    if unswept:
        rows.append(f'<h1 class="grp">Not swept yet'
                    f'<span class="gcount">{len(unswept)}</span></h1>')
        kids = "".join(f'<li><span class="topic">{html.escape(s["title"])}</span></li>'
                       for s in unswept)
        rows.append(f'<section class="loose"><ul>{kids}</ul></section>')

    open(OUT, "w").write(
        TEMPLATE.replace("{{ROWS}}", "".join(rows))
                .replace("{{STAMP}}", time.strftime("%-d %b %H:%M"))
                .replace("{{G}}", str(len(buckets)))
                .replace("{{N}}", str(len(projects))))
    print(OUT)


TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Chats by group</title><style>
:root{--ink:#151227;--paper:#FAF9FC;--card:#fff;--muted:#6E6786;--line:#E6E2F0;--accent:#6736E2}
@media(prefers-color-scheme:dark){:root{--ink:#EBE8F4;--paper:#0F0D18;--card:#181528;--muted:#9891AC;--line:#2A2540;--accent:#9B7BF0}}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 Manrope,system-ui,sans-serif}
.wrap{max-width:640px;margin:0 auto;padding:40px 20px 80px}
header{margin-bottom:26px}
h1.title{margin:0 0 4px;font-size:24px;font-weight:800;letter-spacing:-.02em}
.stamp{color:var(--muted);font-size:13px}
h1.grp{display:flex;align-items:baseline;gap:10px;margin:30px 0 10px;
  font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}
h1.grp:first-of-type{margin-top:0}
.gcount{margin-left:auto;font-size:11px;font-weight:700;letter-spacing:.04em;
  text-transform:none;color:var(--muted)}
section{background:var(--card);border:1px solid var(--line);border-radius:10px;
  padding:13px 15px;margin-bottom:8px}
h2{margin:0;font-size:15px;font-weight:800;display:flex;align-items:center;gap:8px}
.lane{font-size:17px}
.badge{font-size:12.5px;font-weight:700;font-variant-numeric:tabular-nums}
.count{margin-left:auto;font-size:12px;font-weight:600;color:var(--muted)}
.slug{margin:3px 0 0;font-size:12px;color:var(--muted);font-family:ui-monospace,Menlo,monospace}
ul{margin:9px 0 0;padding:0;list-style:none}
li{display:flex;gap:12px;padding:5px 0;border-top:1px solid var(--line);font-size:14px}
.topic{flex:1}
.date{color:var(--muted);font-size:12.5px;font-variant-numeric:tabular-nums;white-space:nowrap}
.loose{opacity:.65}
</style></head><body><div class="wrap">
<header><h1 class="title">Chats by group</h1>
<div class="stamp">{{G}} groups · {{N}} projects · least finished first · {{STAMP}}</div></header>
{{ROWS}}
</div></body></html>"""


if __name__ == "__main__":
    main()
