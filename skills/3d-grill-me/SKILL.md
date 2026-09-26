---
name: 3d-grill-me
description: "Entrevista socrática e implacable de requerimientos mecánicos y funcionales para impresión 3D (estilo Matt Pocock). Usar siempre al inicio de una idea, diseño o modificación de una pieza existente."
triggers:
  - "quiero diseñar"
  - "necesito imprimir"
  - "adapta esta pieza"
  - "modifica este STL"
  - "remix"
  - "soporte para"
  - "diseña una pieza"
  - "grill me"
---

# Skill: 3D Grill-Me (Entrevista de Requerimientos y DFM)

Inspirado en la técnica `/grill-me` de Matt Pocock adaptada a la ingeniería y fabricación aditiva FDM.

> **Propósito:** El 90% de las impresiones 3D fallidas no se deben a la impresora, sino a requerimientos ambiguos, medidas alucinadas o ignorar el método de fabricación. Esta skill fuerza al asistente a detenerse y entrevistar metódicamente al usuario antes de generar código o CAD.

---

## 🚦 Regla Inicial: Identificar el Punto de Partida

Antes de empezar, determina si el proyecto es:

- **Modo A: Greenfield (Diseño desde Cero):** No hay pieza previa. Es un concepto nuevo para resolver un problema.
- **Modo B: Remix & Adaptación (Basado en Pieza Existente):** El usuario tiene un archivo previo (`.stl`, `.step`, `.scad`), una pieza comercial o un diseño descargado que necesita modificar.

---

## 🔍 Protocolo Obligatorio para MODO B (Remix & Adaptación)

Si el usuario va a partir de una pieza existente o patrón geométrico, **DEBES formularle obligatoriamente las siguientes preguntas específicas de conservación**:

1. **Características a CONSERVAR intactas:**
   - ¿Qué interfaces mecánicas deben mantenerse idénticas? (e.g. distancia entre centros de tornillos, diámetro de alojamientos, pestañas snap-fit, contorno exterior, acople macho/hembra).
2. **Características a MODIFICAR, AGREGAR o ELIMINAR:**
   - ¿Qué parte de la pieza actual falla o qué le falta? (e.g. "rompe por la base", "necesito que mida 20 mm más", "quiero añadirle una montura GoPro", "eliminar el clip y poner orificios avellanados").
3. **Disponibilidad de Geometría Base:**
   - ¿Dispones del archivo `.stl`, `.step` o `.scad` original para importarlo directamente al script, o partiremos de tomar medidas con calibre para recrear la interfaz?

---

## 📋 Las 5 Dimensiones del Interrogatorio Socrático

Haz las preguntas de manera conversacional, agrupadas por lógica, sin abrumar con 20 preguntas en un solo bloque. Desciende por las ramas del árbol de decisión:

### 1. Función y Esfuerzos Mecánicos
- ¿Cuál es la carga máxima que soportará la pieza? (¿Peso estático, impacto, vibración, fricción continua?).
- ¿En qué dirección actúan las fuerzas? *(Crucial para determinar la orientación de capas en la Elegoo Centauri Carbon).*

### 2. Entorno y Material
- ¿Dónde vivirá la pieza?
  - ¿Interior a temperatura ambiente? ➔ PLA / PLA+
  - ¿Exteriores expuestos a rayos UV o lluvia? ➔ PETG / ASA
  - ¿Entorno de calor (>55°C, como dentro de un automóvil o cerca de motores)? ➔ ABS / ASA / PA-CF
  - ¿Requiere absorción de impactos o agarre? ➔ TPU flexible

### 3. Piezas de Unión y Fijación (Mating & Fasteners)
- ¿Cómo se monta la pieza?
  - ¿Tornillos directos en plástico (autorroscantes)?
  - ¿Tornillos métricos (M3/M4/M5) con tuerca o insertos roscados de calor (heat-set inserts)?
  - ¿A presión (press-fit) o corredera (sliding-fit)?

### 4. Dimensiones Críticas y Restricciones Físicas
- ¿Cuáles son las medidas exactas del objeto que debe alojar? *(Nunca asumas grosores ni holguras).*
- ¿Existen restricciones de espacio o interferencias alrededor?

### 5. Estética vs. Resistencia vs. Velocidad
- ¿El acabado visual y la ausencia de costuras son prioritarios, o la resistencia mecánica prima sobre la apariencia?

### 6. Enfoque de Modelado (Mecánico vs. Orgánico)
- ¿La pieza es técnica/paramétrica (carcasa, soporte, adaptador, engranaje) o es orgánica/escultural (figura, personaje, mango ergonómico, superficie estética curva)?
  - **Técnica / Paramétrica:** Se enruta a **OpenSCAD** (`skills/parametric-cad`).
  - **Orgánica / Escultural:** Se enruta a **Blender + BlenderMCP** (`skills/blender-mcp`).

### 7. Validación Previa de Tolerancias (Test Coupon)
- Si la pieza involucra un ajuste crítico (press-fit de rodamientos, guías correderas o clips con fricción), **propón al usuario generar una probeta rápida de 10-15 minutos** con `scripts/generate_coupon.py` antes de arriesgar una impresión de varias horas.

---

## 🏁 Cierre de la Entrevista y Persistencia (Grill to Piece Spec)

Para evitar la **pérdida de contexto** (que las decisiones se pierdan al cerrar o truncarse el chat), el agente **NUNCA** deja las conclusiones flotando solo en la conversación. Sigue este procedimiento estricto:

### 1. Presentar el Resumen de Especificaciones (Design Brief) al Usuario:
```markdown
### 📋 Resumen de Especificaciones (Design Brief)
- **Nombre de la pieza:** [nombre_pieza]
- **Tipo de proyecto:** [Greenfield / Remix & Adaptación]
- **Pieza base (si aplica):** [Nombre del archivo o referencia]
- **Rasgos a conservar:** [Lista de geometrías inalterables]
- **Modificaciones requeridas:** [Lista de cambios]
- **Ruta de modelado elegida:** [OpenSCAD (Técnico/Mecánico) / BlenderMCP (Orgánico)]
- **Material seleccionado:** [PLA / PETG / ABS / ASA / TPU / PA-CF]
- **Fuerzas y Cargas:** [Magnitud y dirección]
- **Orientación de capas prevista:** [Plano de mayor resistencia en la Centauri]
- **Fijaciones:** [e.g. 2x M3 insertos térmicos, tornillo M4 avellanado]
- **Tolerancias asignadas:** [e.g. $slop = 0.2 mm]
- **Probeta de prueba previa:** [Sí / No requerida]
```

### 2. Persistir Obligatoriamente en el Repositorio (`pieces/<nombre_pieza>/README.md`):
Una vez que el usuario dé el visto bueno al resumen:
1. **Inicializar la pieza si no existe:**
   ```bash
   python3 scripts/scaffold_piece.py <nombre_pieza> --material <MATERIAL> --desc "<DESCRIPCION>"
   ```
2. **Volcar el Design Rationale:** Escribir o actualizar el bloque `## 📋 Registro de Decisiones de Diseño (Design Rationale)` en `pieces/<nombre_pieza>/README.md`.
3. Esto garantiza un rastro técnico auditable (*paper trail*) permanente que acompaña al código CAD, a la malla STL y al manifest de la pieza durante todo su ciclo de vida.

Una vez persistido, avanza inmediatamente a `skills/spec-advisor`, `skills/parametric-cad` o `skills/blender-mcp`.

