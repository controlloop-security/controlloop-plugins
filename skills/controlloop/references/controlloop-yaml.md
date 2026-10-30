# Drafting controlloop.yaml changes

Draft these only when the user asks, and show them in your reply. The user,
or a reviewer they name, applies them. `controlloop.yaml` is the repository's
own record of what its agents are allowed to do, so a change to it is a
policy decision. The authoritative reference is the CLI's
[manifest schema](https://github.com/controlloop-security/controlloop/blob/main/docs/reference/manifest-schema.md).

If the repository has no `controlloop.yaml`, suggest
`controlloop init <path> --dry-run`. It prints a starter manifest built
from what discovery found, including a starter capability ceiling, and
writes nothing. Every manifest needs `schema_version` (currently `"1.3.0"`)
and `owner`.

## Names

Every field that names something discovery found takes the name discovery
produced, spaces included: `Issue a refund`, not `issue-refund`. When unsure,
run `controlloop bom <path>` and read the node names. `owner` and `approver`
are the exception: they are plain identifiers with no spaces, such as
`platform-team` or `jane-doe`.

## Recording an approval for a change

When a change is intended, an approval turns its authority statement from
`No approval is recorded.` into `Approval recorded.` It also lowers that
component's agent-authority finding to `info`, naming the approver, so the
change no longer blocks. Take `capability` from the JSON entry's `path` and
`key_path` (`<file>#<key path>`), or use the component's name, such as an MCP
server's name. Ask the user who approves it; never fill in a name yourself.

```yaml
schema_version: "1.3.0"
owner: platform-team
approvals:
  - capability: ".claude/settings.json#hooks.SessionStart[0].hooks[0]"
    approver: jane-doe
    expires_at: "2027-01-31T00:00:00Z"   # optional; RFC 3339
```

An expired approval stops counting, and the change blocks again. Suggest
an expiry for anything that is not meant to be permanent.

## Declaring what a tool does (`tool_capabilities`)

Without declarations ControlLoop cannot classify a tool. Its blast radius
then says `no material capability is reachable`, or ranks the tool as
`unclassified`. Declare only what the user tells you a tool does. Use
`"unknown"` when they do not know, which ControlLoop ranks worst.

```yaml
tool_capabilities:
  - tool: Issue a refund        # the discovered tool name
    financial_action: true
    read_only: false
    sensitivity: confidential
  - tool: Look up an order
    read_only: true
    sensitivity: confidential
```

Attributes: `destructive`, `financial_action`, `code_execution`,
`external_communication`, `read_only`, `privileged`, `requires_approval`
(booleans or `"unknown"`), `sensitivity`, `data_classes`.

## Capping what an agent may ever do (`ceilings`)

A ceiling blocks any authority outside it, including routes no rule
anticipates, and cannot be suppressed. An entry without `agent` applies to
every agent.

```yaml
ceilings:
  - prohibited_data_classes: [restricted]
    prohibited_external_destinations: [pastebin.com]
  - agent: refund-agent
    prohibited_resources: [customer-payment-methods]
    prohibited_actions: [writes]
    prohibited_delegation_targets: [unapproved-agent]
```

## After the change

Once the user has applied the change, rerun the gate with the same
`--evidence-path` and show what changed: the approval note on the authority
statement, the lowered finding, or the new ceiling's findings. Do not
suppress a finding to make a gate pass. Suppressions exist (see
[suppressions](https://github.com/controlloop-security/controlloop/blob/main/docs/reference/suppressions.md)),
but they need a written reason and an expiry from the user, and they never
cover a capability ceiling.
