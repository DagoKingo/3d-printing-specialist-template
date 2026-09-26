# Checklist DFM (Design for Additive Manufacturing) — FDM

Asegúrate de comprobar cada uno de estos puntos antes de dar por bueno un modelo para la Elegoo Centauri Carbon.

---

## 1. Orientación de Cargas y Capas
- [ ] **Esfuerzos principales en el plano X-Y:** El laminado FDM es anisótropo. Nunca permitas que una fuerza de flexión o tracción actúe separando capas perpendiculares al eje Z si la pieza es de alta carga.
- [ ] **Apoyo plano en la cama:** Debe existir al menos una cara plana amplia para garantizar adhesión con la lámina PEI texturizada.

## 2. Voladizos (Overhangs) y Puentes (Bridges)
- [ ] **Regla de los 45°:** Las paredes con inclinación menor a 45° respecto a la vertical se imprimen limpiamente sin soporte. Entre 45° y 60° requieren enfriamiento agresivo. A más de 60°, añade soporte o rediseña con chaflanes.
- [ ] **Puentes horizontales:** Puentes de hasta 20-30 mm son viables en la Centauri Carbon con su ventilador auxiliar activado, pero evita techos colgantes sin anclaje en ambos extremos.
- [ ] **Gotas de lágrima en orificios horizontales:** Si un agujero de tornillo se imprime en horizontal (eje Y o X), la parte superior colapsará levemente. Rediséñalo con forma de gota de agua o chaflán a 45° en la cúspide si requiere alta precisión de paso.

## 3. Espesores de Pared y Canales
- [ ] **Espesor mínimo funcional:** 1.2 mm (3 paredes de 0.4 mm). Para piezas que soportan carga mecánica: mínimo 2.4 mm a 3.2 mm (6 a 8 paredes).
- [ ] **Múltiplos de ancho de línea:** Diseña las paredes en múltiplos de 0.4 mm (e.g. 0.8 mm, 1.2 mm, 1.6 mm, 2.0 mm) para evitar rellenos incompletos o zigzags internos innecesarios.

## 4. Pie de Elefante (Elephant's Foot)
- [ ] **Chaflán en base:** Añade un chaflán (chamfer) de 0.4 mm a 0.8 mm a 45° en el borde inferior que contacta con la cama de impresión para compensar el aplastamiento de la primera capa.

## 5. Concentradores de Tensión (Stress Risers)
- [ ] **Evitar esquinas internas vivas a 90°:** Las esquinas vivas internas multiplican las tensiones y son puntos de fractura habituales. Usa redondeos (fillets) de al menos R1.0 mm a R2.5 mm en todas las esquinas interiores sometidas a carga.

---

## 6. Antipatrones y Errores de Diseño Mecánico (Design Mistakes Registry)

Lecciones críticas aprendidas para prevenir fallos durante el montaje:

- [ ] **Stack-up de tornillos y orificios ciegos:** Calcula la suma de espesores: *cabeza de tornillo + grosor de tapa + profundidad de alojamiento*. El tornillo nunca debe tocar el fondo ciego antes de comprimir el ensamble. Añade siempre +1.5 mm de profundidad extra.
- [ ] **Acceso para herramientas (Tool Clearance):** Verifica que un destornillador o llave Allen pueda entrar en línea recta sin chocar con paredes vecinas o voladizos.
- [ ] **Orientación de clips (Snap-fits):** NUNCA imprimas el brazo de un clip en la dirección del eje Z (se romperá en el primer uso). El clip debe trazarse con filamento continuo en X-Y.
- [ ] **Piezas mayores a 256 mm:** Si la pieza excede el volumen de la Centauri Carbon, planifica su división mediante **colas de milano (dovetails)** o encajes machihembrados con holgura de 0.15 mm.

---

## 7. Reglas para Cajas Estancas (IP67) y Texturas
- [ ] **Tornillos fuera del perímetro sellado:** Si el diseño lleva junta de TPU para estanqueidad, los tornillos deben ir en orejetas externas. Los tornillos que atraviesan la cavidad interna provocan fugas por capilaridad a través de la rosca.
- [ ] **Limitador de compresión de junta (Crush Limiters):** Asegura que la junta de TPU se comprima solo entre un **25% y 35%** mediante topes mecánicos rígidos.
- [ ] **Zonas protegidas de textura:** Prohibido aplicar texturas (moleteado, hexágonos o *fuzzy skin*) en caras de apoyo en la cama PEI, orificios de tornillos o caras de sellado hermético.
