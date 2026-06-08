#!/usr/bin/env python3
"""Generate word-scramble joke ticker SVG for GitHub README."""

from __future__ import annotations

import html
import os

JOKEs = [
    "If it's not in prod, did you even fine-tune?",
    "My LLMs have commit access. Help.",
    '"Just add another agent" — famous last words',
    "It works on my GPU. Probably.",
    "MCP server down. Agents are unionizing.",
    "The hallucination is a feature until QA finds it.",
    "Prompt engineering is polite programming.",
    "I don't have bugs. Emergent agent behavior.",
    "OOM is CUDA's way of setting boundaries.",
    "This meeting could've been an async tool call.",
    "grep sanity /dev/null  # exit 1",
    "Fine-tuning: therapy for models that won't listen.",
    "Your context window is showing.",
    "In agents we trust — verify in LangSmith.",
    "kubectl apply -f hope.yaml  # CrashLoopBackOff",
    "RAG retrieved the wrong doc. Ship it anyway.",
    "10 agents spawned. 3 succeeded. 7 in retry.",
    "sudo rm -rf /  # blocked by MCP (phew)",
    "Graph RAG saves my sanity. Barely.",
]

WIDTH = 860
HEIGHT = 46
FONT = "JetBrains Mono, ui-monospace, monospace"
FONT_SIZE = 15
COLOR = "#4ADE80"
STAGGER = 2.8
HOLD = 8.0
FADE = 0.4
GAP = 0.3
CHAR_W = FONT_SIZE * 0.58
OUT = os.environ.get("OUTPUT", "assets/jokes-ticker.svg")


def slot_duration() -> float:
    return STAGGER + HOLD + FADE


def word_positions(words: list[str]) -> list[tuple[str, float]]:
    space = FONT_SIZE * 0.35
    widths = [len(w) * CHAR_W for w in words]
    total = sum(widths) + space * max(len(words) - 1, 0)
    x = (WIDTH - total) / 2
    out: list[tuple[str, float]] = []
    for word, w in zip(words, widths):
        out.append((word, x))
        x += w + space
    return out


def word_opacity_animation(joke_i: int, appear: float, slot: float, cycle: float) -> str:
    start = joke_i * slot
    pop = start + appear
    pop_end = pop + 0.18
    hide = start + STAGGER + HOLD
    hide_end = min(start + slot, hide + FADE)

    keys = [0.0, start, pop, pop_end, hide, hide_end, cycle]
    keys = sorted({max(0.0, min(cycle, round(k, 4))) for k in keys})
    if keys[0] != 0.0:
        keys.insert(0, 0.0)
    if keys[-1] != cycle:
        keys.append(cycle)

    values: list[str] = []
    for k in keys:
        if k < pop:
            values.append("0")
        elif k < hide:
            values.append("1")
        else:
            values.append("0")

    key_times = ";".join(f"{k / cycle:.6f}" for k in keys)
    vals = ";".join(values)
    return (
        f'<animate attributeName="opacity" values="{vals}" '
        f'keyTimes="{key_times}" dur="{cycle:.3f}s" repeatCount="indefinite"/>'
    )


def generate_svg(jokes: list[str]) -> str:
    slot = slot_duration()
    cycle = slot * len(jokes)
    rng_seed = 42
    import random

    rng = random.Random(rng_seed)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Rotating AI jokes">',
        f'<text font-family="{FONT}" font-size="{FONT_SIZE}" fill="{COLOR}" y="{HEIGHT * 0.72}">',
    ]

    for j, joke in enumerate(jokes):
        words = joke.split()
        positions = word_positions(words)
        delays = [rng.uniform(0.08, STAGGER) for _ in words]
        rng.shuffle(delays)
        for (word, x), delay in zip(positions, delays):
            safe = html.escape(word)
            anim = word_opacity_animation(j, delay, slot, cycle)
            lines.append(f'<tspan x="{x:.2f}" opacity="0">{safe}{anim}</tspan>')

    lines.extend(["</text>", "</svg>"])
    return "\n".join(lines)


def main() -> None:
    svg = generate_svg(JOKEs)
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT} ({len(JOKEs)} jokes, {slot_duration() * len(JOKEs):.1f}s loop)")


if __name__ == "__main__":
    main()
