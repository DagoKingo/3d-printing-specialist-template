#!/usr/bin/env python3
"""
feedback.py — Registro de Feedback Post-Impresión, Inspección de Calidad (QA) y Enlace con Print Doctor.
Permite registrar cómo resultó la pieza física y aplicar recomendaciones clínicas de 'skills/print-doctor'.
"""

import sys
import os
import argparse
import time
import re

# Prescripciones clínicas de print-doctor para fallos frecuentes
PRESCRIPTIONS = {
    "tight_fit": {
        "title": "Ajuste demasiado apretado en eje / rodamiento / tornillo",
        "root_cause": "Contracción térmica del filamento hacia el interior de orificios cerrados (shrinkage) o tolerancia $slop insuficiente.",
        "cad_action": "Incrementar tolerancia paramétrica $slop en +0.10 mm (ej. de 0.20 a 0.30 mm).",
        "slicer_action": "Aumentar 'xy_hole_compensation' en +0.10 mm en el perfil de corte (ej. de +0.15 mm a +0.25 mm).",
        "hardware_action": "Verificar con calibre si el eje físico excede su cota nominal."
    },
    "loose_fit": {
        "title": "Ajuste demasiado holgado (baila o no retiene)",
        "root_cause": "Tolerancia $slop sobredimensionada o sobrecompensación en slicer.",
        "cad_action": "Reducir tolerancia paramétrica $slop en -0.10 mm.",
        "slicer_action": "Reducir 'xy_hole_compensation' en -0.10 mm (o fijar en 0.00 mm).",
        "hardware_action": "Verificar apriete o considerar inserción de tornillo prisionero / set-screw."
    },
    "stringing": {
        "title": "Hilos, telarañas o pelusas (Stringing / Oozing)",
        "root_cause": "Filamento húmedo, temperatura excesiva de boquilla o distancia de retracción insuficiente para Direct Drive.",
        "cad_action": "Evitar espacios vacíos que fuercen saltos de desplazamiento continuo si es viable.",
        "slicer_action": "Reducir temperatura de boquilla en -5°C; verificar retracción de 0.8 mm a 40 mm/s y activar 'Wipe while retracting' (2 mm).",
        "hardware_action": "Secar el filamento en secador durante 4-6h (PETG a 65°C, PLA a 45°C)."
    },
    "warping": {
        "title": "Esquinas levantadas o despegadas de la cama (Warping)",
        "root_cause": "Gradiente térmico brusco por enfriamiento prematuro o superficie PEI con grasa.",
        "cad_action": "Diseñar chaflanes redondeados en esquinas inferiores para disipar tensión térmica.",
        "slicer_action": "Añadir ala exterior (Brim) de 6-8 mm; reducir ventilador de capa en primeras 5 capas; aumentar temp cama +5°C.",
        "hardware_action": "Limpiar placa PEI con agua tibia y jabón neutro; precalentar cámara 15 min antes de imprimir (en ABS/ASA)."
    },
    "heat_creep": {
        "title": "Atasco por calor en el disipador (Heat Creep / Clic en extrusor)",
        "root_cause": "Cabina cerrada reteniendo calor en filamentos de bajo punto de fusión (PLA a >40°C de aire interior).",
        "cad_action": "N/A (Fallo térmico de entorno).",
        "slicer_action": "Aumentar retracción máxima si supera 1.2 mm (evitar jalar plástico caliente a zona fría).",
        "hardware_action": "Abrir puerta de cristal o retirar tapa superior de la Centauri Carbon al imprimir PLA."
    },
    "layer_shift": {
        "title": "Salto o escalón de capas (Layer Shift)",
        "root_cause": "Colisión de boquilla con relleno o correas CoreXY destensadas a aceleraciones extremas.",
        "cad_action": "Evitar aristas que se curven hacia arriba por enfriamiento local.",
        "slicer_action": "Cambiar patrón de relleno de Grid a Gyroid (evita cruces en el mismo plano Z); reducir aceleración a 10,000 mm/s².",
        "hardware_action": "Verificar tensión de correas X/Y (~110-130 Hz) y lubricar guías lineales."
    },
    "delamination": {
        "title": "Separación o delaminación entre capas",
        "root_cause": "Fusión interlaminar deficiente por exceso de ventilación o baja temperatura de extrusión.",
        "cad_action": "Orientar la pieza para que los esfuerzos mecánicos no trabajen a tracción perpendicular a Z.",
        "slicer_action": "Subir temperatura de boquilla +5°C a +10°C; reducir ventilador de capa al 20%-30% (en PETG) o 0% (en ABS/ASA).",
        "hardware_action": "Cerrar cabina para evitar corrientes de aire frío."
    },
    "elephant_foot": {
        "title": "Pie de elefante (ensanchamiento en primeras capas)",
        "root_cause": "Cama caliente excesiva o altura de primera capa muy aplastada contra la placa.",
        "cad_action": "Aplicar chaflán de 45° de 0.5 a 1.0 mm en la arista inferior de apoyo.",
        "slicer_action": "Activar compensación de pie de elefante (Elephant foot compensation = 0.15 mm).",
        "hardware_action": "Recalibrar nivelación automática de cama en la pantalla de la Centauri."
    },
    "other": {
        "title": "Desviación personalizada o defecto no catalogado",
        "root_cause": "Revisar variables mecánicas, cinemáticas y térmicas del entorno.",
        "cad_action": "Ajustar geometría según medición manual de calibre.",
        "slicer_action": "Ajustar parámetros según recomendación de skills/slicer-advisor.",
        "hardware_action": "Mantenimiento general y calibración de máquina."
    }
}

