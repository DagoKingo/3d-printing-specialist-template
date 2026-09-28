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

Permite al agente o al usuario interactuar directamente con la **Elegoo Centauri Carbon** a través de su protocolo nativo SDCP (Smart Device Control Protocol v3.0.0). Ofrece dos modalidades de operación:
1. **Canal Primario / Recomendado (CLI `centauri` vía MQTT):** `~/.venv-3d/bin/centauri` (pycentauri) sobre MQTT puerto `1883` + HTTP puertos `80`/`8080`. Es la vía verificada en campo: el puerto WS `3030` puede estar cerrado según firmware/estado.
2. **Fallback / Ligero (`centauri_ctl.py` vía WebSocket):** Script Python sobre WS puerto `3030`. Requiere el módulo `websockets` en el venv del proyecto. Usar solo si el canal MQTT no responde.
3. **Modo Servidor MCP Autónomo ([Kiln](https://github.com/codeofaxel/Kiln)):** Servidor MCP para agentes con cámara web, verificación de seguridad (*pre-flight checks*), slicing y gestión de colas.

> [!CAUTION]
> **Orden canónico de canales (lección de campo 2026-09-27):** intentar siempre primero `centauri status` (MQTT `:1883`). Si el WS `:3030` responde `Connection refused`, NO es un fallo del script ni falta de librería: es el firmware con ese puerto cerrado. Seguir por MQTT sin reintentos al WS.

---

## 📡 Parámetros de Red y Contrato Oficial (`SLICER_API_CONTRACT.md`)

Todo agente que interactúe con la máquina o prepare envíos debe cumplir estrictamente el contrato formalizado en [`SLICER_API_CONTRACT.md`](../../SLICER_API_CONTRACT.md):
- **Puerto 1883 (MQTT):** Control maestro SDCP v3.0 autenticado con `access_code`.
- **Puerto 80 (HTTP):** Subida binaria de archivos G-code y 3MF (`/local`).
- **Puerto 8080 (HTTP):** Stream de video en vivo MJPEG (`http://<IP>:8080/?action=stream`).
- **Puerto 3030 (WebSocket):** Telemetría continua.

> [!CAUTION]
> **Prohibición de Herencia Bambu Lab / AMS en Despacho (Regla 17):**
> Al iniciar trabajos multi-material (Canvas), el payload del método 1020 (`start_print`) **DEBE incluir obligatoriamente** el bloque `config.slot_map` mapeando `{ "t": <herramienta>, "canvas_id": 0, "tray_id": <bahía> }`.
> Parámetros estilo Bambu Lab (`task_use_ams: true`, `ams_mapping: [0, 1]`) sin `config.slot_map` causan que el firmware degrade la impresión a monomaterial en silencio.

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

## 💻 Modalidad B: Comandos CLI Directos (`centauri`, primario) y Fallback WS (`scripts/centauri_ctl.py`)

Canal primario para operaciones rápidas en terminal (verificado en campo vía MQTT `:1883`):
```bash
~/.venv-3d/bin/centauri status
~/.venv-3d/bin/centauri canvas
```
*Muestra:* Estado actual (Idle, Printing, Paused), temperatura actual/objetivo de boquilla, cama y cámara, velocidad de ventiladores y luz.

Fallback solo si MQTT no responde — requiere `websockets` instalado en el venv (`~/.venv-3d` ya lo incluye; el `python3` del sistema, no):

### 1. Consultar Estado y Temperaturas (fallback WS)
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

---

## ⏱️ Política de Frugalidad de Tokens y Monitoreo por Hitos Discretos

El agente **TIENE ESTRICTAMENTE PROHIBIDO ejecutar bucles continuos de sondeo (*polling loops*)** durante la fabricación:
1. **La máquina es autónoma:** El archivo G-code ya reside en la memoria local y la placa Klipper/CC2 ejecuta el trabajo sin supervisión activa de la IA.
2. **Impacto en tokens:** Un bucle de sondeo cada minuto durante 45 minutos recarga ~80,000 tokens de contexto por turno, quemando más de **3.5 a 4.5 millones de tokens** sin aportar valor técnico.
3. **Protocolo Canónico de 3 Hitos:**
   - **Hito 1 (Fin de Calentamiento / Primera Capa ~10-12 min):** Consulta única de telemetría y captura óptica (snapshot) para verificar la adherencia (*squish*) y descartar desprendimiento temprano.
   - **Hito 2 (Transición Crítica / Soporte Multi-Material, si aplica):** Consulta puntual tras el primer cambio de herramienta o inicio de soporte incompatible (PETG/ABS).
   - **Hito 3 (Fin de Fabricación / Post-Print Triage):** Notificación de pieza lista, enfriamiento seguro e inicio de la inspección física (`skills/print-doctor`).
4. **Monitoreo Local Cero Tokens (Out-of-Band):**
   - Transmisión en vivo MJPEG: `http://<IP_IMPRESORA>:8080/?action=stream` (30 FPS en navegador).
   - Telemetría en consola: `centauri status` o `centauri canvas`.
