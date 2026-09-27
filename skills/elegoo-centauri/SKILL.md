---
name: elegoo-centauri
description: "Control, monitoreo y comunicación vía WebSocket (SDCP v3.0.0) y servidor MCP Kiln para la impresora 3D Elegoo Centauri Carbon. Consulta temperaturas de cama/boquilla/cámara, estado de ventiladores, luz, archivos, snapshots de cámara y órdenes de impresión."
triggers:
  - "estado impresora"
  - "temperatura centauri"
  - "conectar centauri"
  - "precalentar"
  - "elegoo centauri"
  - "sdcp"
  - "kiln"
  - "camara centauri"
---

# Skill: Elegoo Centauri Carbon (Control SDCP WebSocket y Kiln MCP)

## 0. Identidad del Repositorio, Plantilla Base y Git Upstream

Cualquier agente que ejecute esta skill debe reconocer de inmediato la naturaleza y límites de este repositorio:

1. **Plantilla Base del Repositorio:**
   - Este repositorio implementa la plantilla corporativa **`laga-solutions/3d-printing-specialist-template`**, formalizada en el manifiesto raíz [`template.yaml`](template.yaml).
   - Su rol es **exclusivamente de Especialista en Fabricación Aditiva e Ingeniería CAD 3D** (`role: 3d-printing-specialist`).
   - La skill `elegoo-centauri` provee la capa de comunicación y control de hardware para la máquina de referencia **Elegoo Centauri Carbon**.

2. **Verificación Inmediata de Plantilla y Git Upstream:**
   - Remote `upstream` hacia `https://github.com/DagoKingo/3d-printing-specialist-template.git`.
   - Consulta [`template.yaml`](template.yaml) y ejecuta `./scripts/verify-environment.sh`.

---

Permite al agente o al usuario interactuar directamente con la **Elegoo Centauri Carbon** a través de su protocolo nativo SDCP (Smart Device Control Protocol v3.0.0) en el puerto `3030`. Ofrece dos modalidades de operación:
1. **Modo Directo / Ligero (`centauri_ctl.py`):** Script Python nativo sin dependencias pesadas.
2. **Modo Servidor MCP Autónomo ([Kiln](https://github.com/codeofaxel/Kiln)):** Servidor MCP para agentes con cámara web, verificación de seguridad (*pre-flight checks*), slicing y gestión de colas.

---

## 📡 Parámetros de Red

- **Protocolo:** WebSocket SDCP (`ws://<IP_IMPRESORA>:3030/websocket`).
- **Configuración de IP:** Se define en `config/config.toml` (o variable de entorno `ELEGOO_PRINTER_IP` / `KILN_PRINTER_HOST`).
- **Descubrimiento de MainboardID:** Auto-descubrimiento en la primera conexión.

---

## 🤖 Modalidad A: Servidor MCP Autónomo con Kiln (`kiln3d`)

[Kiln](https://github.com/codeofaxel/Kiln) es un servidor MCP open-source que implementa control nativo para la Elegoo Centauri Carbon sobre SDCP sin requerir autenticación.

### 1. Configuración MCP (`config/mcp_servers.example.json`)
Agrega la configuración en tu entorno de agentes (Claude, Antigravity, etc.):
```json
{
  "mcpServers": {
    "kiln": {
      "command": "uvx",
      "args": ["--from", "kiln3d", "kiln", "serve"],
      "env": {
        "KILN_PRINTER_HOST": "192.168.1.50",
        "KILN_PRINTER_TYPE": "elegoo"
      }
    }
  }
}
```

### 2. Capacidades Expuestas vía MCP al Agente
- **Telemetría y Estado:** `kiln status` (temperaturas de boquilla/cama/cámara, estado de trabajo y porcentaje).
- **Inspección Visual (Webcam):** `kiln snapshot --save photo.jpg` (captura instantánea de la cámara interna para control de primera capa y detección de spaghetti).
- **Homing y Parqueo Seguro:** `kiln home --plan` y `kiln park` (evita colisiones con piezas ya impresas en la cama).
- **Diagnóstico del Sistema:** `kiln doctor` (verifica conectividad de red, estado de la boquilla y límites de temperatura).
- **Slicing y Envío:** `kiln slice <modelo.stl> --print-after` (genera G-code y envía a la Centauri Carbon).

---

## 💻 Modalidad B: Comandos CLI Directos (`scripts/centauri_ctl.py`)

Para operaciones rápidas en terminal o cuando no se dispone del servidor MCP activo:

### 1. Consultar Estado y Temperaturas
```bash
python3 skills/elegoo-centauri/scripts/centauri_ctl.py status
```
*Muestra:* Estado actual (Idle, Printing, Paused), temperatura actual/objetivo de boquilla, cama y cámara, velocidad de ventiladores y luz.

### 2. Precalentar para Impresión
```bash
# Precalentar para PLA (Boquilla 210°C, Cama 60°C)
python3 skills/elegoo-centauri/scripts/centauri_ctl.py preheat --nozzle 210 --bed 60

# Precalentar cámara para ABS/ASA (Cama 100°C)
python3 skills/elegoo-centauri/scripts/centauri_ctl.py preheat --bed 100
```

### 3. Control de Luces y Ventiladores
```bash
# Encender o apagar luz de cabina
python3 skills/elegoo-centauri/scripts/centauri_ctl.py light on
python3 skills/elegoo-centauri/scripts/centauri_ctl.py light off

# Controlar ventilador auxiliar al 80%
python3 skills/elegoo-centauri/scripts/centauri_ctl.py fan --aux 80
```

### 4. Pausar, Reanudar o Cancelar Impresión
```bash
python3 skills/elegoo-centauri/scripts/centauri_ctl.py pause
python3 skills/elegoo-centauri/scripts/centauri_ctl.py resume
python3 skills/elegoo-centauri/scripts/centauri_ctl.py stop
```

### 5. Listar Archivos en la Memoria Interna
```bash
python3 skills/elegoo-centauri/scripts/centauri_ctl.py files
```
