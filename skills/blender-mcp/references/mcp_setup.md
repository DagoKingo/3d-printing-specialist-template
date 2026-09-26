# Configuración de BlenderMCP para Agentes de IA

Permite que tu asistente controle Blender directamente desde el chat.

---

## 1. Requisitos Previos
- **Blender 4.0 o superior** instalado en tu sistema.
- **Python con `uv` o `pip`**: Se recomienda `uv` para ejecutar servidores MCP sin ensuciar el entorno.

---

## 2. Instalación de BlenderMCP

El servidor oficial de BlenderMCP se ejecuta con `uvx`:
```bash
uvx blender-mcp
```
O con `pipx`:
```bash
pipx run blender-mcp
```

En la primera ejecución, BlenderMCP te guiará para instalar el addon complementario dentro de Blender (Edit > Preferences > Add-ons).

---

## 3. Configuración en Agentes

### En Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"]
    }
  }
}
```

### En Google Antigravity / AGY / OpenCode
Añade la entrada correspondiente en tu configuración local de MCP o en `~/.gemini/antigravity-cli/config.json`:
```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"]
    }
  }
}
```
Consulta el archivo [`mcp_servers.example.json`](file:///home/dago/repos/3d-printing-specialist-template/mcp_servers.example.json) en la raíz de este repositorio.
