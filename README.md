# ControlLoop plugins

Skills and plugins that let a coding agent run the open-source
[ControlLoop CLI](https://github.com/controlloop-security/controlloop) and
explain its answer to "what does this change let my agents do?"

ControlLoop reads agent configuration (Claude Code, Codex, Gemini CLI,
Cursor, Kiro and Copilot settings, MCP declarations, agent-running
workflows, A2A cards, OpenAPI, AWS IAM, and CrewAI, LangGraph and OpenAI
Agents SDK code) and reports the authority a change adds, with a
deterministic verdict. These plugins run it locally and read its output.
They do not edit your configuration and do not send anything anywhere.

## The skill

[`skills/controlloop/SKILL.md`](skills/controlloop/SKILL.md) is one
[Agent Skill](https://agentskills.io) shared by every host. It tells the
agent to:

1. find the CLI (`controlloop` on `PATH`, else `uvx controlloop` after
   asking, else show the install options; it never installs anything);
2. run `controlloop gate` against the default branch, writing the evidence
   file to a temp directory rather than the repository;
3. quote the verdict and each authority statement, explain the worst
   reachable capability and each finding, and link the rule's
   documentation;
4. draft `controlloop.yaml` approvals, tool declarations or ceilings only
   when asked, and leave applying them to you.

## Install

Every plugin runs the `controlloop` CLI you already have, or `uvx controlloop`
after asking you. Install the CLI with
`brew install controlloop-security/controlloop/controlloop`,
`uv tool install controlloop`, or `pipx install controlloop`.

### Claude Code

```text
/plugin install controlloop --marketplace controlloop-security/controlloop-plugins
```

On Claude Code older than 2.1.275, add the marketplace first:

```text
/plugin marketplace add controlloop-security/controlloop-plugins
/plugin install controlloop@controlloop
```

Then ask "what does this change let my agents do?", or run
`/controlloop:review` (optionally with a directory and
`--default-branch <name>`).

Plugins for the other hosts are added here as they are released.

## License

Apache License 2.0. See [LICENSE](LICENSE).
