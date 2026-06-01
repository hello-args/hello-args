#!/usr/bin/env python3
"""Generate recent open-source contribution table for profile README."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

USER = os.environ.get("GITHUB_USER", "hello-args")
PROFILE_REPO = f"{USER}/hello-args"
README_PATH = os.environ.get("README_PATH", "README.md")
MARKER_START = "<!-- recent-oss:start -->"
MARKER_END = "<!-- recent-oss:end -->"
MAX_ROWS = 8

LOOT_DROPS = [
    '+10 observability, boss debuffs "where did it die?"',
    "Achievement: *Agents Must Scream*",
    "Loot: merged PR, +5 GitHub street cred",
    "Debuff removed: silent failure",
    "Rare drop: maintainer said LGTM",
    "Side quest complete: docs updated",
    "Buff: CI green on first try (allegedly)",
    "Epic: touched prod without incident",
]


def api_get(url: str, token: str) -> dict | list:
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def loot_for(repo: str, title: str) -> str:
    key = sum(ord(c) for c in repo + title) % len(LOOT_DROPS)
    return LOOT_DROPS[key]


def relative_time(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - dt
        days = delta.days
        if days == 0:
            return "today"
        if days == 1:
            return "yesterday"
        if days < 30:
            return f"{days}d ago"
        if days < 365:
            return f"{days // 30}mo ago"
        return f"{days // 365}y ago"
    except ValueError:
        return ""


def truncate(text: str, max_len: int = 52) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def fetch_merged_prs(token: str) -> list[dict]:
    q = urllib.parse.quote(
        f"author:{USER} is:pr is:merged -repo:{PROFILE_REPO} sort:updated-desc"
    )
    url = f"https://api.github.com/search/issues?q={q}&per_page=30"
    data = api_get(url, token)
    return data.get("items", [])


def fetch_public_events(token: str) -> list[dict]:
    url = f"https://api.github.com/users/{USER}/events/public?per_page=100"
    return api_get(url, token)


def patch_from_pr(item: dict) -> str:
    title = item.get("title", "Contribution")
    labels = [lb["name"] for lb in item.get("labels", [])]
    if labels:
        return truncate(f"{title} `{labels[0]}`")
    return truncate(title)


def patch_from_event(event: dict) -> str:
    etype = event.get("type", "")
    payload = event.get("payload", {})
    if etype == "PushEvent":
        commits = payload.get("commits") or []
        if commits:
            return truncate(commits[-1].get("message", "push"))
        return "pushed commits"
    if etype == "PullRequestEvent":
        pr = payload.get("pull_request") or {}
        return truncate(pr.get("title", "pull request"))
    if etype == "IssuesEvent":
        issue = payload.get("issue") or {}
        return truncate(issue.get("title", "issue"))
    if etype == "CreateEvent":
        ref = payload.get("ref", "")
        return truncate(f"created `{ref}`" if ref else "repository activity")
    return truncate(etype.replace("Event", "").lower())


def collect_contributions(token: str) -> list[dict]:
    rows: list[dict] = []
    seen_repos: set[str] = set()

    for item in fetch_merged_prs(token):
        repo = item.get("repository_url", "").rstrip("/").split("/repos/")[-1]
        if not repo or repo in seen_repos or repo == PROFILE_REPO:
            continue
        if repo.split("/")[0].lower() == USER.lower() and repo.count("/") == 1:
            # skip own user repos unless explicitly whitelisted OSS
            if repo.startswith(f"{USER}/"):
                continue
        seen_repos.add(repo)
        rows.append(
            {
                "repo": repo,
                "url": f"https://github.com/{repo}",
                "patch": patch_from_pr(item),
                "loot": loot_for(repo, item.get("title", "")),
                "when": relative_time(item.get("updated_at", "")),
                "sort": item.get("updated_at", ""),
            }
        )
        if len(rows) >= MAX_ROWS:
            return rows

    for event in fetch_public_events(token):
        repo_obj = event.get("repo") or {}
        repo = repo_obj.get("name", "")
        if not repo or repo in seen_repos or repo == PROFILE_REPO:
            continue
        owner = repo.split("/")[0]
        if owner.lower() == USER.lower():
            continue
        etype = event.get("type", "")
        if etype not in {
            "PushEvent",
            "PullRequestEvent",
            "IssuesEvent",
            "CreateEvent",
            "PullRequestReviewEvent",
        }:
            continue
        if etype == "PullRequestEvent":
            action = (event.get("payload") or {}).get("action", "")
            if action not in {"opened", "closed", "merged"}:
                continue
        seen_repos.add(repo)
        rows.append(
            {
                "repo": repo,
                "url": f"https://github.com/{repo}",
                "patch": patch_from_event(event),
                "loot": loot_for(repo, patch_from_event(event)),
                "when": relative_time(event.get("created_at", "")),
                "sort": event.get("created_at", ""),
            }
        )
        if len(rows) >= MAX_ROWS:
            break

    rows.sort(key=lambda r: r.get("sort", ""), reverse=True)
    return rows[:MAX_ROWS]


def build_markdown(rows: list[dict]) -> str:
    lines = [
        "| Project | Recent contribution | Loot drop |",
        "|---------|---------------------|-----------|",
    ]
    if not rows:
        lines.append(
            "| — | No recent public OSS events in the feed *(yet)* | "
            "Equip: `git clone` and cause trouble |"
        )
    else:
        for row in rows:
            project = f"[**{row['repo'].split('/')[-1]}**]({row['url']})"
            patch = f"{row['patch']} *({row['when']})*" if row["when"] else row["patch"]
            lines.append(f"| {project} | {patch} | {row['loot']} |")
    lines.append("")
    lines.append(
        f"<sub>Auto-refreshed from GitHub · last sync: "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</sub>"
    )
    return "\n".join(lines)


def update_readme(fragment: str) -> None:
    with open(README_PATH, encoding="utf-8") as f:
        content = f.read()
    if MARKER_START not in content or MARKER_END not in content:
        print(f"Markers not found in {README_PATH}", file=sys.stderr)
        sys.exit(1)
    before, rest = content.split(MARKER_START, 1)
    _, after = rest.split(MARKER_END, 1)
    updated = f"{before}{MARKER_START}\n{fragment}\n{MARKER_END}{after}"
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated)


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN is required", file=sys.stderr)
        sys.exit(1)
    try:
        rows = collect_contributions(token)
        fragment = build_markdown(rows)
        update_readme(fragment)
        print(f"Updated {README_PATH} with {len(rows)} OSS contribution(s).")
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"GitHub API error: {e.code} {body}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
