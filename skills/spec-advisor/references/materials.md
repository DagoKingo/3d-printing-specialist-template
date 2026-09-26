# Guía de Materiales y Parámetros para Elegoo Centauri Carbon

La Elegoo Centauri Carbon cuenta con un hotend de 300°C con boquilla de acero templado, cama caliente hasta 110°C y cabina cerrada.

---

## Comparativa Técnica de Materiales

| Material | Temp Boquilla | Temp Cama | Cámara | Ventilación | Resistencia Térmica (HDT) | Uso Principal |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PLA / PLA+** | 205 - 225 °C | 55 - 65 °C | **Abierta / Puerta entreabierta** | 100% | ~55 °C | Prototipos, maquetas, soportes interiores, juguetes. |
| **PETG** | 235 - 250 °C | 70 - 80 °C | Abierta o Cerrada | 30 - 50% | ~70 °C | Resistencia al agua, químicos, ganchos funcionales, exteriores moderados. |
| **ABS** | 245 - 265 °C | 95 - 105 °C | **Cerrada (Precalentar 15 min)** | 0 - 15% | ~90 °C | Piezas mecánicas, automoción interior, carcasas electrónicas. |
| **ASA** | 250 - 265 °C | 95 - 105 °C | **Cerrada (Precalentar 15 min)** | 0 - 20% | ~95 °C | Piezas expuestas al sol continuo, intemperie severa, jardinería, náutica. |
| **TPU (95A)** | 220 - 240 °C | 40 - 50 °C | Abierta | 50 - 80% | ~60 °C | Protectores antigolpes, neumáticos, juntas de estanqueidad, suelas. |
| **PA-CF (Nylon+CF)** | 275 - 295 °C | 80 - 100 °C | **Cerrada (Secar filamento antes)** | 0 - 20% | 140 - 170 °C | Ingeniería de alto esfuerzo, componentes automotrices, drones, herramentales. |

---

## ⚠️ Advertencias Específicas para la Elegoo Centauri Carbon

1. **PLA y calor en cabina (Heat Creep):**
   - Cuando imprimas PLA en la Centauri Carbon, **mantén la puerta de cristal ligeramente entreabierta o quita la tapa superior**, especialmente en impresiones de varias horas. El cerramiento retiene tanto calor que puede ablandar el PLA antes de entrar al bloque térmico, provocando atascos en el extrusor.
2. **Boquilla de Acero Endurecido:**
   - La boquilla de acero templado tiene una conductividad térmica ligeramente inferior al latón. Como regla general, imprime a unos **5°C más** de lo que usarías en boquillas de latón convencionales.
   - Es resistente al desgaste abrasivo de filamentos con fibra de carbono (PA-CF, PETG-CF) y partículas que destruirían una boquilla de latón en pocas horas.
3. **Impresión de ABS/ASA sin Warping:**
   - Enciende la cama a 100°C con la cabina cerrada durante 15 minutos antes de imprimir para calentar el aire interior a unos 40-50°C.
   - Aplica una capa fina de adhesivo (pegamento en barra o laca 3D) en la placa PEI para evitar que las esquinas se despeguen.
