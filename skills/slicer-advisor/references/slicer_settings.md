# Guía de Ajustes de Slicer para OrcaSlicer & Elegoo Slicer

Ajustes detallados para afinar la calidad y resistencia mecánica.

---

## 1. Patrones de Relleno (Infill)
- **Gyroid (Giroide):** El patrón más recomendado para casi cualquier pieza funcional. Ofrece resistencia uniforme en todas las direcciones tridimensionales, no cruza líneas sobre la misma capa (evitando choques de boquilla a 300 mm/s) y permite drenaje si se sella.
- **Cross Hatch / Grid:** Rápido de imprimir pero sufre choques en intersecciones. No recomendado para CoreXY a alta velocidad.
- **Adaptive Cubic:** Densidad progresiva que se vuelve más densa cerca de las capas superiores, ahorrando material en el centro sin sacrificar soporte de techos.

## 2. Ajuste de Paredes vs. Relleno
> **Regla de Resistencia:** 1 pared perimetral adicional aporta mucho más aguante a la flexión y tracción que un 15% adicional de relleno, consumiendo menos tiempo de impresión.

- Piezas decorativas: 2 paredes.
- Piezas de uso ligero: 3 a 4 paredes.
- Piezas de sujeción / esfuerzo mecánico: 5 a 6 paredes.

## 3. Control de Costura (Seam)
- **Scarf Joint Seam (OrcaSlicer v2.0+):** OrcaSlicer introdujo la unión biselada (Scarf Seam) que difumina el inicio y final del bucle de pared, haciendo la costura prácticamente invisible en piezas cilíndricas.
- **Esquinas internas:** En piezas mecánicas con esquinas vivas, coloca la costura en la arista interior más oculta (`Seam: Aligned`, o pintar costura manualmente).

## 4. Soportes (Tree / Árbol vs. Snug / Normal)
- **Soportes en árbol orgánicos (Tree Supports - Hybrid / Slim):**
  - Consumen hasta un 60% menos filamento.
  - Se desprenden fácilmente sin dejar marcas en la superficie.
  - Ideales para casi todas las geometrías con voladizos.
- **Distancia de contacto superior (Top Z distance):**
  - PLA: `0.20 mm` (fácil despegue).
  - PETG: `0.24 mm` a `0.28 mm` (el PETG se suelda fuertemente; aumentar distancia o usar interfaz de PLA).

---

## 5. Archivos STEP (B-Rep) vs. STL y Arcos G2/G3 en OrcaSlicer

OrcaSlicer y Elegoo Slicer cuentan con soporte nativo para importar modelos en formato **`.step` / `.stp`**.

### Ventajas de importar `.step` en lugar de `.stl`:
1. **Superficies matemáticas reales sin polígonos:** Un cilindro en STL es una aproximación de muchas caras planas (facetado). En un archivo STEP, es una superficie analítica exacta.
2. **Ajuste de Arcos (Arc Fitting - Comandos G2/G3):**
   - OrcaSlicer detecta las curvas puras del archivo STEP y genera comandos nativos `G2` (arco horario) y `G3` (arco antihorario) en lugar de cientos de pequeños movimientos lineales `G1`.
   - **Beneficio para la Centauri Carbon:** A 300-500 mm/s, miles de micro-segmentos `G1` saturan el buffer del firmware provocando micro-pausas (stuttering). Los arcos `G2/G3` garantizan movimientos fluidos a máxima velocidad y orificios de tornillo y rodamiento perfectamente circulares.
3. **Configuración recomendada en OrcaSlicer:**
   - Activar: `Quality > Advanced > Arc fitting: Enabled`.
   - Resolución de arco: `0.01 mm`.
