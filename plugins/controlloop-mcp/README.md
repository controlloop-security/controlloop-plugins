# controlloop-mcp

An opt-in plugin that runs the ControlLoop CLI's local MCP server,
`controlloop mcp`, so the agent can call `gate`, `diff`, `bom` and `rules`
as tools and get the CLI's JSON back.

It is separate from the main `controlloop` plugin on purpose. Hosts start a
plugin's MCP servers when a session opens, and the main plugin starts
nothing. Install this one only if you want the tools, and disable it when
you don't.

- Needs a `controlloop` on your `PATH` that has the `mcp` command (the CLI
  release after 0.6.1). Check with `controlloop mcp --help`.
- The server is read-only and local: no network (Team is switched off for
  every call), no file written in your repository, and no path outside the
  project. See the CLI's
  [local MCP server](https://github.com/controlloop-security/controlloop/blob/main/docs/reference/mcp-server.md)
  page.
- No hooks.

Install with Claude Code: `/plugin install controlloop-mcp@controlloop`.
With Codex: `codex plugin add controlloop-mcp@controlloop`. With Copilot
CLI: `copilot plugin install controlloop-mcp@controlloop`.
