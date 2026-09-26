# Protocolo SDCP v3.0.0 (Smart Device Control Protocol) — Elegoo

El protocolo SDCP es el estándar propietario basado en JSON sobre WebSockets utilizado por Elegoo para controlar sus impresoras CoreXY y de resina modernas.

---

## Estructura de Mensajes SDCP

Todos los paquetes enviados al WebSocket (`ws://<IP>:3030/websocket`) siguen este formato JSON:

```json
{
  "Id": "",
  "Data": {
    "Cmd": 0,
    "Data": {},
    "RequestID": "a1b2c3d4...",
    "MainboardID": "0123456789abcdef",
    "TimeStamp": 1720000000,
    "From": 1
  }
}
```

## Comandos Principales

| Cmd ID | Nombre | Descripción |
| :--- | :--- | :--- |
| `0` | `GET_PRINTER_STATUS` | Solicita el estado en tiempo real (temperaturas, ventiladores, progreso). |
| `1` | `GET_PRINTER_ATTR` | Atributos de máquina (firmware, límites físicos, dimensiones de cama). |
| `128` | `SEND_PRINTER_START_PRINT` | Iniciar impresión de un archivo subido. |
| `129` | `SEND_PRINTER_SUSPEND_PRINT`| Pausar impresión actual. |
| `130` | `SEND_PRINTER_STOP_PRINT` | Detener/cancelar trabajo de impresión. |
| `131` | `SEND_PRINTER_RESTORE_PRINT`| Reanudar impresión pausada. |
| `258` | `GET_PRINTER_FILE_LIST` | Listar archivos gcode / ctb almacenados. |
| `401` | `EDIT_PRINTER_AXIS_NUMBER` | Desplazamiento manual de ejes (Jogging X, Y, Z, E). |
| `402` | `EDIT_PRINTER_AXIS_ZERO` | Homing de ejes (G28). |
| `403` | `EDIT_PRINTER_STATUS_DATA` | Ajustar temperaturas (`TempTargetNozzle`, `TempTargetHotbed`, `TempTargetBox`), luces (`Light: 1/0`) y ventiladores. |
