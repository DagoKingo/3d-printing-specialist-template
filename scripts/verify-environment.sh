#!/usr/bin/env bash
set -u

missing=0
check() {
  if command -v "$1" >/dev/null 2>&1; then
    printf 'OK   %-10s %s\n' "$1" "$("$1" --version 2>&1 | head -n 1)"
  else
    printf 'MISS %-10s %s\n' "$1" "$2"
    missing=1
  fi
}

# Verificación de Manifiesto de Plantilla
if [ -f "template.yaml" ]; then
  TEMPLATE_ID=$(grep -E '^template:' template.yaml | head -n 1 | awk '{print $2}' | tr -d '"'"'")
  ROLE_ID=$(grep -E '^role:' template.yaml | head -n 1 | awk '{print $2}' | tr -d '"'"'")
  printf 'OK   %-10s %s\n' 'manifest' "template.yaml ($TEMPLATE_ID, rol: $ROLE_ID)"
else
  printf 'WARN %-10s %s\n' 'manifest' 'Falta archivo template.yaml en la raíz del repositorio.'
fi

# Verificación de Perfil de Máquina Receptor (PRINTER.md)
if [ -f "PRINTER.md" ]; then
  PRINTER_NAME=$(grep -E 'Modelo Comercial Exacto' PRINTER.md | awk -F'|' '{print $3}' | tr -d '*' | xargs || echo "Elegoo CC2")
  printf 'OK   %-10s %s\n' 'printer' "PRINTER.md ($PRINTER_NAME)"
else
  printf 'WARN %-10s %s\n' 'printer' 'Falta artefacto PRINTER.md en la raíz del repositorio.'
fi

check git 'Instala Git y vuelve a ejecutar.'
check python3 'Se requiere Python 3.10 o posterior para el pipeline de análisis 3D.'

# Verificación de librerías Python FDM (trimesh, numpy)
PYTHON_BIN="python3"
if [ -d "$HOME/.venv-3d" ]; then
  PYTHON_BIN="$HOME/.venv-3d/bin/python3"
fi

if $PYTHON_BIN -c "import trimesh, numpy" >/dev/null 2>&1; then
  TRIMESH_VER=$($PYTHON_BIN -c "import trimesh; print(trimesh.__version__)" 2>/dev/null || echo "instalado")
  printf 'OK   %-10s %s\n' 'trimesh' "trimesh $TRIMESH_VER (en $PYTHON_BIN)"
else
  printf 'WARN %-10s %s\n' 'trimesh' 'Opcional (recomendado): requerido para Printability Gate y volumen. pip install trimesh numpy'
fi

if command -v openscad >/dev/null 2>&1; then
  printf 'OK   %-10s %s\n' openscad "$(openscad --version 2>&1 | head -n 1)"
else
  printf 'INFO %-10s %s\n' openscad 'Opcional: requerido para compilar modelos OpenSCAD (.scad) a STL desde terminal.'
fi

if command -v tgrep >/dev/null 2>&1; then
  printf 'OK   %-10s %s\n' tgrep "$(tgrep --version 2>&1 | head -n 1)"
else
  printf 'INFO %-10s %s\n' tgrep 'Opcional (mandatorio en agentes si está instalado): acelera la búsqueda en archivos.'
fi

if command -v blender >/dev/null 2>&1; then
  printf 'OK   %-10s %s\n' blender "$(blender --version 2>&1 | head -n 1)"
else
  printf 'INFO %-10s %s\n' blender 'Opcional: requerido para Track B (modelado orgánico y BlenderMCP).'
fi

# Verificación y auto-enlace con la plantilla base (upstream)
CURRENT_REPO=$(git remote get-url origin 2>/dev/null || echo "")
if [[ "$CURRENT_REPO" != *"3d-printing-specialist-template"* ]]; then
  if ! git remote get-url upstream >/dev/null 2>&1; then
    git remote add upstream https://github.com/DagoKingo/3d-printing-specialist-template.git
    printf 'INFO %-10s %s\n' 'upstream' 'Configurado automáticamente hacia 3d-printing-specialist-template.'
  fi
fi

if git remote get-url upstream >/dev/null 2>&1; then
  git fetch upstream --quiet 2>/dev/null || true
  if git rev-parse --verify upstream/main >/dev/null 2>&1 && git rev-parse --verify HEAD >/dev/null 2>&1; then
    # Auto-enlace de historial si las historias no están relacionadas
    if ! git merge-base HEAD upstream/main >/dev/null 2>&1; then
      git merge -s ours upstream/main --allow-unrelated-histories -m "chore: link template upstream history" --quiet 2>/dev/null || true
      printf 'INFO %-10s %s\n' 'template' 'Historial enlazado automáticamente con la plantilla base.'
    fi
    BEHIND=$(git rev-list --count HEAD..upstream/main 2>/dev/null || echo 0)
    if [ "$BEHIND" -gt 0 ]; then
      printf 'WARN %-10s %s\n' 'template' "Desactualizado ($BEHIND commit(s) pendientes en upstream/main). Ejecuta: git merge upstream/main"
    else
      printf 'OK   %-10s %s\n' 'template' 'Sincronizado con 3d-printing-specialist-template (upstream/main).'
    fi
  fi
fi

if [ "$missing" -ne 0 ]; then
  printf '\nEntorno incompleto. Verifica las herramientas faltantes.\n'
  exit 1
fi
