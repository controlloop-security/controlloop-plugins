# Reading ControlLoop's output

This is how `controlloop gate` and `controlloop scan` text output is laid
out in CLI 0.6, and what each part means. The authoritative description is
the CLI's
[terminal report format](https://github.com/controlloop-security/controlloop/blob/main/docs/reference/terminal-report-format.md).

## A blocked example

From the ControlLoop reference agent, a branch that adds a Claude Code
`SessionStart` hook:

```text
! WORST REACHABLE  code-execution: Claude Code can invoke PostToolUse command
  hook (Edit|Write)

✕ DEPLOYMENT BLOCKED

Authority:
  • This change gives Claude Code the power to run `node .github/setup.js` on
    every session start (`.claude/settings.json`, hook `SessionStart`). No
    approval is recorded.

• GAINED  code-execution: Claude Code invokes SessionStart command hook

✕ HIGH     policy.agent-hook-command-change: Added: Hook on event 'SessionStart'
  for host 'Claude Code' runs `node .github/setup.js`.
    at .claude/settings.json

Suppressions: none declared

Completeness enforcement: warn (default)
Evidence: /tmp/controlloop-evidence.json
```

A good explanation: the change adds a hook that runs
`node .github/setup.js` every time a Claude Code session opens in this
repository. It runs before the developer types anything, with their
permissions, and nobody approved it. Rule
`policy.agent-hook-command-change` blocks at high severity. To proceed,
remove the hook. If it is intended, a named reviewer can record an
approval for `.claude/settings.json#hooks.SessionStart[0].hooks[0]`. The
worst-reachable line names a different, pre-existing hook: the most
dangerous capability in the repository is not necessarily the new one.

## The parts, top to bottom

**`! WORST REACHABLE  <class>: <who> can <what>`** is the single most
dangerous capability any agent in the repository can reach now, ranked by
class. It describes the whole repository, not the change. `no material
capability is reachable` means nothing is classified. Tools ControlLoop
cannot classify count as `unclassified`, which ranks worst, because
unknown is never treated as safe.

Material classes: `destructive-action`, `financial-action`,
`code-execution`, `external-communication`, `sensitive-data-access`,
`delegation`, `write-access`, `unclassified`.

**The verdict:**

| Text | JSON `verdict` | Meaning |
| --- | --- | --- |
| `✓ PASSED` | `passed` | Nothing at or above the blocking threshold |
| `! PASSED WITH WARNINGS` | `passed_with_warnings` | Findings below the threshold |
| `! REVIEW REQUIRED` | `review_required` | A person has to look before merging |
| `✕ DEPLOYMENT BLOCKED` | `deployment_blocked` | A finding at or above the threshold (default `high`) |
| `• NOT EVALUATED` | `not_evaluated` | Policy did not run |

**`Authority:`** has one sentence per power the change grants an agent.
Each one names the host, the power, the file and key, and whether an
approval is recorded. These are the sentences to quote. In JSON they are
`authority_delta.entries[].statement`, with `key_path` for drafting an
approval.

**Material changes**, the `• GAINED` and `• LOST` lines, are capabilities
that became reachable or unreachable against the baseline, by class.
`• material change: not evaluated` means there was no baseline: no git
history, or no default branch found. In that case new authority is not
judged as new, and findings say `Recorded on a scan with no baseline`.
Say this explicitly. A pass without a baseline means much less.

**Findings**: `<glyph> <SEVERITY> <rule id>: <message>`, then `at <file>`.
Severities from lowest to highest: `info`, `low`, `medium`, `high`,
`critical`. `✕` marks a finding that blocks, `!` one that warns. Each rule
has a `documentation_url` in `controlloop rules --format json`, covering
what it detects, why, and how to fix it.

**`Suppressions:`** lists repo-local, expiring suppressions in
`controlloop.yaml` that applied. An expired one stops suppressing.

**`Completeness enforcement:`** shows whether incomplete analysis blocks
(`enforce`) or only warns (`warn`, the default). Incomplete analysis
means a file was too large, a parser failed, or code registered tools
dynamically. Mention any diagnostics about it. They mean part of the
repository was not fully read.

**`Evidence:`** is where the evidence artifact was written. With this
skill's `--evidence-path`, that is a temp file outside the repository.

## Common findings and what they mean

| Rule | What happened |
| --- | --- |
| `policy.agent-hook-command-change` | A hook was added or changed: a command the host runs on an event such as session start or after an edit |
| `policy.widened-permission-rule` | An allow rule got broader, for example `Bash(npm test)` became `Bash(*)` |
| `policy.permission-bypass-from-project` | Project settings turn off permission prompts, for example `bypassPermissions` or Codex `approval_policy = "never"` |
| `policy.mcp-server-identity-change` | An MCP server is new, or its package, version, command or host changed under the same name |
| `policy.overprivileged-agent-workflow` | A CI workflow runs a coding agent with write tokens (such as `id-token: write`) and skipped permission prompts, or on untrusted input with no `permissions` block |
| `policy.unpinned-agent-component` | A plugin or marketplace was added or changed without a commit or digest pin, so its contents can change upstream |
| `policy.agent-sandbox-weakened` | A change turns off an agent's sandbox, lets commands run outside it, or opens its network access |
| `policy.capability-ceiling` | An agent can now reach something its `controlloop.yaml` ceiling forbids. Ceilings cannot be suppressed |

Run `controlloop rules` for the full list. Use each rule's documentation
rather than this table when they differ.