def resolve_piece_dir(path_or_name):
    # Buscar si se pasó un path directo o solo el nombre de la pieza
    if os.path.isdir(path_or_name):
        return os.path.abspath(path_or_name)
    
    # Buscar en carpeta pieces/
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidate = os.path.join(root_dir, "pieces", path_or_name)
    if os.path.isdir(candidate):
        return candidate
    
    # Si termina en pieces/<algo>
    candidate_alt = os.path.join(os.getcwd(), path_or_name)
    if os.path.isdir(candidate_alt):
        return os.path.abspath(candidate_alt)
        
    return None

def generate_initial_feedback_content(piece_name, target_device=""):
    date_str = time.strftime("%Y-%m-%d %H:%M")
    device_text = f"**Hardware Objetivo:** `{target_device}`\n" if target_device else ""
    return f"""# Control de Calidad y Feedback Post-Impresión: {piece_name}

**Pieza:** [`{piece_name}`](./README.md)  
{device_text}**Estado de Validación:** ⏳ PENDIENTE_DE_IMPRESION  
**Última Actualización:** {date_str}  

---

## 📋 Registro de la Impresión Real

| Parámetro | Valor Real en Máquina | Comentario / Observación |
| :--- | :--- | :--- |
| **Fecha / Hora de Impresión** | Pendiente | Registrar fecha de retiro de la cama |
| **Impresora 3D** | Elegoo Centauri Carbon | Placa texturizada PEI |
| **Material y Marca** | Pendiente (e.g. PETG Negro) | Registrar bobina y horas de secado previo |
| **Tiempo Real de Impresión** | Pendiente | Comparar contra estimado de slicer |
| **Masa Real en Báscula** | Pendiente (g) | Comparar contra estimado en manifest.json |
| **Boquilla / Altura de Capa** | 0.4 mm / 0.20 mm | Acero endurecido |

---

## 🔍 Checklist de Inspección Física (First Article Inspection)

### 1. Adherencia y Base (Z=0)
- [ ] Base plana sin alabeo ni desprendimiento en esquinas (sin warping).
- [ ] Libre de pie de elefante excesivo (chaflán de 45° efectivo).

### 2. Calidad Superficial y Estética
- [ ] Paredes perimetrales lisas y homogéneas sin subextrusión ni costuras prominentes.
- [ ] Cara superior uniforme (sin cicatrices de boquilla ni infill traslúcido).
- [ ] Ausencia de hilos finos o telarañas (stringing controlado).

### 3. Soportes y Voladizos
- [ ] Desprendimiento de soportes limpio y sin cicatrices en caras cosméticas (Zona A).
- [ ] Voladizos a 45°-50° autoportantes sin descolgamiento de filamento.

### 4. Ajuste Mecánico y Funcional (Fit Check)
- [ ] Barrenos y alojamientos con la tolerancia nominal prevista ($slop).
- [ ] Acople firme con el hardware receptor (sin juego holgado y sin requerir fuerza bruta destructiva).
- [ ] Resistencia a la tracción y flexión adecuada a la orientación de capas.

---

## 🩺 Consulta Clínica Print Doctor (`skills/print-doctor`)

<!-- Si la pieza presentó desviaciones, documentar aquí el diagnóstico y prescripción -->
- **Estado Clínico:** No se han reportado defectos mecánicos o dimensionales.
- **Acciones Realizadas:** Pendiente de inspección física.

---

## 🏁 Veredicto Final

- [ ] **APROBADO (PASS):** La pieza cumple 100% su propósito funcional y tolerancias.
- [ ] **REQUIERE AJUSTES (ADJUST):** Se requiere corregir CAD o perfil de corte antes de uso definitivo.
- [ ] **FALLO TOTAL (FAIL):** Pieza inutilizable; requiere diagnóstico de causa raíz y reimpresión.
"""

