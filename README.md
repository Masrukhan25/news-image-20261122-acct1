# The World in One Day — 22 November 2026

[![make.fun](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/Masrukhan25/news-image-20261122-acct1/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/Masrukhan25/news-image-20261122-acct1/reward.svg)](https://make.fun/bounty/news-image-20261122)

A broadsheet newspaper front page for Sunday 22 November 2026: 35 verified
stories on one day — 3 big heroes (COP31 collapses in Antalya, Russian
strikes kill 15 in Ukraine, Libyan corvette capsized), a 10-story grid, a
world map with numbered dots, a 22-dispatch list, a "THE DAY IN UTC" strip,
a "THE DAY IN NUMBERS" strip, and a DATE CHECK bar.

- **Middle East & Iran War** — 10 stories
- **Europe & Ukraine War** — 3 stories
- **COP31 (global)** — 1 story
- **Africa** — 4 stories
- **Asia** — 2 stories
- **Americas** — 9 stories
- **Sport & Oddities** — 6 stories

The image (`entry.png`, 1024×1024) is drawn entirely with flat-vector shapes
and text — no AI-generated imagery, so every label is crisp and readable. A key
numbers row, source footer, and a date-check box (what was left out because
it happened on another day) complete the page.

## How it runs

`main.py` (standard library only) copies `entry.png` byte-identical to
`MAKEFUN_OUTPUT_DIR` (default `/output`) as `entry.png`:

```sh
MAKEFUN_OUTPUT_DIR=/output python3 main.py
```
