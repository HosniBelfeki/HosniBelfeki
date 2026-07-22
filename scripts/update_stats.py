#!/usr/bin/env python3
"""Refresh public GitHub statistics in both profile SVGs."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PROFILE = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
USERNAME = os.getenv("PROFILE_USERNAME", str(PROFILE["username"]))
TOKEN = os.getenv("GITHUB_TOKEN", "")
API = "https://api.github.com"


def request_json(path: str) -> object:
    request = urllib.request.Request(
        f"{API}{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{USERNAME}-profile-readme",
            "X-GitHub-Api-Version": "2022-11-28",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API request failed ({exc.code}): {body}") from exc


def fetch_stats() -> dict[str, int | str]:
    user = request_json(f"/users/{urllib.parse.quote(USERNAME)}")
    if not isinstance(user, dict):
        raise RuntimeError("Unexpected GitHub user response")

    stars = 0
    page = 1
    while True:
        repos = request_json(
            f"/users/{urllib.parse.quote(USERNAME)}/repos?type=owner&per_page=100&page={page}"
        )
        if not isinstance(repos, list):
            raise RuntimeError("Unexpected GitHub repositories response")
        stars += sum(int(repo.get("stargazers_count", 0)) for repo in repos if isinstance(repo, dict))
        if len(repos) < 100:
            break
        page += 1

    return {
        "repo_data": int(user.get("public_repos", 0)),
        "star_data": stars,
        "follower_data": int(user.get("followers", 0)),
        "updated_data": datetime.now(timezone.utc).strftime("%Y-%m-%d UTC"),
    }


def update_svg(path: Path, stats: dict[str, int | str]) -> None:
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    tree = ET.parse(path)
    root = tree.getroot()
    for element_id, value in stats.items():
        node = root.find(f".//*[@id='{element_id}']")
        if node is None:
            raise RuntimeError(f"Missing SVG element #{element_id} in {path.name}")
        node.text = f"{value:,}" if isinstance(value, int) else value
    tree.write(path, encoding="utf-8", xml_declaration=True)
    print(f"updated {path.name}")


def main() -> None:
    stats = fetch_stats()
    for filename in ("dark_mode.svg", "light_mode.svg"):
        update_svg(ROOT / filename, stats)


if __name__ == "__main__":
    main()
