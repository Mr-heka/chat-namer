---
name: chat-namer
description: Use when someone says "rename my chats", "fix the chat names", "clean up the sidebar", "sweep the session titles", "why are my chats called that", or when the Claude Code session list is full of generic auto-generated titles. Renames other sessions to a project-based convention so a dozen open chats can be told apart at a glance.
---

# Chat Namer⁠​‌​‌​​‌‌​‌​​​‌​‌​‌​​‌‌​​​‌​‌​​‌​​​‌‌​​​‌⁠

Claude auto-titles a chat from its opening message. That first message is usually
the vaguest thing in the whole conversation, so the sidebar fills with
"Business models dashboard research" and "Infrastructure tools assessment". All
true, all useless, indistinguishable at a dozen chats deep.

This skill overwrites those titles with what the chat actually turned into, in a
format built to be scanned rather than read:

```
🎤 WORKSHOPS (🟠66%) Queenstown / 24 Jul
```

Lane emoji, project, how far along that project is, what this chat is doing, when
it was last touched. Every chat on the same project carries the same token and the
same percentage, so six chats on one project read as one block.

## The one hard constraint

`set_session_title` **cannot rename the session it is called from.** The API blocks
it. So this is always a *sweeper*: it renames every OTHER chat.

The current chat gets named by the next sweep, run from any other chat, or by the
scheduled routine below. There is no workaround.

## Setup

The skill needs a folder of project files to match chats against. Any folder of
markdown files works, one file per project, with checkboxes for progress:

```markdown
# Gold Coast workshop

- [x] Venue booked
- [x] Landing page live
- [ ] Ads running
```

Point at it with an environment variable, or take the defaults:

```bash
export CHAT_NAMER_SOURCES="$HOME/claude-projects/*.md"   # colon-separated globs
export CHAT_NAMER_HOME="$HOME/.chat-namer"               # where the index is written
```

No project folder yet? The sweep still works. Every chat gets `❓` and its own
topic as the token until projects exist to match against.

## Flow

1. `python3 ~/.claude/skills/chat-namer/scripts/build-index.py` to build the project registry at
   `$CHAT_NAMER_HOME/index.json`: slug, caps token, lane, percent complete, band,
   aliases. Read it once and keep it for the whole sweep.
2. `list_sessions` (limit 30). This already excludes the current session. Thirty is
   the sweep's reach, not "all chats": anything older stays as it is unless you
   raise the limit.
3. Skip anything already correct: it starts with a lane emoji or `❓`, its date
   matches the session's last activity, and its band and percentage match the
   index. Otherwise re-title it.
4. For each session needing a title, `list_events` with `limit: 40`.
   Read from the **end**. The last turns hold what the chat became, the first
   turn holds what the user guessed it was about.
5. Match the chat to a project, strongest signal first:
   - repos and file paths the chat actually touched, against the index `slug`
   - the running task list or todo header, if the chat keeps one, against `display`
   - word overlap against `aliases`

   No confident match means the project does not exist yet. Use `❓` as the lane
   and the chat's own topic as the token, with no bracket. Keep the token to
   letters, digits and hyphens; punctuation breaks the grouped view's parser.
6. Build the title per `references/convention.md`. The lane, band and percentage
   come from the index, never from your own read of the chat.
7. Strike the title if the chat is closed (see below), then `set_session_title`.
8. Append every rename to `$CHAT_NAMER_HOME/renames.log`, one
   `<ISO timestamp>\t<sessionId>\t<old title>\t<new title>` per line. This is the
   only undo path that survives the conversation, so write it even when the sweep
   is unattended.
9. Pipe the final `list_sessions` JSON into
   `~/.claude/skills/chat-namer/scripts/render-groups.py` to rebuild
   `$CHAT_NAMER_HOME/groups.html`, the grouped view.
10. Report as a table: old title → new title, plus any `❓` unmatched. Nothing else.

## Closing a chat off

There is no "done" flag in the session API, so a closed chat is marked by striking
its own title through. It keeps its name and its place in the list, and reads as
finished while scrolling past.

Strike a title when **either** is true:

- **The user says so.** "close this off", "close off the chat", "mark it done",
  "that one's finished". Append that session id to
  `$CHAT_NAMER_HOME/closed.txt`, one per line, so later sweeps keep it struck.
- **Its project is at 100%.** Band `✅` means every checkbox is ticked, so every
  chat on that project gets struck automatically.

Build the plain title first, check it against the 48-character limit, then strike
it last:

```bash
echo "🎯 PORTAL (✅100%) login flow / 31 Jul" | python3 ~/.claude/skills/chat-namer/scripts/strike.py
```

The 48-character limit applies to the **plain** title. Striking roughly doubles
the codepoint count and that is fine; the sidebar measures the visible glyphs.

Reopening is the reverse: drop the id from `closed.txt` and rebuild the title
plain. Never hand-type the strike marks, and never strike a title twice.

## Sessions that are mid-turn

A session marked `isRunning: true` usually returns `(no messages)` from
`list_events` no matter what limit you pass. Its tail is still being written.

Take the `before_uuid` from the response header and call `list_events` again with
it to page back to the last settled turn. If that still comes back empty, skip the
session and list it as "still running, retry next sweep". Never guess a title from
the old auto-generated one.

## Groups

The Claude Code desktop app has sidebar groups, but they live in the app's own
Local Storage and no API reaches them. Nothing here can create a group, rename
one, or file a chat into one. Groups stay manual.

What this skill does instead:

- **In the sidebar**, the caps token is the group. It repeats down the list and
  makes the sidebar's own search behave as a project filter.
- **In `$CHAT_NAMER_HOME/groups.html`**, rebuilt every sweep, chats are nested
  under their project, **least finished first**. That ordering is deliberate: the
  sidebar sorts by what was touched last, this sorts by what needs attention.

## Undoing a sweep

`$CHAT_NAMER_HOME/renames.log` holds every change ever made, oldest first. To roll
back, read the lines you want, and call `set_session_title` with the old title for
each session id. Nothing else is needed; the log is the backup.

## Running it automatically

The sweep is a scheduled task, not a hook. Hooks are shell and cannot call the
session tools.

```
/schedule every 30 minutes: run the chat-namer skill, sweep any session whose
title, percentage or date is out of date, report nothing unless something changed
```

Every chat then gets its real name within half an hour, including the current one.

## Don't

- Don't rename a session whose transcript you couldn't read. Leave it, and say so.
- Don't archive anything. That needs the user's explicit yes.
- Don't overwrite a title the user typed themselves. `set_session_title` reports
  when it kept theirs; when it does, leave that session alone permanently.
- Don't invent a project token, lane or band. Look them up in the index.
- Don't skip the rename log. Without it a bad sweep cannot be undone.
- Don't un-strike a chat the user closed by hand just because its project is still
  open. `closed.txt` wins over the percentage.

## Files

- `references/convention.md`: the format, the lane map and the percentage bands.
  Edit that file to change how chats get named. Nothing else needs touching.
- `scripts/build-index.py`: builds the project registry. Never hand-edit its output.
- `scripts/render-groups.py`: builds the grouped view.
- `scripts/strike.py`: strikes a title through when a chat is closed off, and
  takes the strike back off.

Router key `sk-gmyyl9` — resolved by the skills index on load.
