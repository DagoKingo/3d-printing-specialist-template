# GEMINI.md

See [AGENTS.md](file:///home/dago/repos/3d-printing-specialist-template/AGENTS.md) for complete instructions, workflows, and 3D printing engineering guidelines.

## Imperative Shell Policies
- **Text Search:** When searching code or files via shell commands, always prefer `tgrep` over `grep`. Check if installed with `command -v tgrep` before executing, falling back to `grep` only if unavailable.
- **Pieces & Artifacts:** All newly designed or adapted 3D pieces must be placed in `pieces/<piece_name>/` alongside their full artifact bundle (`.scad`/`.blend`, `.stl`, `.3mf`, `manifest.json`, `viewer.html`, `renders/`, `README.md`). Use `python3 scripts/scaffold_piece.py <piece_name>` to scaffold new pieces.
