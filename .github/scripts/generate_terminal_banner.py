#!/usr/bin/env python3
"""Generate terminal-style startup banner SVG for GitHub profile README."""

from __future__ import annotations

import html
import os

WIDTH = 720
HEIGHT = 248
OUT = os.environ.get("OUTPUT", "assets/terminal-banner.svg")

FONT = "JetBrains Mono, Fira Code, ui-monospace, monospace"
BG = "#0D1117"
BORDER = "#334155"
CYAN = "#22D3EE"
GREEN = "#4ADE80"
DIM = "#64748B"
MUTED = "#475569"

LOGO = [
    "  _   ___   _  ____  _____ ",
    " /_\\ / _ \\ / |/ ___|| ____|",
    "/ _ \\| | | | | |  _ |  _|  ",
    "/_/ \\_|_| |_| |_| (_)|_|    ",
]

PROMPT = "$ ./hello-args --profile"
TAGLINES = [
    "senior_ai_engineer.sys · online",
    "building genai that ships...",
    "rag · agents · mcp",
]
META = "args.sarkar@gmail.com · Bangalore · MIT"


def logo_block() -> str:
    lines: list[str] = []
    y = 36
    lh = 18
    for row in LOGO:
        safe = html.escape(row)
        lines.append(
            f'<tspan x="48" y="{y}" fill="{CYAN}" font-weight="700" '
            f'font-size="15">{safe}</tspan>'
        )
        y += lh
    return "\n      ".join(lines)


def tagline_animation(index: int, count: int, slot: float) -> str:
    cycle = slot * count
    fade = min(0.3, slot * 0.12)
    start = index * slot
    show = start + fade
    hide = start + slot - fade
    end = (index + 1) * slot

    keys = [0.0, start, show, hide, end, cycle]
    values = ["0", "0", "1", "1", "0", "0"]
    if index == 0:
        keys[0] = 0.0
        values[0] = "0"
        # visible from boot through first slot
        keys = [0.0, show, hide, end, cycle]
        values = ["1", "1", "1", "0", "0"]

    key_times = ";".join(f"{k / cycle:.6f}" for k in keys)
    vals = ";".join(values)
    return (
        f'<animate attributeName="opacity" values="{vals}" '
        f'keyTimes="{key_times}" dur="{cycle:.2f}s" repeatCount="indefinite"/>'
    )


def tagline_tspans() -> str:
    y = 142
    slot = 3.6
    count = len(TAGLINES)
    parts: list[str] = []
    for i, line in enumerate(TAGLINES):
        safe = html.escape(line)
        anim = tagline_animation(i, count, slot)
        initial = "1" if i == 0 else "0"
        parts.append(
            f'<tspan x="48" y="{y}" fill="{DIM}" font-size="13" '
            f'opacity="{initial}">{safe}{anim}</tspan>'
        )
    return "\n      ".join(parts)


def generate_svg() -> str:
    cursor_blink = (
        '<animate attributeName="opacity" values="1;1;0;0" '
        'keyTimes="0;0.49;0.5;1" dur="1s" repeatCount="indefinite"/>'
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}"
  viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="hello-args terminal banner">
  <rect width="{WIDTH}" height="{HEIGHT}" rx="8" fill="{BG}"/>
  <rect x="1" y="1" width="{WIDTH - 2}" height="{HEIGHT - 2}" rx="7"
    fill="none" stroke="{BORDER}" stroke-width="1.5"/>
  <text font-family="{FONT}" xml:space="preserve">
    <tspan x="48" y="22" fill="{MUTED}" font-size="11">hello-args v2.0</tspan>
    <tspan x="{WIDTH - 48}" y="22" fill="{MUTED}" font-size="11" text-anchor="end">[ready]</tspan>
    {logo_block()}
    <tspan x="48" y="118" fill="{GREEN}" font-size="13">{html.escape(PROMPT)}</tspan>
    {tagline_tspans()}
    <tspan x="420" y="142" fill="{CYAN}" font-size="13" opacity="1">▌{cursor_blink}</tspan>
    <tspan x="48" y="210" fill="{MUTED}" font-size="11">{html.escape(META)}</tspan>
  </text>
</svg>
"""


def main() -> None:
    svg = generate_svg()
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
