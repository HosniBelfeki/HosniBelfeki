#!/usr/bin/env python3
"""Generate the light and dark GitHub profile SVGs.

The layout is inspired by Andrew6rant's neofetch-style profile README,
with an original implementation and Hosni Belfeki's profile content.
"""
from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
ASCII_PATH = ROOT / "assets" / "ascii-art.txt"
PROFILE_PATH = ROOT / "profile.json"

THEMES = {
    "dark_mode.svg": {
        "background": "#0D1117",
        "border": "#30363D",
        "text": "#C9D1D9",
        "muted": "#7D8590",
        "key": "#58A6FF",
        "value": "#A5D6FF",
        "accent": "#3FB950",
        "project": "#D2A8FF",
    },
    "light_mode.svg": {
        "background": "#FFFFFF",
        "border": "#D0D7DE",
        "text": "#24292F",
        "muted": "#57606A",
        "key": "#0969DA",
        "value": "#0550AE",
        "accent": "#1A7F37",
        "project": "#8250DF",
    },
}

WIDTH = 1280
HEIGHT = 680
ASCII_X = 18
ASCII_Y = 27
ASCII_FONT_SIZE = 8
ASCII_LINE_HEIGHT = 10.5
PANEL_X = 555
PANEL_Y = 31
PANEL_FONT_SIZE = 14
PANEL_LINE_HEIGHT = 22


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def tspan(x: int, y: float, text: str, css_class: str | None = None, element_id: str | None = None) -> str:
    attrs = [f'x="{x}"', f'y="{y:g}"']
    if css_class:
        attrs.append(f'class="{css_class}"')
    if element_id:
        attrs.append(f'id="{element_id}"')
    return f'<tspan {" ".join(attrs)}>{esc(text)}</tspan>'


def rich_line(x: int, y: float, key: str, value: str, *, value_id: str | None = None) -> str:
    value_attrs = ' class="value"'
    if value_id:
        value_attrs += f' id="{value_id}"'
    return (
        f'<tspan x="{x}" y="{y:g}" class="muted">. </tspan>'
        f'<tspan class="key">{esc(key)}</tspan>'
        f'<tspan class="muted">: </tspan>'
        f'<tspan{value_attrs}>{esc(value)}</tspan>'
    )


def section_line(x: int, y: float, title: str) -> str:
    rule_count = max(8, 52 - len(title))
    return (
        f'<tspan x="{x}" y="{y:g}" class="text">- {esc(title)} </tspan>'
        f'<tspan class="muted">{"-" * rule_count}</tspan>'
    )


