# Setup prompt

Paste the whole block below into Claude Code. It installs the skill, points it at
your projects, sets up the schedule that keeps it running, and does the first
sweep. Nothing else is needed.

```
https://github.com/Mr-heka/chat-namer

Install the chat-namer skill from the repo above and set it up so it keeps
running on its own.

1. Clone it somewhere temporary and copy the inner skill folder into my skills
   directory:
   git clone https://github.com/Mr-heka/chat-namer.git /tmp/chat-namer-install
   mkdir -p ~/.claude/skills
   cp -r /tmp/chat-namer-install/chat-namer ~/.claude/skills/
   rm -rf /tmp/chat-namer-install
   If ~/.claude/skills is not where Claude Code keeps skills on this machine,
   find the right directory and use that instead. If a chat-namer folder is
   already there, rename it to chat-namer.backup first.

2. Work out where my projects live. Look for a folder of markdown files where
   each file is one project with checkboxes for progress, and check the usual
   spots: ~/claude-projects, ~/projects, ~/board, an Obsidian vault, or a docs
   folder in whatever repo I am working in. Tell me which one you picked and why
   in one line. If you find nothing that fits, create ~/claude-projects with a
   README explaining the one-file-per-project format, and carry on. Then add the
   path to my shell profile:
   echo 'export CHAT_NAMER_SOURCES="<the folder you picked>/*.md"' >> ~/.zshrc
   Use ~/.bashrc instead if my shell is bash.

3. Set up the schedule so I never have to ask for a sweep. Create a scheduled
   task called chat-namer-sweep that runs hourly and whose instructions are:
   "Run the chat-namer skill at ~/.claude/skills/chat-namer/SKILL.md. Re-title
   any session whose title, percentage or date is out of date. Cap each run at
   the 12 most recently active sessions that need work and read their
   transcripts with parallel sub-agents so the run finishes quickly. Output
   nothing unless a title changed."
   Use whatever scheduling this build of Claude Code has: the scheduled-task
   tool if you have one, otherwise /schedule, otherwise a cron entry that opens
   Claude Code with that prompt. Tell me in one line which one you used. If none
   of them exist here, say so plainly and tell me to run "rename my chats" by
   hand instead.

4. Run the first sweep now, then show me the old title next to the new title for
   every chat you renamed, and nothing else.

Do all of this without asking me any questions.
```
