# GEMINI.md

See [AGENTS.md](file:///home/dago/repos/3d-printing-specialist-template/AGENTS.md) for complete instructions, workflows, and 3D printing engineering guidelines.

## Imperative Shell Policies
- **Text Search:** When searching code or files via shell commands, always prefer `tgrep` over `grep`. Check if installed with `command -v tgrep` before executing, falling back to `grep` only if unavailable.
