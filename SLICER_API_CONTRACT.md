# 📡 SLICER_API_CONTRACT.md — Contrato Oficial de Red, Slicer y Control de Máquina

> **Artefacto Canónico de Protocolo y Contrato de Red:** Este documento formaliza la especificación técnica estricta de las interfaces de red, comandos SDCP/MQTT y contratos de despacho del Slicer para la **Elegoo Centauri Carbon 2 (CC2)** y su sistema multi-material **Elegoo Canvas**.  
> **Propósito:** Prevenir de forma absoluta la herencia ciega de sintaxis, parámetros o presets de otros fabricantes (Bambu Lab, Klipper/Moonraker, Creality CFS, PrusaConnect) en scripts de automatización, agentes de IA o herramientas de corte.

---

## 1. Arquitectura de Red y Matriz de Puertos

La Elegoo Centauri Carbon 2 expone cuatro canales de comunicación independientes en la red LAN:

| Puerto | Protocolo | Autenticación / Requisitos | Función Técnica |
| :---: | :---: | :---: | :--- |
| **`1883`** | **MQTT** | `access_code` (API Key en pantalla de máquina) | Canal maestro de control bidireccional SDCP v3.0 (comandos, telemetría y eventos). |
| **`80`** | **HTTP** | Ninguna (LAN directa) | Carga binaria multipart/chunked de archivos `.gcode` y proyectos `.3mf` hacia el almacenamiento interno `/local`. |
| **`8080`** | **HTTP (MJPEG)** | Ninguna (LAN directa) | Transmisión de video óptico continuo en vivo a 30 FPS (`http://<IP>:8080/?action=stream`). Cero consumo de tokens de IA. |
| **`3030`** | **WebSocket** | Handshake SDCP | Telemetría push de alta frecuencia para interfaces táctiles y dashboards locales. |

---

## 2. Contrato Oficial de Despacho de Impresión Multi-Material (Cmd 1020: `start_print`)

### Esquema JSON Estricto
Extraído quirúrgicamente del código fuente del plugin oficial de ElegooSlicer (`elegoolink/web/lan_service_web/index.html`):

```json
{
  "filename": "<nombre_archivo>.gcode",
  "storage_media": "local",
  "storage": "local",
  "config": {
    "delay_video": false,
    "printer_check": true,
    "print_layout": "A",
    "bedlevel_force": false,
    "slot_map": [
      { "t": 0, "canvas_id": 0, "tray_id": 0 },
      { "t": 1, "canvas_id": 0, "tray_id": 1 }
    ]
  },
  "task_bed_leveling": true,
  "auto_bed_leveling": 1,
  "task_record_timelapse": false,
  "task_use_ams": true,
  "use_ams": true,
  "ams_mapping": [0, 1]
}
```

### Especificación de Parámetros Críticos

| Campo | Tipo | Obligatorio | Descripción / Regla de Oro |
| :--- | :---: | :---: | :--- |
| `filename` | `string` | **SÍ** | Nombre exacto del archivo G-code ya existente en el almacenamiento de la impresora. |
| `storage_media` | `string` | **SÍ** | Destino del archivo. Debe ser siempre `"local"` (almacenamiento eMMC/flash interno) o `"udisk"`. |
| `config` | `object` | **SÍ** | Contenedor de configuración de firmware para ejecución en cabezal. |
| `config.slot_map` | `array` | **SÍ en Multi-Material** | **Mapeo explícito de herramientas lógicas a bahías físicas Canvas.** Sin este campo, el firmware degrada la impresión a monomaterial. |
| `config.slot_map[].t` | `integer` | **SÍ** | Índice de herramienta lógica definida en el Slicer (`0` para `T0`, `1` para `T1`). |
| `config.slot_map[].canvas_id` | `integer` | **SÍ** | Identificador de la unidad Canvas física (predeterminado: `0`). |
| `config.slot_map[].tray_id` | `integer` | **SÍ** | Índice físico de la bahía/slot donde reside el filamento (`0` = Bahía A, `1` = Bahía B, etc.). |
| `config.delay_video` | `boolean` | Opcional | Si es `true`, activa la captura de video timelapse capa por capa. |
| `config.printer_check` | `boolean` | Opcional | Verificación previa de hardware y calibración antes de imprimir. |

