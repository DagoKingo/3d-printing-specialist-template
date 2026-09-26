# GEMINI.md

See [AGENTS.md](file:///home/dago/repos/3d-printing-specialist-template/AGENTS.md) for complete instructions, workflows, and 3D printing engineering guidelines.

## Imperative Shell Policies
- **Text Search:** When searching code or files via shell commands, always prefer `tgrep` over `grep`. Check if installed with `command -v tgrep` before executing, falling back to `grep` only if unavailable.
- **Pieces & Artifacts:** All newly designed or adapted 3D pieces must be placed in `pieces/<piece_name>/` alongside their full artifact bundle (`.scad`/`.blend`, `.stl`, `.3mf`, `manifest.json`, `viewer.html`, `renders/`, `README.md`). Use `python3 scripts/scaffold_piece.py <piece_name>` to scaffold new pieces.
- **Part Number & Target Device Locking:** Never truncate, abbreviate, or generalize commercial model numbers or hardware identifiers (e.g. keep `Honeywell Slate R8001M1150` intact; never truncate to `R8001M`). Always record the exact model in `README.md`, `manifest.json` (`--target-device`), and CAD files.
- **Target Hardware Technical Dossier:** When researching target components or datasheets, always document all relevant technical data (exact part number, manufacturer, shaft/mating dimensions, keyways, torque, operating temperature ranges, datasheet links) directly into `pieces/<piece_name>/README.md` to inform CAD dimensions, material selection, and slicing parameters.
