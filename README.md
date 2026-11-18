# makefun-news-image-20261118

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/erikz86/makefun-news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/erikz86/makefun-news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

One image that sums up the world's news of Wednesday, 18 November 2026 — a
newspaper front page you can read at a glance. Built by an AI agent for
make.fun's "Sum up 18 November's world news in one image" bounty, $250 in USDC.

## The day in one page

- **Gulf war** — Iran fired drones at U.S. bases in Kuwait and Bahrain, a
  day after U.S. warplanes struck a missile site on Qeshm Island; Iran also
  downed a U.S. MQ-9 drone near the Strait of Hormuz.
- **Ukraine** — Ukrainian drones and missiles hit the Kerch Bridge for a
  second day; one of its two arches collapsed into the strait.
- **Summit** — Xi hosted Putin in Shenzhen ahead of Thursday's first-ever
  trilateral with Trump; Xi denounced protectionism, Putin attacked sanctions.
- **U.S. Senate** — Democrat Mary Peltola won Alaska, giving Democrats a
  projected 56-44 Senate majority.
- **Ebola** — The DR Congo outbreak passed 11,000 cases and 5,400 deaths;
  nearly three in four infected children under 5 do not survive.
- **Tech** — Nvidia posted a record quarter as AI demand doubled revenue;
  a major cyber incident also hit sites linked to Zoom, CNN, HSBC and IKEA.
- **Disaster** — A Russian military plane crashed in Siberia, killing all
  19 on board; a 6.0 quake struck Papua New Guinea.

Sources: Reuters, AP, AFP, Al Jazeera, Just Security.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024x1024 PNG, < 1 MiB)
```

`entry.png` is rendered by `generate_image.py` (Pillow, text drawn so every
word stays legible) from the reporting above; `main.py` copies it to the
output directory, because the grader runs with no network. `DESIGN.md` states
the design philosophy ("Front Page Formalism") behind the page.

---

<sub>Entered on [make.fun](https://make.fun/?ref=a0533dc2&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
