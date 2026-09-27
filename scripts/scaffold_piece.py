#!/usr/bin/env python3
"""
scaffold_piece.py — Generador de estructura para una nueva pieza con sus artefactos.
Crea el directorio 'pieces/<nombre_pieza>/' con su código CAD inicial, ficha técnica y carpeta de renders.
"""

import sys
import os
import argparse
import re

def sanitize_name(name):
    # Convertir a minúsculas y reemplazar espacios o caracteres inválidos por guiones bajos
    clean = re.sub(r'[^a-zA-Z0-9_\-]', '_', name.lower().strip())
    clean = re.sub(r'_+', '_', clean)
    return clean.strip('_')

def scaffold_piece(piece_name, template="starter", material="PLA", description="", target_device=""):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    clean_name = sanitize_name(piece_name)
    piece_dir = os.path.join(root_dir, "pieces", clean_name)
    renders_dir = os.path.join(piece_dir, "renders")

    if os.path.exists(piece_dir):
        print(f"⚠️ El directorio para la pieza '{clean_name}' ya existe en: {piece_dir}")
        return piece_dir

    os.makedirs(renders_dir, exist_ok=True)
    with open(os.path.join(renders_dir, ".gitkeep"), "w") as f:
        f.write("")

    # 1. Crear el archivo CAD paramétrico inicial
    scad_path = os.path.join(piece_dir, f"{clean_name}.scad")
    device_line = f"// Dispositivo Receptor: {target_device}\n" if target_device else ""
    scad_content = f"""// =====================================================================
// Pieza: {clean_name}
{device_line}// Material previsto: {material}
// Máquina: Elegoo Centauri Carbon (CoreXY, 256x256x256 mm)
// =====================================================================

include <BOSL2/std.scad>
include <BOSL2/screws.scad>

// --- RESOLUCIÓN DINÁMICA ---
$preview_fn = 32;
$export_fn = 96;
$fn = $preview ? $preview_fn : $export_fn;
$slop = 0.2; // Tolerancia de holgura diametral FDM

// --- PARÁMETROS PRINCIPALES (mm) ---
ANCHO  = 50.0;
LARGO  = 40.0;
ALTURA = 15.0;
GROSOR_PARED = 2.4; // 6 perímetros con boquilla 0.4 mm

// --- SELECTOR RENDER ("preview", "cuerpo", "tapa") ---
RENDER = "preview";

module cuerpo() {{
    diff()
    cuboid([ANCHO, LARGO, ALTURA], rounding=2, edges="Z", anchor=BOTTOM) {{
        // Cavidad interior (shiftout=0.01 mandatorio para corte limpio)
        attach(TOP, TOP, inside=true, shiftout=0.01)
            cuboid([ANCHO - GROSOR_PARED*2, LARGO - GROSOR_PARED*2, ALTURA - GROSOR_PARED], 
                   rounding=1, edges="Z");
                   
        // Barrenos de montaje M3 en las esquinas
        attach(TOP, TOP, inside=true, shiftout=0.01)
            grid_copies(spacing=[ANCHO - 10, LARGO - 10])
                screw_hole("M3,12", head="socket", counterbore=true, anchor=TOP);
    }}
}}

// --- CONTROL DE RENDERIZADO ---
if (RENDER == "preview" || RENDER == "cuerpo") {{
    cuerpo();
}}
"""
    with open(scad_path, "w", encoding="utf-8") as f:
        f.write(scad_content)

    # 2. Crear ficha técnica README.md
    readme_path = os.path.join(piece_dir, "README.md")
    verify_cmd = f"python3 scripts/verify_mesh.py pieces/{clean_name}/{clean_name}.stl --manifest --material {material}"
    if target_device:
        verify_cmd += f' --target-device "{target_device}"'

    readme_content = f"""# Pieza: {clean_name}

{description if description else "Pieza diseñada para fabricación aditiva FDM en Elegoo Centauri Carbon."}

---

## 🎯 Especificaciones de Diseño
- **Material recomendado:** `{material}`
- **Volumen de impresión:** Elegoo Centauri Carbon (256 × 256 × 256 mm)
- **Boquilla recomendada:** 0.4 mm acero endurecido
- **Holgura de ajuste ($slop):** `0.2 mm`
- **Espesor de pared base:** Múltiplo de 0.4 mm (e.g. 2.0 mm / 2.4 mm)

---

## 📋 Registro de Requerimientos y Decisiones (Design Rationale)
<!-- Acordado durante la entrevista de requerimientos (skills/3d-grill-me) -->
- **Dispositivo Receptor (Target Hardware):** {target_device if target_device else "N/A (Greenfield / Genérico)"}
- **Estrategia:** {"Greenfield (Desde cero)" if template == "starter" else "Remix & Adaptación"}
- **Pieza base / muestra:** {"Ninguna" if template == "starter" else "Pieza STL/STEP previa"}
- **Rasgos a conservar:** {"N/A" if template == "starter" else "Interfaces de acople, patrón de tornillos"}
- **Modificaciones:** {"Diseño funcional inicial" if template == "starter" else "Refuerzos, nueva montura"}
- **Problema previo / Antecedente:** {"N/A" if template == "starter" else "Describir si la pieza previa se rompió o falló y por qué"}
- **Orientación de capas y esfuerzos:** {"Carga en plano XY / Capas orientadas para máxima resistencia mecánica"}
- **Método de fijación:** {"Tornillos M3 con insertos térmicos / agujeros pasantes"}

---

## 🔬 Ficha Técnica del Hardware Receptor (Target Hardware Dossier)
<!-- Documentar cotas oficiales durante spec-advisor (datasheets, manuales de servicio o calibre) -->
| Parámetro | Especificación de Fabricante / Datasheet | Implicación en Diseño CAD y Laminado FDM |
| :--- | :--- | :--- |
| **Componente Receptor** | {target_device if target_device else "Definir componente comercial / máquina"} | Contexto de aplicación y montaje |
| **Número de Parte Exacto** | {target_device if target_device else "N/A"} | No truncar; referencia unívoca |
| **Interfaz Mecánica / Eje** | Pendiente (e.g. Diámetro eje, chaveta, rosca) | Cota nominal y holguras en CAD |
| **Carga / Torque Operativo** | Pendiente (e.g. Par nominal, esfuerzo cortante) | Espesor de paredes y bucles de perímetro |
| **Rango de Temperatura** | Pendiente (e.g. -20°C a +70°C) | Criterio de selección de material (Tg) |
| **Fuente / Datasheet** | [Añadir URL o archivo técnico en references/] | Trazabilidad documental auditable |

---

## 📦 Artefactos de la Pieza

| Artefacto | Descripción | Estado |
| :--- | :--- | :--- |
| [`{clean_name}.scad`](./{clean_name}.scad) | Código CAD paramétrico editable (OpenSCAD + BOSL2) | ✅ Creado |
| [`{clean_name}.stl`](./{clean_name}.stl) | Malla exportada hermética (Z=0, Z-up) | ⏳ Pendiente de compilar |
| [`{clean_name}.3mf`](./{clean_name}.3mf) | Proyecto OrcaSlicer con perfiles y placa nombrada | ⏳ Pendiente de empaquetar |
| [`manifest.json`](./manifest.json) | Certificado de calidad y auditoría (Printability Gate) | ⏳ Pendiente de verificar |
| [`viewer.html`](./viewer.html) | Visor 3D interactivo en navegador | ⏳ Pendiente de generar |
| [`renders/`](./renders/) | Capturas multiángulo PNG (isométrica, planta, frontal) | ⏳ Pendiente de capturar |
| [`print_feedback.md`](./print_feedback.md) | Control de calidad, feedback post-impresión y prescripción clínica (Print Doctor) | ⏳ Pendiente de imprimir |

---

## 🛠️ Comandos de Pipeline para esta Pieza

```bash
# 1. Compilar STL desde OpenSCAD
openscad -D 'RENDER="cuerpo"' -o pieces/{clean_name}/{clean_name}.stl pieces/{clean_name}/{clean_name}.scad

# 2. Auditar imprimibilidad y generar manifest.json
{verify_cmd}

# 3. Generar visor Three.js y vistas previas PNG
python3 scripts/generate_gallery.py pieces/{clean_name}/{clean_name}.scad

# 4. Empaquetar a 3MF para OrcaSlicer / ElegooSlicer
python3 scripts/export_3mf.py pieces/{clean_name}/{clean_name}.stl -o pieces/{clean_name}/{clean_name}.3mf --intent mechanical --material {material}

# 5. Registrar feedback post-impresión o consultar a Print Doctor si requiere ajuste
python3 scripts/feedback.py pieces/{clean_name} --status PASS --notes "Impresión y ajuste validados"
```
"""
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    # 3. Crear archivo de feedback post-impresión inicial (print_feedback.md)
    feedback_path = os.path.join(piece_dir, "print_feedback.md")
    feedback_content = f"""# Control de Calidad y Feedback Post-Impresión: {clean_name}

**Pieza:** [`{clean_name}`](./README.md)  
{f"**Hardware Objetivo:** `{target_device}`\\n" if target_device else ""}**Estado de Validación:** ⏳ PENDIENTE_DE_IMPRESION  
**Última Actualización:** {time.strftime('%Y-%m-%d %H:%M')}  

---

## 📋 Registro de la Impresión Real

| Parámetro | Valor Real en Máquina | Comentario / Observación |
| :--- | :--- | :--- |
| **Fecha / Hora de Impresión** | Pendiente | Registrar fecha de retiro de la cama |
| **Impresora 3D** | Elegoo Centauri Carbon | Placa texturizada PEI |
| **Material y Marca** | `{material}` (Pendiente especificar bobina) | Registrar marca y horas de secado previo |
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

<!-- Si la pieza presentó desviaciones, el agente o el usuario documentarán aquí el diagnóstico y la prescripción -->
- **Estado Clínico:** No se han reportado defectos mecánicos o dimensionales.
- **Acciones Realizadas:** Pendiente de inspección física tras impresión en máquina.

---

## 🏁 Veredicto Final

- [ ] **APROBADO (PASS):** La pieza cumple 100% su propósito funcional y tolerancias.
- [ ] **REQUIERE AJUSTES (ADJUST):** Se requiere corregir CAD o perfil de corte antes de uso definitivo.
- [ ] **FALLO TOTAL (FAIL):** Pieza inutilizable; requiere diagnóstico de causa raíz y reimpresión.
"""
    with open(feedback_path, "w", encoding="utf-8") as f:
        f.write(feedback_content)

    print(f"✨ Estructura de pieza creada exitosamente en: pieces/{clean_name}/")
    print(f"  ├── {clean_name}.scad (Modelo paramétrico)")
    print(f"  ├── README.md (Ficha técnica y lista de artefactos)")
    print(f"  ├── print_feedback.md (Ficha de inspección y feedback Print Doctor)")
    print(f"  └── renders/ (Directorio de vistas previas)")

    return piece_dir

def main():
    parser = argparse.ArgumentParser(description="Scaffold de nueva pieza con sus artefactos para 3D Printing Specialist")
    parser.add_argument("name", help="Nombre descriptivo de la pieza (ej. soporte_sensor_btt, clip_cable_2020)")
    parser.add_argument("--material", default="PLA", choices=["PLA", "PETG", "ABS", "ASA", "TPU", "PA-CF"], help="Material objetivo")
    parser.add_argument("--desc", default="", help="Breve descripción del propósito de la pieza")
    parser.add_argument("--target-device", default="", help="Nombre y modelo exacto del dispositivo o máquina receptora (ej. 'Honeywell Slate R8001M1150')")
    parser.add_argument("--template", default="starter", choices=["starter", "remix"], help="Plantilla base CAD")

    args = parser.parse_args()
    scaffold_piece(args.name, template=args.template, material=args.material, description=args.desc, target_device=args.target_device)

if __name__ == "__main__":
    main()
