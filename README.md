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

Plugins for each host are added here as they are released.

## License

Apache License 2.0. See [LICENSE](LICENSE).
