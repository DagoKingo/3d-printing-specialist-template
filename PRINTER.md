# 🖨️ PRINTER.md — Ficha Técnica y Perfil de Máquina

> **Artefacto Canónico de Contexto de Hardware:** Este documento es la fuente de verdad técnica para cualquier agente o desarrollador sobre la impresora 3D física receptora, sus capacidades mecánicas, cinemáticas y su sistema multi-material. Debe ser consultado obligatoriamente antes de definir perfiles de corte, seleccionar filamentos o estructurar estrategias de soporte.

---

## 1. Identificación del Hardware Receptor

| Parámetro | Especificación de Fábrica | Implicación en Ingeniería FDM |
| :--- | :--- | :--- |
| **Fabricante / Marca** | **Elegoo** | Ecosistema Elegoo Slicer / OrcaSlicer |
| **Modelo Comercial Exacto** | **Elegoo Centauri Carbon 2 (CC2)** | Perfil base de corte: `0.20mm Standard @Elegoo CC2 0.4 nozzle` |
| **Sistema Multi-Material** | **Elegoo Canvas** | Alimentador automático multi-filamento con corte motorizado |
| **Capacidad Multi-Material** | **4 bahías (slots)** automatizadas | Permite alternar materiales incompatibles y colores en el mismo trabajo |
| **Cinemática** | **CoreXY** de alta aceleración | Aceleraciones hasta 20,000 mm/s², velocidad de desplazamiento 500 mm/s |
| **Volumen de Impresión** | **256 × 256 × 256 mm** | Centro de cama en (128.0, 128.0, 0.0) |
| **Tipo de Cabina** | **Cerrada hermética** con filtración | Apta para retener calor (>45°C) en ABS, ASA y PA-CF sin warping |

---

## 2. Sistema Térmico y Cabezal de Extrusión

- **Hotend:** Todo metal (*All-Metal*) hasta **300 °C**.
- **Boquilla Predeterminada:** **Acero endurecido de 0.40 mm** (apta para filamentos abrasivos reforzados con fibra de carbono PA-CF, PETG-CF y partículas minerales).
- **Cama Caliente:** Placa magnética flexible con recubrimiento de **PEI Texturizado** hasta **110 °C**. Proporciona acabado mate industrial homogéneo en la cara en contacto con Z=0.
- **Ventilación y Enfriamiento:**
  - Ventilador de capa dual en cabezal.
  - Ventilador auxiliar de cabina lateral (*auxiliary fan*).
  - Filtro de extracción con carbón activado para retener COVs (VOCs) en ABS/ASA.

---

## 3. Capacidades Avanzadas con Elegoo Canvas Multi-Material

La presencia del sistema **Elegoo Canvas** desbloquea estrategias de fabricación aditiva que **eliminan las limitaciones del monomaterial**:

### A. Soportes de Cero Cicatriz con Materiales Incompatibles (*Zero-Gap Interface*)
Al contar con cambio automático de filamento, **queda estrictamente prohibido usar soportes monomaterial con colchones de aire defectuosos en voladizos planos críticos** cuando se dispone de material de interfaz incompatible:

| Material del Cuerpo de la Pieza | Material de la Interfaz de Soporte | Distancia Z de Contacto (`support_top_z_distance`) | Espaciado de Interfaz (`support_interface_spacing`) | Resultado Superficial |
| :--- | :--- | :--- | :--- | :--- |
| **ABS / ASA** | **PETG** | **`0.00 mm` (Contacto Total)** | **`0.00 mm` (100% Sólida)** | **Acabado espejo/liso**. El ABS se comprime con squish total contra el PETG. Al enfriar se separan sin pegarse químicamente. |
| **PLA** | **PETG** | **`0.00 mm` (Contacto Total)** | **`0.00 mm` (100% Sólida)** | Desprendimiento perfecto sin adherencia intermolecular. |
| **PETG** | **PLA** | **`0.00 mm` (Contacto Total)** | **`0.00 mm` (100% Sólida)** | Superficie inferior idéntica a una cara plana de cama. |

### B. Torre de Purga y Transición (*Prime Tower*)
- Al activar multi-material en el laminador, se debe configurar una **Torre de Purga (Prime Tower)** en la esquina posterior de la cama (típicamente X: 210-230 mm, Y: 210-230 mm) con volumen de purga calibrado (típicamente 180-240 mm³) para garantizar que no queden restos de filamento incompatible en la boquilla antes de volver a imprimir la pieza.

### C. Impresión Bicolor / Multi-Componente Nativa
- Las piezas con leyendas, hendiduras o flechas indicadoras (como la aguja del Honeywell Slate R8001M1150) pueden laminarse como **ensamble multi-material en un solo trabajo `.3mf`**:
  - Ranura 1: ABS Gris (Cuerpo estructural)
  - Ranura 2: PETG Naranja (Inserto / Flecha indicadora integrada o interfaz de soporte)

---

## 4. Matriz Canónica de Ranuras Canvas (Slots)

| Ranura (Slot) | Material | Color Típico | Rol Principal en Proyectos |
| :---: | :---: | :---: | :--- |
| **Slot 1** | **ABS** | Gris / Negro | Piezas mecánicas estructurales de alta temperatura ($T_g \approx 105^\circ\text{C}$) |
| **Slot 2** | **PETG** | Naranja / Blanco / Traslúcido | Flechas indicadoras de contraste / **Interfaz de soporte anti-adherente para ABS** |
| **Slot 3** | **PLA** | Blanco / Negro | Prototipado rápido, plantillas dimensionales y probetas de calibración |
| **Slot 4** | **PA-CF / TPU** | Negro / Especial | Materiales de alta resistencia al desgaste o empaquetaduras flexibles |

---

## 5. Parámetros de Red y Protocolo de Monitoreo (SDCP)

- **Protocolo:** SDCP v3.0.0 (Smart Device Control Protocol) sobre WebSocket.
- **Puerto de Comunicación:** `3030`.
- **Comandos Soportados:** Consulta de telemetría en tiempo real (temperaturas de boquilla/cama/cámara, estado de ventiladores, posición de ejes, estado de ranuras Canvas, control de luz LED y cámara integrada).
- **Herramienta CLI:** [`skills/elegoo-centauri/scripts/elegoo_sdcp.py`](skills/elegoo-centauri/scripts/elegoo_sdcp.py).

---

## 6. Directivas para Agentes de IA

1. **Contexto Obligatorio:** Todo agente debe leer este archivo antes de sugerir o exportar proyectos `.3mf`.
2. **Preset de Sistema:** Los perfiles de corte deben anclarse a `"Elegoo Centauri Carbon 2 0.4 nozzle"` y `"0.20mm Standard @Elegoo CC2 0.4 nozzle"`.
3. **Prioridad Multi-Material en Voladizos Críticos:** Si una pieza monomaterial presenta un voladizo horizontal plano donde el soporte convencional degrade la superficie, el agente **DEBE proponer utilizar el sistema Canvas con interfaz incompatible (ABS + PETG a Z=0.00 mm)** para lograr una cara inferior 100% sólida y plana.
