---
name: elegoo-centauri
description: "Control, monitoreo y comunicación vía WebSocket (SDCP v3.0.0) para la impresora 3D Elegoo Centauri Carbon. Consulta temperaturas de cama/boquilla/cámara, estado de ventiladores, luz, archivos y órdenes de impresión."
triggers:
  - "estado impresora"
  - "temperatura centauri"
  - "conectar centauri"
  - "precalentar"
  - "elegoo centauri"
  - "sdcp"
---

# Skill: Elegoo Centauri Carbon (Control SDCP WebSocket)

Permite al agente o al usuario interactuar directamente con la **Elegoo Centauri Carbon** a través de su protocolo nativo SDCP (Smart Device Control Protocol v3.0.0) en el puerto `3030`.

---

## 📡 Parámetros de Red

- **Protocolo:** WebSocket (`ws://<IP_IMPRESORA>:3030/websocket`).
- **Configuración de IP:** Se define en `config.toml` (o variable de entorno `ELEGOO_PRINTER_IP`).
- **Descubrimiento de MainboardID:** El script auto-descubre el ID de la placa madre en la primera conexión.

---

## 💻 Comandos CLI Disponibles (`scripts/centauri_ctl.py`)

El script `skills/elegoo-centauri/scripts/centauri_ctl.py` provee una interfaz CLI completa:

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
