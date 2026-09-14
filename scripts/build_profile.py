#!/usr/bin/env python3
"""Generate the light and dark profile cards.

The card is an animated terminal window: window chrome, a neofetch-style
read-out whose rows slide in one after another, a typewriter sweep on the
closing echo line, and a blinking block cursor.

Animation is plain CSS and SMIL inside the SVG, which browsers run even when
the file is served through an <img> tag, as GitHub does. Every animated rule
degrades to the finished state, so the card stays readable if animation never
runs at all.

Edit profile.json, then run: python scripts/build_profile.py
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "profile.json"

THEMES = {
    "dark_mode.svg": {
        "card": "#161B22",
        "chrome_bg": "#0D1117",
        "border": "#30363D",
        "text": "#C9D1D9",
        "muted": "#7D8590",
        "key": "#58A6FF",
        "value": "#A5D6FF",
        "accent": "#3FB950",
    },
    "light_mode.svg": {
        "card": "#FFFFFF",
        "chrome_bg": "#F6F8FA",
        "border": "#D0D7DE",
        "text": "#24292F",
        "muted": "#57606A",
        "key": "#0969DA",
        "value": "#0550AE",
        "accent": "#1A7F37",
    },
}

WIDTH = 880
CHROME_H = 38
RADIUS = 12
PAD_X = 26
FONT_SIZE = 15
LINE_HEIGHT = 23
SECTION_GAP = 8
FIRST_BASELINE = CHROME_H + 32
BOTTOM_PAD = 26
RULE_COLUMN = 86

ROW_STAGGER = 0.07
TYPE_DURATION = 1.25

STACK_ROWS = (
    ("Languages", "languages"),
    ("AI.LLM", "ai_llm"),
    ("ML.CV", "ml_cv"),
    ("Backend", "backend"),
    ("Data", "data"),
    ("Cloud.MLOps", "cloud"),
)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def rule_after(prefix_len: int) -> str:
    return "-" * max(8, RULE_COLUMN - prefix_len)


class Card:
    """Collects body rows, tracking the baseline and each row's reveal delay."""

    def __init__(self) -> None:
        self.rows: list[str] = []
        self.y = FIRST_BASELINE

    def row(self, spans: str, *, extra_class: str = "") -> None:
        delay = len(self.rows) * ROW_STAGGER
        cls = f"row {extra_class}".strip()
        self.rows.append(
            f'<text class="{cls}" x="{PAD_X}" y="{self.y:g}"'
            f' style="animation-delay:{delay:.2f}s">{spans}</text>'
        )

    def advance(self, *, section: bool = False) -> None:
        self.y += LINE_HEIGHT + (SECTION_GAP if section else 0)

    def field(self, key: str, value: str) -> None:
        self.row(
            '<tspan class="muted">. </tspan>'
            f'<tspan class="key">{esc(key)}</tspan>'
            '<tspan class="muted">: </tspan>'
            f'<tspan class="value">{esc(value)}</tspan>'
        )

    def section(self, title: str) -> None:
        prefix = f"- {title} "
        self.row(
            f'<tspan class="text">{esc(prefix)}</tspan>'
            f'<tspan class="muted">{rule_after(len(prefix))}</tspan>'
        )


def build_rows(profile: dict[str, object]) -> tuple[Card, float]:
    card = Card()

    heading = f'{str(profile["username"]).lower()}@github'
    card.row(
        f'<tspan class="accent">{esc(heading)}</tspan>'
        f'<tspan class="muted"> {rule_after(len(heading) + 1)}</tspan>'
    )

    for key, field in (("Name", "display_name"), ("Role", "role"),
                       ("Focus", "focus"), ("Education", "education")):
        card.advance()
        card.field(key, str(profile[field]))

    card.advance(section=True)
    card.section("Technical Stack")
    for key, field in STACK_ROWS:
        card.advance()
        card.field(key, str(profile[field]))

    card.advance(section=True)
    card.section("Contact")
    for key, value in (("Email", profile["email"]),
                       ("LinkedIn", f'/in/{profile["linkedin"]}')):
        card.advance()
        card.field(key, str(value))

    # The echo line is uncovered by the typewriter clip instead of sliding in.
    card.advance(section=True)
    echo_y = card.y
    card.row(
        '<tspan class="accent">$ echo </tspan>'
        f'<tspan class="text">&quot;{esc(profile["tagline"])}&quot;</tspan>',
        extra_class="typed",
    )

    card.advance()
    card.row(
        '<tspan class="accent">$ </tspan>'
        '<tspan class="cursor">█</tspan>',
        extra_class="prompt",
    )
    return card, echo_y


