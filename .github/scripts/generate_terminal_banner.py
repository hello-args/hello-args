#!/usr/bin/env python3
"""Generate terminal-style startup banner SVG for GitHub profile README."""

from __future__ import annotations

import html
import os

OUT = os.environ.get("OUTPUT", "assets/terminal-banner.svg")

FONT = "JetBrains Mono, Fira Code, ui-monospace, monospace"
BG = "#0D1117"
BORDER = "#334155"
TITLE_BG = "#161B22"
CYAN = "#22D3EE"
GREEN = "#4ADE80"
DIM = "#64748B"
MUTED = "#475569"
RED = "#F87171"
YELLOW = "#FACC15"
GREEN_DOT = "#4ADE80"

# figlet standard "hello-args" (complete 6-line logo)
LOGO = [
    " _          _ _                                 ",
    "| |__   ___| | | ___         __ _ _ __ __ _ ___ ",
    "| '_ \\ / _ \\ | |/ _ \\ _____ / _` | '__/ _` / __|",
    "| | | |  __/ | | (_) |_____| (_| | | | (_| \\__ \\",
    "|_| |_|\\___|_|_|\\___/       \\__,_|_|  \\__, |___/",
    "                                      |___/     ",
]

LOGO_SIZE = 12
LOGO_LH = 14
PROMPT = "$ ./hello-args --profile"
TAGLINES = [
    "senior_ai_engineer.sys · online",
    "building genai that ships...",
    "rag · agents · mcp",
]
META = "args.sarkar@gmail.com · Bangalore · MIT"

TITLE_H = 34
PAD_X = 24
PAD_TOP = TITLE_H + 18
CHAR_W = LOGO_SIZE * 0.62


def logo_width() -> int:
    return max(len(line.rstrip("\n")) for line in LOGO)


def svg_width() -> int:
    return max(820, int(logo_width() * CHAR_W + PAD_X * 2 + 48))


def svg_height() -> int:
    logo_h = len(LOGO) * LOGO_LH
    return PAD_TOP + logo_h + 128


def logo_block(width: int) -> str:
    lines: list[str] = []
    y = PAD_TOP
    logo_w = logo_width() * CHAR_W
    x = (width - logo_w) / 2
    for row in LOGO:
        safe = html.escape(row.rstrip("\n").rstrip())
        lines.append(
            f'<tspan x="{x:.1f}" y="{y}" fill="{CYAN}" font-weight="700" '
            f'font-size="{LOGO_SIZE}">{safe}</tspan>'
        )
        y += LOGO_LH
    return "\n      ".join(lines)


def tagline_animation(index: int, count: int, slot: float) -> str:
    cycle = slot * count
    fade = min(0.3, slot * 0.12)
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


def tagline_tspans(y: int) -> str:
    slot = 3.6
    count = len(TAGLINES)
    parts: list[str] = []
    for i, line in enumerate(TAGLINES):
        safe = html.escape(line)
        anim = tagline_animation(i, count, slot)
        initial = "1" if i == 0 else "0"
        parts.append(
            f'<tspan x="{PAD_X}" y="{y}" fill="{DIM}" font-size="13" '
            f'opacity="{initial}">{safe}{anim}</tspan>'
        )
    return "\n      ".join(parts)


def cursor_x(tagline: str) -> float:
    return PAD_X + len(tagline) * 7.8 + 6


def generate_svg() -> str:
    width = svg_width()
    height = svg_height()
    logo_bottom = PAD_TOP + len(LOGO) * LOGO_LH
    prompt_y = logo_bottom + 22
    tagline_y = prompt_y + 24
    meta_y = tagline_y + 52
    cursor_blink = (
        '<animate attributeName="opacity" values="1;1;0;0" '
        'keyTimes="0;0.49;0.5;1" dur="1s" repeatCount="indefinite"/>'
    )
    longest_tag = max(TAGLINES, key=len)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
  viewBox="0 0 {width} {height}" role="img" aria-label="hello-args terminal banner"
  overflow="visible">
  <rect width="{width}" height="{height}" rx="8" fill="{BG}"/>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="7"
    fill="none" stroke="{BORDER}" stroke-width="1.5"/>
  <rect x="1" y="1" width="{width - 2}" height="{TITLE_H}" rx="7" fill="{TITLE_BG}"/>
  <line x1="1" y1="{TITLE_H}" x2="{width - 1}" y2="{TITLE_H}" stroke="{BORDER}" stroke-width="1"/>
  <circle cx="{PAD_X}" cy="17" r="5" fill="{RED}"/>
  <circle cx="{PAD_X + 18}" cy="17" r="5" fill="{YELLOW}"/>
  <circle cx="{PAD_X + 36}" cy="17" r="5" fill="{GREEN_DOT}"/>
  <text font-family="{FONT}" font-size="11" fill="{MUTED}" x="{PAD_X + 58}" y="21">hello-args — profile</text>
  <text font-family="{FONT}" font-size="11" fill="{MUTED}" x="{width - PAD_X}" y="21" text-anchor="end">[ready]</text>
  <text font-family="{FONT}" xml:space="preserve">
    {logo_block(width)}
    <tspan x="{PAD_X}" y="{prompt_y}" fill="{GREEN}" font-size="13">{html.escape(PROMPT)}</tspan>
    {tagline_tspans(tagline_y)}
    <tspan x="{cursor_x(longest_tag):.1f}" y="{tagline_y}" fill="{CYAN}" font-size="13" opacity="1">▌{cursor_blink}</tspan>
    <tspan x="{PAD_X}" y="{meta_y}" fill="{MUTED}" font-size="11">{html.escape(META)}</tspan>
  </text>
</svg>
"""


def main() -> None:
    svg = generate_svg()
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT} ({svg_width()}x{svg_height()})")


if __name__ == "__main__":
    main()
