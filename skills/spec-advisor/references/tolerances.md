# Tolerancias Dimensionales y Holguras en Impresión FDM

La física de la deposición de filamento fundido (FDM) provoca que los plásticos se expandan ligeramente al salir de la boquilla (die swell) y luego se contraigan al enfriarse. Además, el movimiento circular del cabezal tiende a cerrar los orificios internos.

---

## 1. Regla de Contracción de Orificios Internos
En piezas FDM, **los orificios cilíndricos interiores siempre quedan entre 0.1 mm y 0.2 mm más pequeños que en el modelo CAD** si no se aplica compensación XY o se diseña la holgura en el modelo:
- Si necesitas alojar un eje o pasador de **5.0 mm**, diseña el orificio en **5.2 mm** para giro suave o **5.1 mm** para ajuste a presión.

---

## 2. Clasificación de Ajustes (Fits)

Para una boquilla estándar de 0.4 mm y altura de capa de 0.2 mm en la Elegoo Centauri Carbon:

### A. Ajuste a Presión Fijo (Press Fit / Interference Fit)
- **Holgura total:** `+0.08 mm` a `+0.12 mm`.
- **Sensación:** Requiere empuje firme con los dedos o golpecito suave con maza de nylon. No se sale por gravedad ni vibración.
- **Ejemplos:** Imanes de neodimio, pasadores guía, topes fijos.

### B. Ajuste Firme Desmontable (Snug / Friction Fit)
- **Holgura total:** `+0.15 mm` a `+0.20 mm`.
- **Sensación:** Entra suavemente con resistencia friccional controlada. Se puede retirar con la mano haciendo palanca.
- **Ejemplos:** Tapas de cajas a presión, acoples modulares, protectores de lente.

### C. Ajuste Deslizante Libre (Sliding / Running Fit)
- **Holgura total:** `+0.25 mm` a `+0.35 mm`.
- **Sensación:** Movimiento libre sin fricción apreciable y sin bamboleo (backlash) excesivo.
- **Ejemplos:** Ejes giratorios, rieles de deslizamiento, bisagras impresas en una sola pieza (print-in-place).

### D. Ajuste Holgado (Clearance Fit)
- **Holgura total:** `+0.40 mm` a `+0.50 mm`.
- **Sensación:** Holgura generosa.
- **Ejemplos:** Agujeros para paso de tornillos, canales de cables, orificios de ventilación.

---

## 3. Variación por Material

| Material | Contracción Térmica (Shrinkage) | Tendencia en Orificios |
| :--- | :--- | :--- |
| **PLA / PLA+** | Muy baja (<0.3%) | Dimensiones muy fieles al CAD. |
| **PETG** | Baja (0.3% - 0.5%) | Puede hilvanar (stringing) en orificios pequeños; añadir +0.05 mm extra. |
| **ABS / ASA** | Alta (0.8% - 1.2%) | Requiere compensación por contracción o escala de 100.5% - 100.8% en slicer. |
| **TPU** | N/A (Elástico) | Requiere restar holgura (-0.1 a -0.2 mm) si se busca ajuste hermético. |
| **PA-CF** | Muy baja (0.2% - 0.4%) | Las fibras de carbono reducen drásticamente la contracción; excelente precisión dimensional. |