def render_svg(profile: dict[str, object], theme: dict[str, str]) -> str:
    card, echo_y = build_rows(profile)
    height = round(card.y + BOTTOM_PAD)

    # The sweep starts once the last slide-in has landed, and the prompt row
    # waits for the sweep to finish.
    type_start = len(card.rows) * ROW_STAGGER + 0.35
    total = type_start + TYPE_DURATION
    hold = type_start / total

    clip_w = WIDTH - PAD_X * 2
    chrome_span = WIDTH - 1 - RADIUS * 2

    return "\n".join([
        "<?xml version='1.0' encoding='UTF-8'?>",
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}"'
        f' viewBox="0 0 {WIDTH} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{esc(profile["display_name"])} GitHub profile</title>',
        '<desc id="desc">An animated terminal card listing role, focus, education,'
        ' technical stack and contact details.</desc>',
        "<defs>",
        '<clipPath id="typewriter">',
        f'<rect x="{PAD_X}" y="{echo_y - FONT_SIZE:g}" height="{LINE_HEIGHT}"'
        f' width="{clip_w}">',
        f'<animate attributeName="width" values="0;0;{clip_w}"'
        f' keyTimes="0;{hold:.3f};1" dur="{total:.2f}s" fill="freeze"'
        ' calcMode="spline" keySplines="0 0 1 1;.2 .6 .3 1"/>',
        "</rect>",
        "</clipPath>",
        "</defs>",
        "<style>",
        "text, tspan { white-space: pre; font-family: ui-monospace, SFMono-Regular,"
        " Menlo, Monaco, Consolas, 'Liberation Mono', monospace; }",
        f"text {{ font-size: {FONT_SIZE}px; }}",
        f".text {{ fill: {theme['text']}; }}",
        f".muted {{ fill: {theme['muted']}; }}",
        f".key {{ fill: {theme['key']}; font-weight: 700; }}",
        f".value {{ fill: {theme['value']}; }}",
        f".accent {{ fill: {theme['accent']}; font-weight: 700; }}",
        f".chrome {{ fill: {theme['muted']}; font-size: 13px; }}",
        # `backwards` leaves the finished state as the base style, so a renderer
        # that ignores animation still paints every row.
        ".row { animation: reveal .5s cubic-bezier(.22,.61,.36,1) backwards; }",
        "@keyframes reveal { from { opacity: 0; transform: translateX(-12px); }"
        " to { opacity: 1; transform: none; } }",
        ".typed { clip-path: url(#typewriter); animation: none; }",
        f".prompt {{ animation-delay: {total:.2f}s !important; }}",
        f".cursor {{ fill: {theme['accent']};"
        " animation: blink 1.06s step-end infinite; }",
        "@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }",
        "@media (prefers-reduced-motion: reduce) { .row, .cursor { animation: none; }"
        " .typed { clip-path: none; } }",
        "</style>",
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}"'
        f' rx="{RADIUS}" fill="{theme["card"]}" stroke="{theme["border"]}"/>',
        f'<path d="M0.5 {RADIUS + 0.5}a{RADIUS} {RADIUS} 0 0 1 {RADIUS}-{RADIUS}'
        f'h{chrome_span}a{RADIUS} {RADIUS} 0 0 1 {RADIUS} {RADIUS}'
        f'v{CHROME_H - RADIUS}H0.5z" fill="{theme["chrome_bg"]}"/>',
        f'<line x1="0.5" y1="{CHROME_H}.5" x2="{WIDTH - 0.5:g}" y2="{CHROME_H}.5"'
        f' stroke="{theme["border"]}"/>',
        '<circle cx="24" cy="19.5" r="6" fill="#FF5F56"/>',
        '<circle cx="44" cy="19.5" r="6" fill="#FFBD2E"/>',
        '<circle cx="64" cy="19.5" r="6" fill="#27C93F"/>',
        f'<text class="chrome" x="{WIDTH / 2:g}" y="24" text-anchor="middle">'
        f'{esc(str(profile["username"]).lower())}@github: ~</text>',
        *card.rows,
        "</svg>",
    ]) + "\n"


def main() -> None:
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    for filename, theme in THEMES.items():
        (ROOT / filename).write_text(render_svg(profile, theme), encoding="utf-8")
        print(f"generated {filename}")


if __name__ == "__main__":
    main()
