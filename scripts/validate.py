#!/usr/bin/env python3
"""Check this repository's skills and plugin manifests.

    python3 scripts/validate.py

Standard library only, so it runs on a bare CI image. Exits 1 and names
every problem it finds, otherwise prints a summary and exits 0.

What it enforces:

- every `skills/<name>/SKILL.md` has frontmatter whose `name` is its
  directory name and whose `description` fits the Agent Skills limit;
- every relative link in a skill's Markdown points at a file that exists;
- every manifest that exists parses, and all of them agree on the
  plugin's name and version;
- the ground rules: no hooks anywhere, nothing that runs at session start,
  and no MCP server in the main plugin (hosts start a plugin's MCP servers
  when a session opens; the server ships as the separate opt-in plugin).
"""

from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Agent Skills (agentskills.io): lowercase letters, digits and hyphens.
SKILL_NAME = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?")
MAX_DESCRIPTION = 1024

#: Manifests of the main plugin, at the repository root. Each maps to the
#: JSON path of its name and version.
JSON_MANIFESTS = {
    "plugin.json": ("name", "version"),
    ".claude-plugin/plugin.json": ("name", "version"),
    "gemini-extension.json": ("name", "version"),
}

#: Agent Plugins 1.0 (agent-plugins.org/schemas/1.0.0/plugin.schema.json):
#: the root manifest Codex, Cursor, Copilot CLI and VS Code read. Its
#: top level is closed.
AGENT_PLUGINS_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
AGENT_PLUGINS_KEYS = frozenset(
    {"$schema", "name", "version", "description", "author", "homepage",
     "repository", "license", "keywords", "extensions"}
)
AGENT_PLUGINS_NAME = re.compile(r"[a-z0-9](?:[a-z0-9.-]{0,62}[a-z0-9])?")

#: Files whose presence at the root would start something with a session.
FORBIDDEN_AT_ROOT = (".mcp.json", "mcp.json", "hooks", "hooks.json")

#: Opt-in plugins under plugins/ may carry an MCP server; nothing may carry hooks.
FORBIDDEN_ANYWHERE = ("hooks.json",)

LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")

problems: list[str] = []


def problem(message: str) -> None:
    problems.append(message)


def frontmatter(path: Path) -> dict[str, str]:
    """Top-level `key: value` pairs of a Markdown file's YAML frontmatter.
    Nested blocks are skipped; quoted values are unquoted."""

    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        problem(f"{path.relative_to(ROOT)}: no frontmatter")
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        problem(f"{path.relative_to(ROOT)}: frontmatter is not closed")
        return {}
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line or line[0] in " \t#":
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        fields[key.strip()] = value
    return fields


def check_skills() -> int:
    skill_files = sorted(ROOT.glob("**/skills/*/SKILL.md"))
    if not skill_files:
        problem("no skills/<name>/SKILL.md found")
    for skill in skill_files:
        rel = skill.relative_to(ROOT)
        fields = frontmatter(skill)
        name = fields.get("name", "")
        if name != skill.parent.name:
            problem(f"{rel}: name {name!r} does not match its directory")
        if not SKILL_NAME.fullmatch(name):
            problem(f"{rel}: name {name!r} is not lowercase letters, digits and hyphens")
        description = fields.get("description", "")
        if not description:
            problem(f"{rel}: description is missing")
        elif len(description) > MAX_DESCRIPTION:
            problem(f"{rel}: description is {len(description)} characters, over {MAX_DESCRIPTION}")
        for markdown in sorted(skill.parent.rglob("*.md")):
            for target in LINK.findall(markdown.read_text(encoding="utf-8")):
                if "://" in target or target.startswith("mailto:"):
                    continue
                if not (markdown.parent / target).exists():
                    problem(f"{markdown.relative_to(ROOT)}: link to missing {target}")
    return len(skill_files)


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        problem(f"{path.relative_to(ROOT)}: {error}")
        return None


def check_agent_plugins(data: dict[str, object]) -> None:
    if data.get("$schema") != AGENT_PLUGINS_SCHEMA:
        problem(f"plugin.json: $schema must be {AGENT_PLUGINS_SCHEMA}")
    for key in sorted(set(data) - AGENT_PLUGINS_KEYS):
        problem(f"plugin.json: {key} is not an Agent Plugins 1.0 field")
    name = data.get("name")
    if not isinstance(name, str) or not AGENT_PLUGINS_NAME.fullmatch(name) or ".." in name or "--" in name:
        problem(f"plugin.json: name {name!r} is not a valid Agent Plugins name")
    extensions = data.get("extensions", {})
    if not isinstance(extensions, dict) or not all(isinstance(v, dict) for v in extensions.values()):
        problem("plugin.json: extensions must map namespaces to objects")


def check_manifests() -> int:
    identities: dict[str, tuple[object, object]] = {}
    for rel, (name_key, version_key) in JSON_MANIFESTS.items():
        path = ROOT / rel
        if not path.exists():
            continue
        data = load_json(path)
        if not isinstance(data, dict):
            continue
        identities[rel] = (data.get(name_key), data.get(version_key))
        if rel == "plugin.json":
            check_agent_plugins(data)
        for key in ("hooks", "mcpServers"):
            if key in data:
                problem(f"{rel}: declares {key}; the main plugin has neither")
        if not data.get("description"):
            problem(f"{rel}: description is missing")

    for marketplace in (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"):
        path = ROOT / marketplace
        if not path.exists():
            continue
        data = load_json(path)
        if not isinstance(data, dict) or not isinstance(data.get("plugins"), list):
            problem(f"{marketplace}: has no plugins list")
            continue
        for entry in data["plugins"]:
            source = entry.get("source")
            path_value = source.get("path") if isinstance(source, dict) else source
            if path_value in ("./", "."):
                identities[f"{marketplace} entry"] = (entry.get("name"), entry.get("version"))
            elif isinstance(path_value, str) and not (ROOT / path_value).is_dir():
                problem(f"{marketplace}: plugin {entry.get('name')!r} source {path_value} is missing")

    names = {name for name, _ in identities.values()}
    if len(names) > 1:
        problem(f"manifests disagree on the plugin name: {identities}")
    versions = {version for _, version in identities.values() if version is not None}
    if len(versions) > 1:
        problem(f"manifests disagree on the version: {identities}")

    for command in sorted(ROOT.glob("commands/**/*.toml")):
        data = tomllib.loads(command.read_text(encoding="utf-8"))
        if "!{" in data.get("prompt", ""):
            problem(f"{command.relative_to(ROOT)}: runs a shell command on invocation")
    return len(identities)


def check_ground_rules() -> None:
    for rel in FORBIDDEN_AT_ROOT:
        if (ROOT / rel).exists():
            problem(f"{rel}: the main plugin must not start anything at session start")
    for name in FORBIDDEN_ANYWHERE:
        for path in ROOT.rglob(name):
            if ".git" not in path.parts:
                problem(f"{path.relative_to(ROOT)}: plugins in this repository ship no hooks")
    for path in ROOT.rglob("*"):
        if ".git" in path.parts or not path.is_file() or path.suffix not in (".json", ".toml"):
            continue
        if "SessionStart" in path.read_text(encoding="utf-8", errors="replace"):
            problem(f"{path.relative_to(ROOT)}: mentions SessionStart")


def main() -> int:
    skills = check_skills()
    manifests = check_manifests()
    check_ground_rules()
    if problems:
        for message in problems:
            print(f"error: {message}", file=sys.stderr)
        return 1
    print(f"ok: {skills} skill(s), {manifests} manifest identity record(s), no hooks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
