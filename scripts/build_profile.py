#!/usr/bin/env python3
"""Generate the light and dark GitHub profile panels.

The panel is the right-hand column of the README card: a neofetch-style
terminal read-out that sits next to assets/msdos-boot.gif. Both halves are
sized to the same rendered height so the two cells line up exactly.

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
        "text": "#C9D1D9",
        "muted": "#7D8590",
        "key": "#58A6FF",
        "value": "#A5D6FF",
        "accent": "#3FB950",
        "rule": "#30363D",
    },
    "light_mode.svg": {
        "text": "#24292F",
        "muted": "#57606A",
        "key": "#0969DA",
        "value": "#0550AE",
        "accent": "#1A7F37",
        "rule": "#D0D7DE",
    },
}

# Kept in sync with the gif width in README.md: the panel height and the
# rendered gif height must match for the two table cells to align.
WIDTH = 640
PAD_X = 22
FONT_SIZE = 14
LINE_HEIGHT = 21
SECTION_GAP = 6
FIRST_BASELINE = 28
BOTTOM_PAD = 18
# Every divider rule is padded out to this column so their right edges line up.
RULE_COLUMN = 68

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


def rich_line(y: float, key: str, value: str) -> str:
    return (
        f'<tspan x="{PAD_X}" y="{y:g}" class="muted">. </tspan>'
        f'<tspan class="key">{esc(key)}</tspan>'
        f'<tspan class="muted">: </tspan>'
        f'<tspan class="value">{esc(value)}</tspan>'
    )


def rule_after(prefix_len: int) -> str:
    return "-" * max(8, RULE_COLUMN - prefix_len)


def section_line(y: float, title: str) -> str:
    prefix = f"- {title} "
    return (
        f'<tspan x="{PAD_X}" y="{y:g}" class="text">{esc(prefix)}</tspan>'
        f'<tspan class="muted">{rule_after(len(prefix))}</tspan>'
    )


def render_svg(profile: dict[str, object], theme: dict[str, str]) -> str:
    body: list[str] = []
    y = FIRST_BASELINE

    heading = f'{str(profile["username"]).lower()}@github'
    body.append(
        f'<tspan x="{PAD_X}" y="{y:g}" class="accent">{esc(heading)}</tspan>'
        f'<tspan class="muted"> {rule_after(len(heading) + 1)}</tspan>'
    )

    for key, field in (("Name", "display_name"), ("Role", "role"),
                       ("Focus", "focus"), ("Education", "education")):
        y += LINE_HEIGHT
        body.append(rich_line(y, key, str(profile[field])))

    y += LINE_HEIGHT + SECTION_GAP
    body.append(section_line(y, "Technical Stack"))
    for key, field in STACK_ROWS:
        y += LINE_HEIGHT
        body.append(rich_line(y, key, str(profile[field])))

    y += LINE_HEIGHT + SECTION_GAP
    body.append(section_line(y, "Contact"))
    for key, value in (("Email", profile["email"]),
                       ("LinkedIn", f'/in/{profile["linkedin"]}'),
                       ("GitHub", f'@{profile["username"]}')):
        y += LINE_HEIGHT
        body.append(rich_line(y, key, str(value)))

    y += LINE_HEIGHT + SECTION_GAP
    body.append(
        f'<tspan x="{PAD_X}" y="{y:g}" class="accent">$ echo </tspan>'
        f'<tspan class="text">&quot;{esc(profile["tagline"])}&quot;</tspan>'
    )

    height = round(y + BOTTOM_PAD)
    return "\n".join([
        "<?xml version='1.0' encoding='UTF-8'?>",
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}"'
        f' viewBox="0 0 {WIDTH} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{esc(profile["display_name"])} GitHub profile</title>',
        '<desc id="desc">A terminal-style read-out listing role, focus, education,'
        ' technical stack and contact details.</desc>',
        "<style>",
        "text, tspan { white-space: pre; font-family: ui-monospace, SFMono-Regular,"
        " Menlo, Monaco, Consolas, 'Liberation Mono', monospace; }",
        f".text {{ fill: {theme['text']}; }}",
        f".muted {{ fill: {theme['muted']}; }}",
        f".key {{ fill: {theme['key']}; font-weight: 700; }}",
        f".value {{ fill: {theme['value']}; }}",
        f".accent {{ fill: {theme['accent']}; font-weight: 700; }}",
        "</style>",
        f'<text x="{PAD_X}" y="{FIRST_BASELINE}" font-size="{FONT_SIZE}px" class="text">',
        *body,
        "</text>",
        "</svg>",
    ]) + "\n"


def main() -> None:
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    for filename, theme in THEMES.items():
        (ROOT / filename).write_text(render_svg(profile, theme), encoding="utf-8")
        print(f"generated {filename}")


if __name__ == "__main__":
    main()
