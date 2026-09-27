#!/usr/bin/env python3
"""
scaffold_draft.py — Generador de estructura para iteraciones y prototipos (drafts) de piezas.
Crea el directorio 'pieces/<nombre_pieza>/prototypes/draft-[N]/' con su artefacto EVALUATION.md y carpeta evidence/.
"""

import sys
import os
import argparse
import time
import re

def resolve_piece_dir(path_or_name):
    # Buscar si se pasó un path directo o solo el nombre de la pieza
    if os.path.isdir(path_or_name):
        return os.path.abspath(path_or_name)
    
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidate = os.path.join(root_dir, "pieces", path_or_name)
    if os.path.isdir(candidate):
        return candidate
    
    candidate_alt = os.path.join(os.getcwd(), path_or_name)
    if os.path.isdir(candidate_alt):
        return os.path.abspath(candidate_alt)
        
    return None

def scaffold_draft(piece_input, draft_number, goal="", target_device=""):
    piece_dir = resolve_piece_dir(piece_input)
    if not piece_dir:
        print(f"❌ Error: No se encontró el directorio de pieza para: {piece_input}")
        sys.exit(1)

    piece_name = os.path.basename(piece_dir)
    # Extraer número si se pasa "draft-1" o "1"
    clean_draft_num = str(draft_number).lower().replace("draft-", "").replace("draft", "").strip()
    draft_dir_name = f"draft-{clean_draft_num}"
    
    prototypes_dir = os.path.join(piece_dir, "prototypes")
    draft_dir = os.path.join(prototypes_dir, draft_dir_name)
    evidence_dir = os.path.join(draft_dir, "evidence")

    os.makedirs(evidence_dir, exist_ok=True)
    gitkeep_path = os.path.join(evidence_dir, ".gitkeep")
    if not os.path.exists(gitkeep_path):
        with open(gitkeep_path, "w") as f:
            f.write("")

    evaluation_path = os.path.join(draft_dir, "EVALUATION.md")
    if not os.path.exists(evaluation_path):
        now_str = time.strftime("%Y-%m-%d %H:%M")
        eval_content = f"""# Evaluación Técnica de Prototipo: Draft {clean_draft_num}

**Pieza:** [`{piece_name}`](../../README.md)  
**Iteración:** `draft-{clean_draft_num}`  
**Fecha:** {now_str}  
**Hardware Receptor:** `{target_device if target_device else "N/A"}`  
**Estado:** ⏳ EN_EVALUACION <!-- PASS | FAIL | ADJUST | EN_EVALUACION -->

---

## 🎯 Objetivo e Hipótesis de la Iteración
<!-- ¿Qué hipótesis de diseño o laminación se puso a prueba en este draft? -->
{goal if goal else "- Validar ajuste mecánico, integridad geométrica y calidad superficial del prototipo."}

---

## ⚙️ Parámetros de Fabricación y Slicer
| Parámetro | Configuración de este Draft |
| :--- | :--- |
| **Material Cuerpos** | e.g. ABS / PETG |
| **Material Soportes / Interfaz** | e.g. Mismo material / PETG zero-gap |
| **Boquilla / Altura de Capa** | 0.40 mm / 0.20 mm |
| **Estrategia de Soportes** | e.g. Snug / Tree / Zero-gap Canvas |
| **Compensación XY de Agujeros** | `0.00 mm` (o especificar si difiere) |
| **Holgura Paramétrica ($slop)** | e.g. 0.15 mm |

---

## ✅ En qué acertó (Successes)
<!-- Describir qué cotas, funciones o acabados cumplieron satisfactoriamente los requisitos -->
- 

---

## ❌ En qué falló (Failures & Deviations)
<!-- Describir qué defectos dimensionales, mecánicos o superficiales se manifestaron -->
- 

---

## 🔬 Diagnóstico y Causa Raíz Física (Root Cause Analysis)
<!-- Análisis físico de la causa del fallo: térmico, cinemático, contracción, adhesión o brecha Z -->
- 

---

## 📋 Acciones Prescritas para el Siguiente Draft (Next Actions)
<!-- Cambios concretos a implementar en CAD (.scad), Slicer (.3mf) o preparación de máquina -->
- 

---

## 📸 Evidencia Fotográfica y Registros
<!-- Colocar imágenes de la pieza impresa en evidence/ y documentar el análisis visual -->
<!-- Ejemplo: ![Inspección de voladizo](evidence/foto1.jpg) -->
- *Pendiente de adjuntar evidencia fotográfica en [`evidence/`](./evidence/).*
"""
        with open(evaluation_path, "w", encoding="utf-8") as f:
            f.write(eval_content)

    print(f"✨ Estructura de draft creada exitosamente en:")
    print(f"  {draft_dir}/")
    print(f"  ├── EVALUATION.md (Artefacto de evaluación formal)")
    print(f"  ├── evidence/ (Directorio de evidencia fotográfica)")
    print(f"  └── (.3mf / .stl de esta iteración)")

    return draft_dir

def main():
    parser = argparse.ArgumentParser(description="Scaffold de nuevo draft/prototipo para una pieza 3D")
    parser.add_argument("piece", help="Nombre o ruta de la pieza (ej. aguja_slate_r8001m o pieces/aguja_slate_r8001m)")
    parser.add_argument("draft", help="Número o nombre del draft (ej. 1, 2, draft-3)")
    parser.add_argument("--goal", default="", help="Objetivo o hipótesis que se busca validar con este draft")
    parser.add_argument("--target-device", default="", help="Dispositivo receptor asociado")

    args = parser.parse_args()
    scaffold_draft(args.piece, args.draft, goal=args.goal, target_device=args.target_device)

if __name__ == "__main__":
    main()