def get_artifacts_dir(piece_dir):
    for candidate in ["artifacts", "artefacts"]:
        c_dir = os.path.join(piece_dir, candidate)
        if os.path.isdir(c_dir):
            return c_dir
    return piece_dir

def update_feedback_report(piece_dir, status, symptom=None, notes="", material="", weight="", print_time=""):
    target_dir = get_artifacts_dir(piece_dir)
    feedback_path = os.path.join(target_dir, "print_feedback.md")
    piece_name = os.path.basename(piece_dir)
    
    # Si no existe, crear el esqueleto base
    target_device = ""
    manifest_path = os.path.join(target_dir, "manifest.json")
    if os.path.exists(manifest_path):
        try:
            import json
            with open(manifest_path, "r", encoding="utf-8") as f:
                mdata = json.load(f)
                target_device = mdata.get("target_device", "")
        except Exception:
            pass

    if not os.path.exists(feedback_path):
        initial_content = generate_initial_feedback_content(piece_name, target_device=target_device)
        with open(feedback_path, "w", encoding="utf-8") as f:
            f.write(initial_content)

    with open(feedback_path, "r", encoding="utf-8") as f:
        content = f.read()

    date_str = time.strftime("%Y-%m-%d %H:%M")

    # Mapeo de status a badge
    status_map = {
        "PASS": "🟢 APROBADO (PASS)",
        "ADJUST": "🟡 REQUIERE AJUSTES (ADJUST)",
        "FAIL": "🔴 FALLO / REIMPRESION (FAIL)"
    }
    status_badge = status_map.get(status.upper(), f"⚪ {status.upper()}")

    # Actualizar cabecera de estado
    content = re.sub(
        r"\*\*Estado de Validación:\*\*.*",
        f"**Estado de Validación:** {status_badge}",
        content
    )
    content = re.sub(
        r"\*\*Última Actualización:\*\*.*",
        f"**Última Actualización:** {date_str}",
        content
    )

    # Actualizar tabla de impresión real si se proporcionaron datos
    if material:
        content = re.sub(r"(\|\s*\*\*Material y Marca\*\*\s*\|\s*).*?(\s*\|)", rf"\g<1>{material}\g<2>", content)
    if print_time:
        content = re.sub(r"(\|\s*\*\*Tiempo Real de Impresión\*\*\s*\|\s*).*?(\s*\|)", rf"\g<1>{print_time}\g<2>", content)
    if weight:
        content = re.sub(r"(\|\s*\*\*Masa Real en Báscula\*\*\s*\|\s*).*?(\s*\|)", rf"\g<1>{weight} g\g<2>", content)
    content = re.sub(r"(\|\s*\*\*Fecha / Hora de Impresión\*\*\s*\|\s*).*?(\s*\|)", rf"\g<1>{date_str}\g<2>", content)

    # Actualizar sección clínica de Print Doctor si hay síntoma
    if symptom and symptom.lower() in PRESCRIPTIONS:
        rx = PRESCRIPTIONS[symptom.lower()]
        rx_section = f"""## 🩺 Consulta Clínica Print Doctor (`skills/print-doctor`)

### 1. Cuadro Clínico y Síntoma Reportado
- **Defecto Observado:** **{rx['title']}**
- **Observaciones del Usuario:** {notes if notes else 'Sin comentarios adicionales.'}
- **Fecha de Consulta:** {date_str}

### 2. Diagnóstico de Causa Raíz
{rx['root_cause']}

### 3. Prescripción y Tratamiento Aplicable
- **🛠️ Ajuste en Código CAD (.scad):** {rx['cad_action']}
- **⚙️ Ajuste en Laminador (.3mf / OrcaSlicer):** {rx['slicer_action']}
- **🔧 Ajuste en Hardware / Material:** {rx['hardware_action']}

### 4. Próximos Pasos Recomendados
1. Aplicar las correcciones prescritas en el código paramétrico `.scad` o en el perfil de corte `.3mf`.
2. Si hubo cambio geométrico, re-ejecutar `verify_mesh.py` y actualizar el manifest.
3. Reimprimir y volver a ejecutar la inspección de control de calidad.
"""
        # Reemplazar la sección de Print Doctor
        pattern = r"## 🩺 Consulta Clínica Print Doctor.*?(?=## 🏁 Veredicto Final|\Z)"
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, rx_section + "\n", content, flags=re.DOTALL)
        else:
            content += "\n" + rx_section

    elif notes:
        # Añadir nota al cuadro clínico si no hubo síntoma específico
        notes_block = f"\n- **Observación registrada ({date_str}):** {notes}\n"
        content = content.replace("## 🩺 Consulta Clínica Print Doctor (`skills/print-doctor`)",
                                  f"## 🩺 Consulta Clínica Print Doctor (`skills/print-doctor`)\n{notes_block}")

    # Actualizar veredicto final en los checkboxes
    content = re.sub(r"- \[[ xX]\] \*\*APROBADO \(PASS\):\*\*", f"- [{'x' if status.upper() == 'PASS' else ' '}] **APROBADO (PASS):**", content)
    content = re.sub(r"- \[[ xX]\] \*\*REQUIERE AJUSTES \(ADJUST\):\*\*", f"- [{'x' if status.upper() == 'ADJUST' else ' '}] **REQUIERE AJUSTES (ADJUST):**", content)
    content = re.sub(r"- \[[ xX]\] \*\*FALLO TOTAL \(FAIL\):\*\*", f"- [{'x' if status.upper() == 'FAIL' else ' '}] **FALLO TOTAL (FAIL):**", content)

    with open(feedback_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"📝 Reporte de feedback actualizado exitosamente en: {feedback_path}")
    print(f"• Estado: {status_badge}")
    if symptom and symptom.lower() in PRESCRIPTIONS:
        rx = PRESCRIPTIONS[symptom.lower()]
        print(f"• Diagnóstico Print Doctor: {rx['title']}")
        print(f"  - CAD:     {rx['cad_action']}")
        print(f"  - Slicer:  {rx['slicer_action']}")
        print(f"  - Máquina: {rx['hardware_action']}")

    return feedback_path

