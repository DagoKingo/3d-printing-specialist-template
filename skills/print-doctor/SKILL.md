---
name: print-doctor
description: "Diagnóstico clínico y resolución de fallos de impresión 3D FDM (Troubleshooting). Especializado en la Elegoo Centauri Carbon: warping, stringing, heat creep, subextrusión, delaminación de capas, pata de elefante, ghosting y problemas de filamento húmedo."
triggers:
  - "falló la impresión"
  - "salió mal"
  - "stringing"
  - "hilos"
  - "warping"
  - "se despegó"
  - "se levantaron las esquinas"
  - "atasco"
  - "clic clic extrusor"
  - "heat creep"
  - "subextrusión"
  - "sobreextrusión"
  - "capas separadas"
  - "layer shift"
  - "salto de capa"
  - "pie de elefante"
  - "print doctor"
  - "diagnóstico impresión"
---

# Skill: 3D Print Doctor (Diagnóstico y Solución de Fallos FDM)

Inspirado en *3d-print-doctor* de Johann-github, adaptado con los parámetros y cinemática de la **Elegoo Centauri Carbon** (CoreXY de alta aceleración, cabina cerrada, extrusor Direct Drive y boquilla de acero endurecido).

> **Objetivo:** Cuando una pieza impresa sale con defectos o la impresión falla a mitad de trabajo, el agente no da respuestas genéricas; actúa como un **médico especialista** que interroga los síntomas con orden clínico, determina la causa raíz y receta la solución exacta (ajuste en OrcaSlicer o mantenimiento de hardware).

---

## 🩺 Protocolo de Entrevista de Diagnóstico (Triage Clínico)

Cuando el usuario reporte un fallo, averigua estos 4 datos clave antes de recetar una solución:

1. **¿Cuál es el síntoma visual exacto?**
   - Hilos finos o telarañas (Stringing)
   - Esquinas despegadas de la cama (Warping)
   - Extrusión discontinua, esponjosa o vacía (Under-extrusion)
   - Separación entre capas horizontales (Delamination)
   - Salto o escalón en las capas (Layer shift)
   - Ondulaciones o sombras cerca de las esquinas (Ghosting / Ringing)
2. **¿Qué material y marca estás usando?** (e.g. PLA, PETG, ABS, ASA, TPU, PA-CF).
3. **¿Cuándo ocurrió el fallo?** (en la primera capa, a mitad de una pieza larga, o tras acelerar a alta velocidad).
4. **¿La cabina estaba abierta o cerrada?** *(Crítico para la Centauri Carbon).*

---

## 🗂️ Rutas de Consulta Rápida

- Para síntomas específicos, causas raíz y correcciones mecánicas: consulta [`references/fdm_troubleshooting.md`](references/fdm_troubleshooting.md).
- Para problemas de humedad, temperaturas de secado y adhesión por tipo de plástico: consulta [`references/filament_doctor.md`](references/filament_doctor.md).

---

## 💊 Diagnósticos Frecuentes en Elegoo Centauri Carbon

### 1. Atasco por "Heat Creep" en PLA (Clic-clic en extrusor tras 1-2 horas)
- **Causa:** Imprimir PLA con la puerta y tapa superior de cristal completamente cerradas. La cabina cerrada retiene el calor de la cama (60°C) y el aire interior supera los 40°C, reblandeciendo el filamento antes de entrar al bloque calefactor.
- **Receta:**
  - Mantener la puerta de cristal ligeramente entreabierta o retirar la tapa superior al imprimir PLA.
  - Verificar que el ventilador del disipador del cabezal esté girando al 100%.

### 2. Hilos (Stringing) excesivos en PETG o PLA
- **Causa:** La Centauri Carbon es **Direct Drive**. Si se usan valores de retracción de impresoras tipo Bowden (3 a 6 mm), entrará aire a la boquilla y se generará hilvanado severo y atascos.
- **Receta en OrcaSlicer:**
  - Distancia de retracción: **0.6 mm a 0.8 mm** (máximo 1.0 mm).
  - Velocidad de retracción: **35 a 45 mm/s**.
  - Activar *Wipe while retracting* (barrido al retraer) con 2 mm de recorrido.
  - Reducir temperatura de boquilla en -5°C.

### 3. Esquinas levantadas (Warping) o grietas en ABS / ASA
- **Causa:** Gradiente térmico brusco por enfriamiento prematuro del plástico.
- **Receta:**
  - **Cabina cerrada obligatoria:** Cerrar puerta y tapa superior.
  - **Precalentamiento de cabina:** Encender la cama a 100°C durante 15 minutos antes de enviar la impresión para crear un ambiente a 45°C dentro de la cabina.
  - **Ventilador de capa:** Reducir al 0% – 10% máximo.
  - Añadir *Brim* (borde exterior) de 8 mm con 0.1 mm de separación de objeto.

### 4. Sombras y ondulaciones (Ghosting / Ringing) en paredes a alta velocidad
- **Causa:** Vibraciones mecánicas a 20,000 mm/s² no compensadas por el Input Shaper o correderas CoreXY destensadas.
- **Receta:**
  - Ejecutar la autocalibración de resonancia (Input Shaping) desde la pantalla táctil de la Centauri.
  - Verificar que ambas correas CoreXY tengan una tensión uniforme (~110-130 Hz).
  - Reducir la velocidad de la *Pared Exterior* a 120-150 mm/s manteniendo las paredes internas rápidas.
