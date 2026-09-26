# Texturas Funcionales, Nervaduras y Torretas en FDM

Directrices para mejorar la rigidez estructural, el agarre táctil y la estética sin comprometer las tolerancias mecánicas.

---

## 1. Zonas Protegidas (Protected Regions) — Regla Crítica de DFM

Antes de aplicar cualquier textura en el CAD o habilitar *Fuzzy Skin* (piel rugosa) en OrcaSlicer:

> [!CAUTION]
> **NUNCA apliques textura en:**
> 1. **Caras de asiento y acoplamiento mecánico** (flanges, juntas de estanqueidad, encajes machihembrados).
> 2. **Orificios y avellanados de tornillos** (provoca que las cabezas de tornillo queden torcidas o los insertos térmicos entren descentrados).
> 3. **La cara base en contacto con la cama PEI** (arruina la adhesión de la primera capa y provoca desprendimiento durante la impresión).

Siempre delimita una máscara o zona de guarda limpia de al menos **2.0 mm a 3.0 mm** alrededor de cualquier agujero o borde funcional.

---

## 2. Texturas Táctiles y Moleteado (Knurling)

Para diales, perillas, mangos de herramientas y tapas a rosca:

- **Moleteado Diamante (Diamond Knurling):** Ranuras cruzadas a ±45° o ±60°.
  - **Profundidad de relieve:** `0.6 mm` a `1.0 mm`.
  - **Paso (Pitch):** Mínimo `1.5 mm` a `2.5 mm` entre estrías para que una boquilla de 0.4 mm trace los valles y crestas con nitidez.
- **Estrías longitudinales (Ribbed Grip):** Canales verticales paralelos. Se imprimen de forma mucho más limpia en el eje Z que patrones con voladizos pronunciados.

---

## 3. Nervaduras de Refuerzo (Structural Ribs)

Aumentan el momento de inercia y la rigidez a la flexión sin añadir exceso de masa ni alargar los tiempos de impresión:

| Parámetro | Regla para FDM | Motivo |
| :--- | :--- | :--- |
| **Espesor de la nervadura ($t_{rib}$)** | $0.5 \cdot t_{pared}$ a $0.7 \cdot t_{pared}$ | Evita marcas de contracción superficial (sink marks) y enfriamiento disparejo. |
| **Altura máxima de nervadura** | $\le 3 \cdot t_{pared}$ | Nervaduras excesivamente altas son propensas a pandeo o delaminación. |
| **Radio en la raíz (Root fillet)** | $R \approx 0.25 \cdot t_{pared}$ | Distribuye las tensiones en la unión nervadura-placa. |
| **Espaciado entre nervaduras** | $\ge 2 \cdot t_{pared}$ | Permite ventilación de capa y previene sobrecalentamiento local. |

---

## 4. Torretas para Tornillos (Screw Bosses)

Las torretas que alojan tornillos o insertos roscados de latón suelen ser puntos de falla si se diseñan como simples cilindros aislados:

1. **Unión a paredes adyacentes:** Siempre que sea posible, conecta la torreta a la pared lateral más cercana mediante una pequeña nervadura o cartabón (gusset).
2. **Espesor de pared de la torreta:** Mínimo **1.6 mm a 2.4 mm** de pared alrededor del inserto térmico (4 a 6 perímetros) para resistir la fuerza radial de inserción sin agrietarse.
3. **Chaflán de desahogo en la base:** Evita que el radio interno choque con la cabeza del tornillo o el componente a fijar.
