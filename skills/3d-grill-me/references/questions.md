# Banco de Preguntas Estructuradas para 3D Grill-Me

Utiliza estas preguntas específicas según la naturaleza del proyecto. No lances todas a la vez; mantén una conversación fluida y técnica.

---

## 🔄 Ramo 1: Remix, Adaptación o Modificación de Pieza Existente

Cuando el usuario tenga un modelo previo o quiera adaptar una pieza de Thingiverse, Printables, MakerWorld o un diseño propio:

1. **Sobre la preservación geométrica:**
   - *"De la pieza que tomas como referencia, ¿qué superficies o características deben mantenerse 100% inalterables?"*
   - *"¿Hay orificios para tornillos, estrías de agarre o un patrón de ventilación que deba replicarse exactamente?"*
   - *"Si la pieza aloja un componente (por ejemplo, el cuerpo de un motor o el conector USB), ¿cuál es el volumen interno que no debemos invadir?"*

2. **Sobre el problema o la modificación:**
   - *"¿Por qué motivo estás rediseñando esta pieza? ¿Falta de rigidez, incompatibilidad de anclaje, rotura por fatiga o cambio de dimensiones?"*
   - *"¿Qué nueva función o anclaje debemos añadirle?"*

3. **Sobre el formato de origen:**
   - *"¿Dispones del archivo `.stl`, `.3mf`, `.step` o `.scad`? Si es un STL, podemos importarlo directamente a OpenSCAD usando `import(\"pieza.stl\")` y aplicar sustracciones o uniones booleanas, o bien tomar medidas y recrear solo la interfaz paramétrica."*

---

## 🛠️ Ramo 2: Piezas Mecánicas y Funcionales (Greenfield)

1. **Cargas y Esfuerzos:**
   - *"¿La fuerza principal será de tracción, compresión, flexión o torsión?"*
   - *"Recuerda que en FDM la unión entre capas (eje Z) es el punto más débil (aproximadamente 40-60% de la resistencia en X-Y). ¿En qué orientación debe colocarse la pieza para que el esfuerzo no abra las capas?"*

2. **Fijaciones y Acoples:**
   - *"¿Cómo se unirá a otras superficies? ¿Tornillos M3/M4 pasantes, tuercas hexagonales empotradas, o insertos roscados de latón para termosellar (heat-set inserts)?"*
   - *"¿Deseas cabezas de tornillo avellanadas (flush) o cilíndricas (socket head)?"*

3. **Espesores y Rigidez:**
   - *"Para una boquilla de 0.4 mm, el espesor de pared mínimo recomendado para rigidez es de 2.0 a 3.0 mm (5 a 7 perímetros). ¿Tienes alguna restricción de grosor?"*

---

## 🎨 Ramo 3: Piezas Estéticas, Carcasas o Figuras

1. **Acabado Superficial:**
   - *"¿Las líneas de capa deben ser imperceptibles (capa de 0.12 - 0.16 mm) o priorizamos rapidez de impresión (0.24 - 0.28 mm)?"*
2. **Costuras y Orientación:**
   - *"¿Hay alguna cara visible prioritaria donde debamos esconder la costura (z-seam) o evitar soportes?"*
3. **Cierres y Encastres:**
   - *"Si es una carcasa o caja, ¿cómo cerrará? ¿Con tapa deslizante, tornillos o pestañas snap-fit?"*