---

## 3. Cláusula de Aislamiento de Ecosistema (Anti-Bambu / Anti-Klipper)

> [!CAUTION]
> **Mecanismo de Falla por Herencia Ciega:**
> En plataformas Bambu Lab (BambuStudio / Bambu Handy), el mapeo de bobinas del AMS se transmite habitualmente mediante cadenas o listas simples como `"task_use_ams": true` y `"ams_mapping": "[0, 1]"`.
> 
> En la **Elegoo Centauri Carbon 2**, si el script o cliente API envía los parámetros de Bambu Lab pero **omite el objeto `config.slot_map`**, el firmware clasifica el trabajo internamente como `MQTT单色打印` (impresión monomaterial). En consecuencia:
> 1. La máquina imprimirá todo el archivo con la bobina activa inicial (ej. 100% ABS).
> 2. Todas las macros de corte `M6211` y llamadas `T1` serán ignoradas o generarán pausas erróneas.
> 3. En soportes Zero-Gap, el cuerpo se soldará térmicamente al soporte por no alimentar el material incompatible.
> 
> **Regla Inquebrantable:** Queda terminantemente prohibido despachar trabajos a la CC2 sin construir e inyectar el bloque `config.slot_map` cuando el pasaporte técnico declare `use_ams: true`.

---

## 4. Contrato de Telemetría y Estados de Máquina (Cmd 1002: `status`)

* **Método SDCP:** `1002` (vía MQTT o WebSocket).
* **Diccionario de Estados Principales (`state`):**
  * `state = 1`: **IDLE** (Máquina en reposo, lista para recibir trabajos).
  * `state = 2`: **PRINTING / PREPARING** (En preparación, calentamiento activo o imprimiendo capa).
  * `state = 3`: **PAUSED** (Pausa manual o por sensor de filamento).
  * `state = 4`: **COMPLETED** (Trabajo finalizado exitosamente).
  * `state = 5`: **STOPPED / CANCELLED** (Trabajo abortado por el usuario o por error).

---

## 5. Contrato de Monitoreo Canvas Multi-Material (Cmd 1003: `canvas_status`)

* **Método SDCP:** `1003`.
* **Ruta de Acceso:** `canvas_info.canvas_list[0].tray_list[]`.
* **Codificación de Estados de Bahía (`tray_list[].status`):**
  * `status = 0`: **VACÍO** (No hay carrete de filamento detectado en la bahía).
  * `status = 1`: **CARGADO / LISTO** (Filamento presente en el alimentador de la bahía, listo para ser empujado al cabezal).
  * `status = 2`: **EN CABEZAL / ACTIVO** (El filamento de esta bahía se encuentra actualmente cargado a través del tubo PTFE y alojado en el bloque extrusor).
* **Criterio de Validación Pre-Vuelo:** Tanto `status == 1` como `status == 2` son estados válidos y aptos para autorizar el lanzamiento de una herramienta asignada a esa bahía.

---

## 6. Integración con Herramientas del Repositorio

1. **Aduana Pre-Vuelo ([`scripts/preflight_audit.py`](scripts/preflight_audit.py)):** Audita que el G-code contenga las llamadas `T0`/`T1` y `M6211`, y valida contra la máquina viva que las bahías declaradas en el pasaporte cumplan `status in (1, 2)`.
2. **Control por Línea de Comandos (`centauri print start`):** Debe construirse siempre con `--use-ams --ams-mapping "[0, 1]"` asegurando que la librería subyacente ensamble el objeto `config.slot_map` estipulado en este contrato.
3. **Preset de Slicer Oficial:** ElegooSlicer / OrcaSlicer con perfil base anclado a `"0.20mm Standard @Elegoo CC2 0.4 nozzle"`.
