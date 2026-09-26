---
name: slicer-advisor
description: "Asesor de perfiles y ajustes de corte en OrcaSlicer y Elegoo Slicer. Optimiza parámetros según la intención de la pieza (resistencia mecánica, prototipado rápido, estética fina, materiales técnicos) para la Elegoo Centauri Carbon."
triggers:
  - "slicer"
  - "parámetros de corte"
  - "OrcaSlicer"
  - "Elegoo Slicer"
  - "infill"
  - "relleno"
  - "perímetros"
  - "costura"
  - "seam"
  - "soporte"
---

# Skill: Slicer Advisor (OrcaSlicer & Elegoo Centauri Carbon)

Optimiza los parámetros de corte (slicing) en **OrcaSlicer** o **Elegoo Slicer** en función del objetivo real de la pieza física.

---

## 🎯 Perfiles por Intención (Intent-Based Slicing)

No existe una configuración única. Clasifica la intención del usuario en una de estas 4 categorías:

### 1. Resistencia Mecánica Máxima (Piezas Funcionales / Soportes)
- **Loops de pared (Wall loops):** 5 a 6 paredes (más efectivo para resistencia que aumentar el % de infill).
- **Capas superior / inferior:** 5 a 6 capas.
- **Patrón de relleno:** `Gyroid` o `3D Honeycomb` al 25% - 40% (resistencia isotrópica sin solapamiento de líneas).
- **Ancho de línea:** 0.45 mm (para boquilla de 0.4 mm, mejora la adhesión inter-capas).
- **Ventilador de capa:** Moderado (30-50% en PETG/ABS; 70-80% en PLA) para maximizar la fusión inter-capas.

### 2. Prototipado Rápido (Draft / Verificación de Encaje)
- **Altura de capa:** 0.28 mm.
- **Loops de pared:** 2 paredes.
- **Relleno:** `Grid` o `Lightning` al 10% - 15%.
- **Velocidad de impresión:** 300 - 450 mm/s (aprovechando la cinemática CoreXY de la Centauri Carbon).
- **Capas superiores:** 3 a 4.

### 3. Alta Definición y Estética (Miniaturas / Carcasas Visibles)
- **Altura de capa:** 0.12 mm a 0.16 mm (o altura de capa adaptativa).
- **Loops de pared:** 3 paredes.
- **Posición de costura (Seam):** `Alineada` (Aligned) o `Trasera` (Back), o colocada manualmente en aristas vivas ocultas.
- **Modo planchado (Ironing):** Activado en la capa superior más alta (Topmost surface) a 30 mm/s y 15% de flujo para acabado suave como molde de inyección.

### 4. Materiales Técnicos (ABS / ASA / PA-CF en Cámara Caliente)
- **Cámara:** Completamente cerrada.
- **Brim (Borde):** Activado (5 mm con holgura de 0.1 mm) para prevenir despegado de esquinas.
- **Enfriamiento:** Mínimo (0-15%) para evitar delaminación por contracción térmica.
- **Velocidad de pared exterior:** Reducir a 80-120 mm/s para asegurar brillo y unión molecular.

---

## 🖨️ Especificaciones del Perfil Elegoo Centauri Carbon

Consulta `references/centauri_carbon_specs.md` para las aceleraciones máximas, volumen de cama (256x256x256 mm) y cinemática.
