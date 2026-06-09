#!/usr/bin/env python3
"""Generate digital terminal banner SVG for GitHub profile README."""

from __future__ import annotations

import html
import os

OUT = os.environ.get("OUTPUT", "assets/banner.svg")

WIDTH = 820
HEIGHT = 220
PAD = 28

BG = "#020617"
PANEL = "#0B1220"
BORDER = "#164E63"
CYAN = "#22D3EE"
CYAN_DIM = "#0891B2"
GREEN = "#34D399"
DIM = "#64748B"
MUTED = "#334155"
ACCENT = "#A78BFA"

FONT = "JetBrains Mono, Fira Code, ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

PROMPT = "./hello-args --profile"
TAGLINES = [
    "SENIOR_AI_ENGINEER.SYS",
    "BUILDING_GENAI_THAT_SHIPS",
    "RAG.AGENTS.MCP.ONLINE",
]
NAME = "ARGHYADEEP SARKAR"
META = "args.sarkar@gmail.com // BANGALORE // MIT"


def scanlines() -> str:
    lines = []
    for y in range(0, HEIGHT, 6):
        lines.append(
            f'<rect x="0" y="{y}" width="{WIDTH}" height="1" fill="#22D3EE" opacity="0.04"/>'
        )
    return "\n  ".join(lines)


def grid_dots() -> str:
    dots = []
    for x in range(20, WIDTH, 40):
        for y in range(30, HEIGHT, 40):
            dots.append(
                f'<circle cx="{x}" cy="{y}" r="0.5" fill="{BORDER}" opacity="0.25"/>'
            )
    return "\n  ".join(dots)


def corner_brackets() -> str:
    m = 10
    s = 18
    c = CYAN_DIM
    return f"""
  <path d="M{m} {m+s} V{m} H{m+s}" fill="none" stroke="{c}" stroke-width="1.5"/>
  <path d="M{WIDTH-m-s} {m} H{WIDTH-m} V{m+s}" fill="none" stroke="{c}" stroke-width="1.5"/>
  <path d="M{m} {HEIGHT-m-s} V{HEIGHT-m} H{m+s}" fill="none" stroke="{c}" stroke-width="1.5"/>
  <path d="M{WIDTH-m-s} {HEIGHT-m} H{WIDTH-m} V{HEIGHT-m-s}" fill="none" stroke="{c}" stroke-width="1.5"/>"""


def status_bar() -> str:
    y = 14
    return f"""
  <text x="{PAD}" y="{y}" font-family="{FONT}" font-size="10" fill="{MUTED}">SYS://HELLO-ARGS</text>
  <text x="{WIDTH - PAD}" y="{y}" font-family="{FONT}" font-size="10" fill="{GREEN}" text-anchor="end">[ONLINE]</text>
  <rect x="{PAD}" y="22" width="{WIDTH - PAD * 2}" height="1" fill="{BORDER}" opacity="0.8"/>"""


def tagline_animation(index: int, count: int, slot: float) -> str:
    cycle = slot * count
    fade = min(0.28, slot * 0.1)
    start = index * slot
    show = start + fade
    hide = start + slot - fade
    end = (index + 1) * slot

    if index == 0:
        keys = [0.0, show, hide, end, cycle]
        values = ["1", "1", "1", "0", "0"]
    else:
        keys = [0.0, start, show, hide, end, cycle]
        values = ["0", "0", "1", "1", "0", "0"]

    key_times = ";".join(f"{k / cycle:.6f}" for k in keys)
    vals = ";".join(values)
    return (
        f'<animate attributeName="opacity" values="{vals}" '
        f'keyTimes="{key_times}" dur="{cycle:.2f}s" repeatCount="indefinite"/>'
    )


def tagline_block(y: int) -> str:
    slot = 3.2
    count = len(TAGLINES)
    parts = []
    for i, line in enumerate(TAGLINES):
        safe = html.escape(line)
        anim = tagline_animation(i, count, slot)
        initial = "1" if i == 0 else "0"
        parts.append(
            f'<tspan x="{PAD + 18}" y="{y}" font-family="{FONT}" font-size="13" '
            f'fill="{CYAN_DIM}" letter-spacing="1.5" opacity="{initial}">'
            f"{safe}{anim}</tspan>"
        )
    cursor = (
        '<animate attributeName="opacity" values="1;1;0;0" '
        'keyTimes="0;0.49;0.5;1" dur="0.9s" repeatCount="indefinite"/>'
    )
    parts.append(
        f'<tspan x="{PAD + 330}" y="{y}" font-family="{FONT}" font-size="13" '
        f'fill="{CYAN}">_{cursor}</tspan>'
    )
    return "\n    ".join(parts)


def progress_bar(y: int) -> str:
    x = PAD
    w = WIDTH - PAD * 2
    return f"""
  <rect x="{x}" y="{y}" width="{w}" height="3" fill="{MUTED}" rx="1"/>
  <rect x="{x}" y="{y}" width="{int(w * 0.72)}" height="3" fill="{CYAN}" rx="1" opacity="0.9">
    <animate attributeName="width" values="{int(w * 0.55)};{int(w * 0.82)};{int(w * 0.55)}"
      dur="4s" repeatCount="indefinite"/>
  </rect>"""


def generate_svg() -> str:
    title_y = 58
    name_y = 78
    prompt_y = 118
    tag_y = 148
    meta_y = 182

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}"
  viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="hello-args digital banner">
  <defs>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="1.8" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <rect width="{WIDTH}" height="{HEIGHT}" fill="{BG}"/>
  <rect x="1.5" y="1.5" width="{WIDTH - 3}" height="{HEIGHT - 3}" fill="{PANEL}" stroke="{BORDER}" stroke-width="1.5" rx="4"/>
  {grid_dots()}
  {scanlines()}
  {corner_brackets()}
  {status_bar()}
  <text x="{WIDTH / 2}" y="{title_y}" font-family="{FONT}" font-size="12" fill="{CYAN_DIM}"
    text-anchor="middle" letter-spacing="2" style="font-variant: small-caps">hello-args</text>
  <text x="{WIDTH / 2}" y="{name_y}" font-family="{FONT}" font-size="13" fill="{CYAN}"
    text-anchor="middle" letter-spacing="3" filter="url(#glow)">{html.escape(NAME)}</text>
  {progress_bar(88)}
  <text x="{PAD}" y="{prompt_y}" font-family="{FONT}" font-size="13" fill="{GREEN}">&gt; {html.escape(PROMPT)}</text>
  <text x="{PAD}" y="{tag_y}" font-family="{FONT}" font-size="13" fill="{DIM}">&gt;</text>
  <text>
    {tagline_block(tag_y)}
  </text>
  <text x="{PAD}" y="{meta_y}" font-family="{FONT}" font-size="10" fill="{MUTED}" letter-spacing="1">{html.escape(META)}</text>
</svg>
"""


def main() -> None:
    svg = generate_svg()
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