def main():
    parser = argparse.ArgumentParser(description="Registro de Feedback Post-Impresión y Triage Clínico con Print Doctor")
    parser.add_argument("piece", help="Ruta o nombre del directorio de la pieza (ej. pieces/aguja_slate_r8001m)")
    parser.add_argument("--status", choices=["PASS", "ADJUST", "FAIL"], default="PASS", help="Resultado de la inspección física")
    parser.add_argument("--symptom", choices=list(PRESCRIPTIONS.keys()), default=None, help="Síntoma o defecto visual/mecánico detectado")
    parser.add_argument("--notes", default="", help="Observaciones del usuario sobre el acabado o ajuste")
    parser.add_argument("--material", default="", help="Material y marca real empleada (ej. 'PETG Elegoo Rapid Negro')")
    parser.add_argument("--weight", default="", help="Masa real pesada en báscula en gramos")
    parser.add_argument("--time", default="", help="Tiempo real de impresión")
    parser.add_argument("--init-only", action="store_true", help="Solo inicializar el archivo print_feedback.md si no existe")

    args = parser.parse_args()

    piece_dir = resolve_piece_dir(args.piece)
    if not piece_dir:
        print(f"❌ Error: No se encontró la carpeta de la pieza '{args.piece}'.")
        sys.exit(1)

    if args.init_only:
        target_dir = get_artifacts_dir(piece_dir)
        feedback_path = os.path.join(target_dir, "print_feedback.md")
        if not os.path.exists(feedback_path):
            piece_name = os.path.basename(piece_dir)
            content = generate_initial_feedback_content(piece_name)
            with open(feedback_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✨ Artefacto print_feedback.md creado en: {feedback_path}")
        else:
            print(f"ℹ️ El archivo print_feedback.md ya existe en: {feedback_path}")
        sys.exit(0)

    update_feedback_report(
        piece_dir,
        status=args.status,
        symptom=args.symptom,
        notes=args.notes,
        material=args.material,
        weight=args.weight,
        print_time=args.time
    )

if __name__ == "__main__":
    main()
