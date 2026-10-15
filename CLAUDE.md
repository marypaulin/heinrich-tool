@AGENTS.md

## Claude Code specifics

- Data protection is also recorded in Claude's memory for this project.
  Deny rules in `.claude/settings.json` and a global PreToolUse hook enforce it
  for direct access. Indirect reads — wildcards, scripts that open these files —
  are not caught; the rule above covers them. A blocked call is intentional,
  never work around it.
- Commits follow the global `commit-work` skill; the Git section above fills
  in what it leaves open.