def render_svg(profile: dict[str, object], ascii_lines: Iterable[str], theme: dict[str, str]) -> str:
    lines = list(ascii_lines)
    svg: list[str] = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{esc(profile["display_name"])} GitHub profile</title>',
        '<desc id="desc">A terminal-style profile card with an ASCII portrait, technical skills, projects, contact information and GitHub statistics.</desc>',
        '<defs><clipPath id="asciiClip"><rect x="12" y="12" width="505" height="645" rx="10"/></clipPath></defs>',
        "<style>",
        "text, tspan { white-space: pre; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace; }",
        f".text {{ fill: {theme['text']}; }}",
        f".muted {{ fill: {theme['muted']}; }}",
        f".key {{ fill: {theme['key']}; font-weight: 700; }}",
        f".value {{ fill: {theme['value']}; }}",
        f".accent {{ fill: {theme['accent']}; font-weight: 700; }}",
        f".project {{ fill: {theme['project']}; }}",
        "</style>",
        f'<rect x="1" y="1" width="{WIDTH - 2}" height="{HEIGHT - 2}" rx="16" fill="{theme["background"]}" stroke="{theme["border"]}" stroke-width="2"/>',
        f'<line x1="532" y1="20" x2="532" y2="660" stroke="{theme["border"]}" stroke-width="1"/>',
        f'<text x="{ASCII_X}" y="{ASCII_Y}" font-size="{ASCII_FONT_SIZE}px" class="text" clip-path="url(#asciiClip)">',
    ]

    for index, line in enumerate(lines):
        y = ASCII_Y + index * ASCII_LINE_HEIGHT
        svg.append(tspan(ASCII_X, y, line))
    svg.append("</text>")

    y = PANEL_Y
    svg.append(f'<text x="{PANEL_X}" y="{PANEL_Y}" font-size="{PANEL_FONT_SIZE}px" class="text">')
    heading = f'{profile["username"].lower()}@github'
    svg.append(
        f'<tspan x="{PANEL_X}" y="{y}" class="accent">{esc(heading)}</tspan>'
        f'<tspan class="muted"> {"-" * 45}</tspan>'
    )

    y += PANEL_LINE_HEIGHT
    svg.append(rich_line(PANEL_X, y, "Name", str(profile["display_name"])))
    y += PANEL_LINE_HEIGHT
    svg.append(rich_line(PANEL_X, y, "Role", str(profile["role"])))
    y += PANEL_LINE_HEIGHT
    svg.append(rich_line(PANEL_X, y, "Focus", str(profile["focus"])))
    y += PANEL_LINE_HEIGHT
    svg.append(rich_line(PANEL_X, y, "Education", str(profile["education"])))

    y += PANEL_LINE_HEIGHT + 4
    svg.append(section_line(PANEL_X, y, "Technical Stack"))
    y += PANEL_LINE_HEIGHT
    svg.append(rich_line(PANEL_X, y, "Languages", str(profile["languages"])))
    y += PANEL_LINE_HEIGHT
    svg.append(rich_line(PANEL_X, y, "AI.LLM", str(profile["ai_llm"])))
    y += PANEL_LINE_HEIGHT
    svg.append(rich_line(PANEL_X, y, "ML.CV", str(profile["ml_cv"])))
    y += PANEL_LINE_HEIGHT
    svg.append(rich_line(PANEL_X, y, "Backend", str(profile["backend"])))
    y += PANEL_LINE_HEIGHT
    svg.append(rich_line(PANEL_X, y, "Data", str(profile["data"])))
    y += PANEL_LINE_HEIGHT
    svg.append(rich_line(PANEL_X, y, "Cloud.MLOps", str(profile["cloud"])))

    y += PANEL_LINE_HEIGHT + 4
    svg.append(section_line(PANEL_X, y, "Featured Work"))
    for project in profile["projects"]:
        y += PANEL_LINE_HEIGHT
        svg.append(
            f'<tspan x="{PANEL_X}" y="{y:g}" class="muted">. </tspan>'
            f'<tspan class="project">{esc(project)}</tspan>'
        )

    y += PANEL_LINE_HEIGHT + 4
    svg.append(section_line(PANEL_X, y, "Contact"))
    y += PANEL_LINE_HEIGHT
    svg.append(rich_line(PANEL_X, y, "Email", str(profile["email"])))
    y += PANEL_LINE_HEIGHT
    svg.append(rich_line(PANEL_X, y, "LinkedIn", f'/in/{profile["linkedin"]}'))
    y += PANEL_LINE_HEIGHT
    svg.append(rich_line(PANEL_X, y, "GitHub", f'@{profile["username"]}'))

    y += PANEL_LINE_HEIGHT + 4
    svg.append(section_line(PANEL_X, y, "GitHub Stats"))
    y += PANEL_LINE_HEIGHT
    svg.append(
        f'<tspan x="{PANEL_X}" y="{y:g}" class="muted">. </tspan>'
        '<tspan class="key">Repos</tspan><tspan class="muted">: </tspan><tspan class="value" id="repo_data">0</tspan>'
        '<tspan class="muted">  |  </tspan><tspan class="key">Stars</tspan><tspan class="muted">: </tspan><tspan class="value" id="star_data">0</tspan>'
        '<tspan class="muted">  |  </tspan><tspan class="key">Followers</tspan><tspan class="muted">: </tspan><tspan class="value" id="follower_data">0</tspan>'
    )
    y += PANEL_LINE_HEIGHT
    svg.append(
        f'<tspan x="{PANEL_X}" y="{y:g}" class="muted">. Last refresh: </tspan>'
        '<tspan class="value" id="updated_data">run the workflow</tspan>'
    )

    y += PANEL_LINE_HEIGHT + 4
    svg.append(
        f'<tspan x="{PANEL_X}" y="{y:g}" class="accent">$ echo </tspan>'
        f'<tspan class="text">&quot;{esc(profile["tagline"])}&quot;</tspan>'
    )
    svg.append("</text>")
    svg.append("</svg>")
    return "\n".join(svg) + "\n"


def main() -> None:
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    ascii_lines = ASCII_PATH.read_text(encoding="utf-8").splitlines()
    for filename, theme in THEMES.items():
        (ROOT / filename).write_text(render_svg(profile, ascii_lines, theme), encoding="utf-8")
        print(f"generated {filename}")


if __name__ == "__main__":
    main()
