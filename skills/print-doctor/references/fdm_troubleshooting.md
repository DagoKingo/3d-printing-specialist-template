# Matriz Clínica de Diagnóstico de Fallos FDM (Troubleshooting)

Especializada en cinemática CoreXY de alta velocidad y la Elegoo Centauri Carbon.

---

## 1. Problemas de Extrusión y Superficie

### A. Hilvanado y Pelusa (Stringing / Oozing)
- **Síntoma:** Telarañas o hilos finos entre torres o al viajar de una sección a otra.
- **Causas y Soluciones:**
  1. *Retracción incorrecta en Direct Drive:* Configurar entre 0.6 mm y 0.8 mm a 40 mm/s.
  2. *Temperatura excesiva:* Bajar temperatura de boquilla en pasos de 5°C.
  3. *Humedad en filamento:* Si se escuchan chasquidos ("popping") o los hilos son grumosos, el filamento está húmedo (especialmente PETG, TPU o PA-CF). Secar antes de continuar.
  4. *Modo Combing / Avoid crossing walls:* Activar en OrcaSlicer para que los desplazamientos ocurran dentro del relleno y no crucen perímetros expuestos.

### B. Subextrusión (Under-Extrusion)
- **Síntoma:** Capas con huecos, paredes esponjosas, acabado frágil que se rompe con los dedos.
- **Causas y Soluciones:**
  1. *Heat Creep (Atasco térmico progresivo):* La extrusión empieza bien y empeora tras 1 hora. Típico en PLA con cabina cerrada. **Solución:** Abrir puerta superior y verificar ventilador de hotend.
  2. *Boquilla parcialmente obstruida:* Partículas o residuos quemados. **Solución:** Realizar una extracción en frío (*cold pull*) a 90°C con Nylon o PLA, o limpiar con aguja de acupuntura.
  3. *Velocidad superior al flujo volumétrico del hotend:* Si imprimes a 400 mm/s con capa de 0.28 mm, puedes superar los 22-26 mm³/s del hotend. **Solución:** Reducir velocidad o limitar el *Max volumetric speed* en el perfil de filamento de OrcaSlicer.
  4. *Tensión insuficiente en los engranajes del extrusor:* El motor patina y deja polvo de plástico en las ruedas. **Solución:** Ajustar el tornillo prisionero de tensión del extrusor dual-gear.

### C. Sobreextrusión y Costuras Prominentes (Over-Extrusion & Blobs)
- **Síntoma:** Gotas en las esquinas, relieve rugoso en paredes, bultos notables en la costura Z.
- **Causas y Soluciones:**
  1. *Multiplicador de flujo alto:* Calibrar el *Flow Ratio* en OrcaSlicer (típicamente 0.96 a 0.98 en PLA/PETG).
  2. *Pressure Advance descalibrado:* Los arranques y paradas de línea acumulan exceso de presión. **Solución:** Calibrar la torre de Pressure Advance en OrcaSlicer (valores típicos para Direct Drive: 0.02 a 0.045 s).

---

## 2. Problemas Térmicos y de Primera Capa

### A. Esquinas Levantadas y Despegue (Warping)
- **Síntoma:** Las esquinas de la base se levantan de la placa texturizada PEI curvando la pieza.
- **Causas y Soluciones:**
  1. *Cama fría o corriente de aire en ABS/ASA/Nylon:* Requiere cabina sellada a 45°C y cama a 100°C.
  2. *Placa PEI contaminada con grasa:* Las huellas dactilares impiden la adhesión del plástico fundido. **Solución:** Lavar la placa de acero flexible con agua tibia y jabón lavavajillas antigrasa (Fairy/Dawn) usando estropajo suave. No basta con alcohol isopropílico si hay acumulación de grasa.
  3. *Falta de Brim (Borde exterior):* En piezas rectangulares grandes, añadir un Brim de 8 a 10 mm con orejetas en las esquinas (*mouse ears*).
  4. *Primera capa demasiado rápida:* Reducir la velocidad de la primera capa a 30-40 mm/s con altura de capa de 0.24 mm.

### B. Pie de Elefante (Elephant's Foot)
- **Síntoma:** El primer milímetro de la base sobresale hacia afuera impidiendo el encaje dimensional.
- **Causas y Soluciones:**
  1. *Temperatura de cama excesiva:* El plástico de las primeras capas se mantiene blando por encima de su temperatura de transición vítrea ($T_g$) y el peso superior lo aplasta. Bajar 5°C la cama tras la primera capa.
  2. *Compensación en Slicer:* Ajustar en OrcaSlicer el parámetro `Elephant foot compensation` a `0.15 mm` - `0.20 mm`.
  3. *Chaflán CAD:* Diseñar siempre un chaflán a 45° de 0.6 mm en la base del modelo.

### C. Delaminación y Agrietamiento Inter-capas
- **Síntoma:** Grietas horizontales en paredes, la pieza se parte como pizarra al ejercer fuerza.
- **Causas y Soluciones:**
  1. *Ventilador de capa demasiado alto:* Enfría la capa anterior antes de que la nueva se funda molecularmente. Bajar el ventilador al 10-20% en PETG/ABS y 0% en Nylon.
  2. *Temperatura de boquilla insuficiente:* La boquilla de acero endurecido de la Centauri disipa más lento que el latón; subir la temperatura de boquilla en +5°C a +10°C.

---

## 3. Problemas Mecánicos y Cinemáticos (CoreXY)

### A. Salto de Capa (Layer Shift)
- **Síntoma:** A partir de cierta altura, todo el modelo se desplaza varios milímetros en el eje X o Y formando un escalón.
- **Causas y Soluciones:**
  1. *Colisión con relleno Grid/Crosshatch:* A 300 mm/s, el cabezal choca con las intersecciones de plástico sólido del relleno Grid provocando pérdida de pasos en los motores. **Solución:** Usar SIEMPRE relleno `Gyroid` que nunca cruza líneas sobre la misma capa.
  2. *Tensión asimétrica o excesiva en correas CoreXY:* Comprobar que ambas correas tengan la misma tensión afinada.
  3. *Aceleración excesiva en esquinas:* Reducir la aceleración de desplazamiento de 20,000 a 10,000 mm/s² si la pieza tiene voladizos que se levantan al enfriar.

### B. Ondulaciones y Sombras (Ghosting / Ringing)
- **Síntoma:** Eco o repetición de letras, esquinas u orificios en las paredes lisas adyacentes.
- **Causas y Soluciones:**
  1. *Vibraciones mecánicas de la mesa:* La Centauri Carbon tiene mucha masa móvil y aceleración violenta. Si la mesa se tambalea, la inercia rebota en la boquilla. **Solución:** Colocar la impresora sobre una mesa sólida o losa de hormigón/pavimento con base de espuma densa.
  2. *Input Shaper descalibrado:* Ejecutar la calibración de resonancia en el menú de la impresora.
