# Chat naming convention

Edit this file to change how chats get named. The skill reads it every run.

## Format

```
<lane emoji> <PROJECT> (<band><pct>%) <chat topic> / <date>
```

Example: `🎤 WORKSHOPS (🟠66%) Queenstown / 24 Jul`

Tight. No space inside the bracket, no separator after it, no dots anywhere. The
bracket is the only punctuation that earns its place, because it fences the health
reading off from the words. Everything else is a single slash.

When `pct` is `null`, drop the bracket entirely: `📣 CRM Access map / 9 Jul`.

- **Lane emoji**: one character, from the map below. Colour you scan before you
  read a word.
- **PROJECT**: the `token` field from the index, always caps. This is the group.
  Every chat on the same project carries the same token, which is what makes it
  read as a column down the sidebar. Never invent one, look it up.
- **band + pct**: the project's `band` and `pct`, not this chat's. Six chats on one
  project all show the same number, because it is the project that is 58% done, not
  the conversation. Drop both when `pct` is `null` (a reference doc with no
  checkboxes; `0%` would read as abandoned work).
- **Chat topic**: what this one conversation is doing, in two or three words.
  Lower case, so the caps token stays the thing the eye catches.
- **Date**: last activity, `1 Aug` style, in the user's local timezone.

## Band

| Button | Range | Reads as |
|---|---|---|
| ⚫ | 0% | Nobody has started |
| 🔴 | 1 to 24% | Barely begun |
| 🟠 | 25 to 49% | Early |
| 🟡 | 50 to 74% | Past halfway |
| 🟢 | 75 to 99% | Nearly there |
| ✅ | 100% | Done, safe to archive |

Black is deliberately not red. A project nobody has opened is a different problem
from one that started and stalled, and the sidebar should say which.

The button is the whole point of the number: a stalled project should be visible
while scrolling past it, without reading a single digit.

## Rules

- **The token is never freestyled.** If no project in the index matches with
  confidence, prefix `❓` instead and leave the rest of the title alone. A wrong
  project is worse than an unfiled one.
- **48 characters max.** Past that the sidebar truncates, and a truncated name is
  a useless name. Cut the topic, never the token.
- **No `x/y` counts.** The band and the percentage replaced them. Raw checkbox
  counts live in the project file where they belong.
- **No verbs.** "Fixing the invoice holds" and "invoice holds" carry the same
  information; one of them fits.
- **Plain nouns.** `GC workshop ads`, not `Gold Coast workshop advertising
  campaign relaunch`.

## Lane emoji map

Fifteen lanes, because seven meant one emoji swallowed a third of the list and
told you nothing. Keep them visually distinct: never two parcels, never two screens.

| Emoji | Lane | Covers |
|---|---|---|
| 🏫 | Community | Membership, classroom, forum |
| 🌐 | Websites | Landing pages, sites, domains, hosting |
| 📦 | Skills & tools | Skills, internal tooling, MCP servers |
| 🧰 | Workflows | Automations, routines, cron, pipelines |
| 📣 | Ads | Campaigns, adsets, creative testing, audiences, pixel |
| 🎬 | Video | Reels, footage, edits, editing suites |
| 🎨 | Design | Carousels, brand, covers, banners, images |
| ✉️ | Email & SMS | Flows, nurture, sequences, inbox |
| 💰 | Money | Accounting, invoices, payroll, pricing |
| 🔧 | Infra | Servers, source control, sync, auth, installs |
| 🤖 | Agents | Background agents, autonomous loops, memory |
| 🎤 | Events | Workshops, attendees, the room |
| 🤝 | People | Clients, team, hiring, sales, outreach |
| 🔍 | Research | Audits, comparisons, strategy reading |
| 🎯 | Build | Anything genuinely new that fits nowhere above |

The lane comes from the project's index entry, not from the chat. Every chat on a
project shares its lane, which is what keeps the column readable.

The keywords that map a project into a lane live at the top of
`scripts/build-index.py`. Add your own vocabulary there.

## Worked examples

| Auto-title | Renamed |
|---|---|
| Business models dashboard research | 🎯 BIZMODEL (🟢76%) V5 React port / 1 Aug |
| Infrastructure tools assessment | 🤖 AGENTS (🟡73%) infra review / 1 Aug |
| Customer testimonial videos and transcripts | 🎤 TESTIMONY (🟡53%) video cuts / 1 Aug |
| Community integration mapping | 🏫 COMMUNITY (🟡58%) Zapier auth / 1 Aug |
| Link tree profile research | 🎯 LINKS (🟡60%) bio page / 1 Aug |
| Team chat asks | 🤝 TEAM (⚫0%) inbound requests / 1 Aug |
