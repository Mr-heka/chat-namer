#!/usr/bin/env python3
"""Strike a chat title through, or take the strike back off.

A closed chat keeps its name and its place in the list, but reads as done at a
glance while scrolling. There is no "closed" flag in the session API, so the
strike is carried by the title itself: U+0336 (combining long stroke overlay)
after each visible character.

  echo "🎯 PORTAL (✅100%) login flow / 31 Jul" | strike.py
  echo "🎯 P̶O̶R̶T̶A̶L̶ …" | strike.py --undo

Emoji and spaces are skipped. A stroke on top of an emoji renders as a smear on
most systems, and striking the spaces makes the line look like one solid bar.
"""
import sys
import unicodedata

MARK = "̶"


def strike(text):
    out = []
    for ch in text:
        if ch == MARK:                       # already struck, don't double up
            continue
        out.append(ch)
        if ch != " " and not unicodedata.combining(ch) and ord(ch) < 0x2600:
            out.append(MARK)
    return "".join(out)


def unstrike(text):
    return text.replace(MARK, "")


def main():
    text = sys.stdin.read().strip("\n")
    sys.stdout.write(unstrike(text) if "--undo" in sys.argv[1:] else strike(text))


if __name__ == "__main__":
    main()
