# Chat Namer

**Your Claude Code sidebar, readable at a glance.**

Claude names a chat from your opening message. That first message is the vaguest
thing in the whole conversation, so after a week the sidebar looks like this:

```
Business models dashboard research
Infrastructure tools assessment
Agent folder structure and Markdown workflow
Community platform integration mapping
```

All true. All useless. You open three of them to find the one you wanted.

This skill renames them to what they actually became:

```
🎯 BIZMODEL (🟢76%) V5 React port / 1 Aug
🤖 AGENTS (🟡73%) infra review / 1 Aug
🧰 WORKFLOWS (🟢79%) md spine / 1 Aug
🏫 COMMUNITY (🟡58%) Zapier auth / 1 Aug
```

Reading left to right: what kind of work it is, which project it belongs to, how
far along that project is, what this particular chat is doing, when you last
touched it.

## Who it's for

Anyone running more than about five Claude Code chats at once. If you keep several
conversations going on the same project, this is what stops them blurring together.
Every chat on a project carries the same tag and the same percentage, so they read
as one block instead of four unrelated lines.

## Install

Copy the `chat-namer` folder into your skills directory:

```bash
mkdir -p ~/.claude/skills && cp -r chat-namer ~/.claude/skills/
```

Then tell it where your projects live. One markdown file per project, anywhere you
like, with checkboxes for progress:

```markdown
# Gold Coast workshop

- [x] Venue booked
- [x] Landing page live
- [ ] Ads running
```

```bash
echo 'export CHAT_NAMER_SOURCES="$HOME/claude-projects/*.md"' >> ~/.zshrc
```

Use `~/.bashrc` if you're on bash. Restart Claude afterwards so it picks the
variable up, then ask it to "rename my chats" and it sweeps them.

Skip that step entirely and it reads `~/claude-projects/*.md` by default.

No project files yet? It still runs. Chats get `❓` and their own topic until
projects exist to match against, and it never invents a project to fill the gap.

## Keep it running

The useful version is the one you never think about:

```
/schedule every 30 minutes: run the chat-namer skill, sweep any session whose
title, percentage or date is out of date, report nothing unless something changed
```

Now percentages update themselves as you tick things off, dates stay current, and
new chats get named without you asking.

## The percentage

The number belongs to the **project**, not the chat. Six chats on one project all
show the same figure, because it's the project that's 58% done.

| | | |
|---|---|---|
| ⚫ | 0% | Nobody has started |
| 🔴 | 1–24% | Barely begun |
| 🟠 | 25–49% | Early |
| 🟡 | 50–74% | Past halfway |
| 🟢 | 75–99% | Nearly there |
| ✅ | 100% | Done, safe to archive |

Black is deliberately not red. A project nobody has opened is a different problem
from one that started and stalled.

The side effect is the useful bit: a sidebar full of ⚫ and 🔴 tells you something
about how you're working that a list of chat titles never could.

## Two things it can't do

**It can't rename the chat you're sitting in.** The API blocks a session from
renaming itself. So it's always a sweeper. It renames every *other* chat, and the
current one gets named by the next pass. This is why the scheduled version is
worth setting up.

**It can't touch the desktop app's sidebar groups.** Those live in the app's own
local storage and no API reaches them, so making and filling groups stays a manual
job. What you get instead is the project tag in every title, plus a grouped view
written to `~/.chat-namer/groups.html` on every sweep: every chat nested under its
project, least finished first.

## Making it yours

Everything you'd want to change is in two files:

- `chat-namer/references/convention.md`: the title format, the fifteen lane
  emoji, and the percentage bands. Edit this to change how chats get named.
- `chat-namer/scripts/build-index.py`: the keywords that sort a project into a
  lane. Add your own vocabulary at the top. If a project file gets a bad tag
  (`gold-coast-workshop` becomes `GOLD` rather than `WORKSHOP`), pin it in the
  `OVERRIDE` map on the same page.

## What it touches

Reads your project markdown files. Writes two files under `~/.chat-namer/`. Calls
the Claude Code session tools to read chat transcripts and set chat titles.

It does not delete anything, does not archive anything, and will not overwrite a
title you typed yourself. Every rename is appended to `~/.chat-namer/renames.log`
with the old title, so any sweep can be rolled back.

One limit worth knowing: a sweep covers your 30 most recent chats. Older ones stay
as they are.

---

Made by Selr AI. MIT licensed, so use it, change it, ship it.
