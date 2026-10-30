# Contributing

This repository packages the open-source
[ControlLoop CLI](https://github.com/controlloop-security/controlloop) as a
skill and plugin for coding-agent hosts. The CLI does the analysis; this
repository only tells an agent how to run it and read its output.

## Ground rules for every change

- **Read-only.** Nothing here edits a user's agent configuration on its own.
  The skill drafts `controlloop.yaml` changes only when asked and leaves
  applying them to the user.
- **Local.** Nothing here sends data anywhere. The one exception is a
  repository that has enabled ControlLoop Team itself, and the skill asks
  before running that gate.
- **No hooks, and nothing at session start.** No `hooks/` directory, no
  `SessionStart` entry, and no MCP server in the main plugin, because hosts
  start a plugin's MCP servers when a session opens. The MCP server lives in
  the separate, opt-in `controlloop-mcp` plugin.
- **One skill.** `skills/controlloop/SKILL.md` is shared by every host. Change
  it once; do not fork it per host.
- **Plain descriptions.** Manifest descriptions say what the plugin does, in
  the CLI's own terms. Directories reject marketing copy.

`python3 scripts/validate.py` checks these rules and the manifests, and runs
on every pull request.

## Sign off your commits

ControlLoop uses the [Developer Certificate of Origin](https://developercertificate.org)
(DCO) instead of a contributor license agreement. By adding a
`Signed-off-by` line to a commit, you certify that you wrote the change, or
otherwise have the right to submit it under the project's license, as the
DCO describes.

Sign off with `-s`, which adds the line using your configured name and
email:

```bash
git commit -s -m "fix: describe the change"
```

The line must name the commit's author:

```text
Signed-off-by: Your Name <you@example.com>
```

A check on every pull request (`.github/workflows/dco.yml`, running
`scripts/check-dco.sh`) fails if any commit lacks a sign-off from its
author. To sign off commits you have already made on your branch:

```bash
git rebase --signoff main
git push --force-with-lease
```

## Commits and review

Use a [Conventional Commit](https://www.conventionalcommits.org) subject,
such as `feat(skill): explain capability ceilings`. Pull requests merge by
squash.

## License

Apache License 2.0. See [LICENSE](LICENSE). Your sign-off certifies the
Developer Certificate of Origin for your contribution.
