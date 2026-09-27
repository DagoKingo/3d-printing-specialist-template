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

## 0. Identidad del Repositorio, Plantilla Base y Git Upstream

Cualquier agente que ejecute esta skill debe reconocer de inmediato la naturaleza y límites de este repositorio:

1. **Plantilla Base del Repositorio:**
   - Este repositorio implementa la plantilla corporativa **`laga-solutions/3d-printing-specialist-template`**, formalizada en el manifiesto raíz [`template.yaml`](template.yaml).
   - Su rol es **exclusivamente de Especialista en Fabricación Aditiva e Ingeniería CAD 3D** (`role: 3d-printing-specialist`).
   - La skill `print-doctor` actúa como el servicio clínico de resolución de fallos y control de calidad (QA) de piezas impresas.

2. **Verificación Inmediata de Plantilla y Git Upstream:**
   - Remote `upstream` hacia `https://github.com/DagoKingo/3d-printing-specialist-template.git`.
   - Consulta [`template.yaml`](template.yaml) y ejecuta `./scripts/verify-environment.sh`.

3. **Persistencia Obligatoria en `print_feedback.md`:**
   - Toda interacción, síntoma, diagnóstico y prescripción formulada por `print-doctor` **DEBE quedar registrada obligatoriamente en el artefacto `pieces/<nombre_pieza>/print_feedback.md`**.
   - Queda estrictamente prohibido emitir recetas que queden solo en el chat sin actualizar el reporte de feedback ni iterar los archivos de la pieza.

---

Inspirado en *3d-print-doctor* de Johann-github, adaptado con los parámetros y cinemática de la **Elegoo Centauri Carbon** (CoreXY de alta aceleración, cabina cerrada, extrusor Direct Drive y boquilla de acero endurecido).

> **Objetivo:** Cuando una pieza impresa sale con defectos o la impresión falla a mitad de trabajo, el agente no da respuestas genéricas; actúa como un **médico especialista** que interroga los síntomas con orden clínico, determina la causa raíz, receta la solución exacta y la registra formalmente en `pieces/<nombre_pieza>/print_feedback.md`.

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

## 📝 Procedimiento de Ejecución y Registro en `print_feedback.md`

Cuando el usuario brinde retroalimentación sobre una pieza física impresa:

1. **Localizar o Inicializar el Artefacto:**
   - Comprueba si existe `pieces/<nombre_pieza>/print_feedback.md`. Si no existe, inicialízalo con:
     ```bash
     python3 scripts/feedback.py pieces/<nombre_pieza> --init-only
     ```

2. **Interrogar el Síntoma y Determinar Causa Raíz:**
   - Consulta las 4 preguntas de triage y la tabla de diagnósticos frecuentes.
   - Si el problema es dimensional (e.g. apriete excesivo en ejes o barrenos), diagnostica contracción térmica y tolerancia `$slop`.
   - Si el problema es de acabado o adherencia (warping, stringing, pie de elefante), diagnostica temperatura, ventilación y retracción.

3. **Registrar la Consulta y Prescripción:**
   - Ejecuta el comando automatizado de registro o actualiza el archivo directamente:
     ```bash
     python3 scripts/feedback.py pieces/<nombre_pieza> --status ADJUST --symptom tight_fit --notes "Eje de 1/2 pulgada entra forzado"
     ```
   - El script volcará el diagnóstico, la causa raíz y las acciones prescritas en el archivo `pieces/<nombre_pieza>/print_feedback.md`.

4. **Aplicar el Tratamiento (Bucle de Corrección Iterativa):**
   - **Si el cambio es CAD:** Modifica `pieces/<nombre_pieza>/<nombre_pieza>.scad`, compila el nuevo `.stl`, pasa el `verify_mesh.py` y genera el nuevo `.3mf`.
   - **Si el cambio es de Slicer:** Modifica el perfil de corte o ejecuta `export_3mf.py` con los nuevos ajustes y regenera el `.3mf`.
   - Documenta la nueva versión e iteración en `print_feedback.md`.

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
