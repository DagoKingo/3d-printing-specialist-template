# Uniones Mecánicas y Ensambles en Impresión 3D FDM

Guía de diseño de uniones impresas sin tornillos, división de piezas grandes y diseño de carcasas estancas (IP67). Basado en principios de ingeniería de *zabaglione/3d-printing-design-skills* y *Circus-Systems/VibePrint3D*.

---

## 1. Clips Flexibles y Encastres (Snap-Fits)

Los clips a presión tipo viga en voladizo (cantilever snap-fits) permiten ensambles rápidos y desmontables.

### Ecuación de Deformación Admisible (Cantilever Strain)
Para evitar que el clip se quiebre durante la inserción:
$$\epsilon \approx 1.5 \cdot \frac{y \cdot t}{L^2}$$
- $y$: Deflexión necesaria para encastrar (mm)
- $t$: Espesor del brazo del clip (mm)
- $L$: Longitud del brazo (mm)
- $\epsilon$: Deformación unitaria (strain). Para FDM:
  - **PLA:** Máximo 1.0% - 1.5% (material rígido y quebradizo)
  - **PETG:** Máximo 2.0% - 2.5% (excelente elasticidad y fatiga)
  - **ABS / ASA:** Máximo 2.0%
  - **TPU:** > 10% (deformación muy alta)

### Reglas de Oro de Snap-Fits para FDM
1. **Orientación de Capas (CRÍTICO):** El brazo del clip debe imprimirse **apoyado en el plano X-Y**. Si se imprime verticalmente (en eje Z), la fuerza de flexión abrirá las capas inmediatamente.
2. **Radio en la Raíz (Fillet):** NUNCA dejes una esquina viva a 90° en la base del clip. Aplica un radio de redondeo $R \ge 0.5 \cdot t$ para eliminar el concentrador de tensiones.
3. **Ángulos de Entrada y Salida:**
   - **Ángulo de entrada (Lead-in):** 30° a 45° (inserción suave).
   - **Ángulo de retención (Back face):**
     - Desmontable con fuerza moderada: 45° a 60°.
     - Permanente / Bloqueo firme: 90° (requiere herramienta para liberar).

---

## 2. División de Piezas Grandes (> 256 mm) con Colas de Milano (Dovetails)

Cuando un diseño supera el volumen de la **Elegoo Centauri Carbon (256 × 256 × 256 mm)**, debe dividirse en componentes interconectables.

### Parámetros de Cola de Milano (Dovetail) FDM
- **Ángulo de conicidad:** 10° a 15° (un ángulo muy abierto se desliza; muy cerrado concentra esfuerzos).
- **Holgura diametral por cara:** `0.15 mm` a `0.20 mm` en los flancos de deslizamiento.
- **Chaflán de entrada:** Añade un bisel de 1.0 mm a 45° en el extremo de entrada para facilitar la inserción manual.
- **Tope positivo (Hard stop):** Diseña un fondo ciego o pestaña escalonada para que la unión no se pase de largo y quede enrasada.

---

## 3. Cierres de Bayoneta (Twist Locks)

Ideales para tapas de recipientes, filtros o difusores de luz.
- Divide la rotación en 3 o 4 tetones simétricos para repartir la carga.
- Añade una pequeña hendidura o tope de retención (detent) al final del giro (típicamente 30° a 60° de giro) para que la vibración no lo afloje.
- Holgura radial en el canal: `0.25 mm`.

---

## 4. Mecanismos Print-in-Place (Bisagras y Rótulas)

Piezas articuladas impresas ensambladas en una sola operación sin montaje posterior.
- **Holgura entre superficies móviles:**
  - En la Centauri Carbon bien calibrada: `0.35 mm` a `0.40 mm`.
  - Si usas PETG: aumenta a `0.45 mm` debido a la tendencia a hilvanar (stringing).
- **Conicidad en pasadores:** Usa extremos en cono a 45° en lugar de cilindros planos para evitar puentes horizontales que se fusionen durante la impresión.

---

## 5. Diseño de Cajas Estancas y Herméticas (Estándar IP67 FDM)

Para carcasas que deben resistir polvo y agua (inmersión hasta 1 m durante 30 minutos):

### A. Juntas de Estanqueidad en TPU (Gaskets)
- **Tasa de compresión ideal:** **25% a 35%** de la altura libre de la junta de TPU.
- **Limitadores de aplastamiento (Crush Limiters):** La carcasa rígida (PLA/PETG/ASA) debe tener topes mecánicos que hagan tope antes de que el tornillo aplaste la junta al 100%.

### B. Posición de Tornillos (Regla Inquebrantable)
- **Tornillos SIEMPRE fuera del perímetro sellado:** El agua filtra fácilmente a lo largo de las roscas y capas de plástico. Los orificios de tornillos, tuercas o insertos térmicos deben ubicarse en orejetas externas a la junta de sellado.

### C. Acople Macho-Hembra (Tongue-and-Groove)
- Nunca unas dos caras planas para estanqueidad. Diseña un canal perimetral continuo (ranura de 2 a 3 mm de ancho) donde se aloje la junta de TPU, y un nervio saliente en la tapa que la presione.
