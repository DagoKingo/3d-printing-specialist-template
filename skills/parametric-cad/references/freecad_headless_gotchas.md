# Trampas Críticas de FreeCAD Headless (CLI / Scripting Automation)

Inspirado en los hallazgos de *mijugit/freecad-stl*. Cada punto documentado a continuación fue comprobado empíricamente en FreeCAD 1.0+ y previene fallos silenciosos y bucles infinitos en agentes de IA que automatizan scripts CAD o conversiones STEP/STL.

---

## ⚠️ Las 10 Trampas de `freecadcmd` y sus Soluciones

### 1. Las excepciones no controladas retornan Exit Code 0
- **Trampa:** Si un script de Python en `freecadcmd` lanza una excepción no capturada, FreeCAD imprime `Exception while processing file:...`, pero **retorna código de salida 0** y, además, ¡vuelve a ejecutar el archivo una segunda vez! Para un agente de IA o un pipeline de CI, esto hace que un fallo crítico parezca un éxito rotundo.
- **Solución:** Envolver siempre el código principal en `try...except` y finalizar con un `sys.exit(código)` explícito:
  ```python
  import sys
  try:
      # Lógica de modelado / exportación
      ...
  except Exception as e:
      sys.stderr.write(f"Error fatal: {e}\n")
      sys.exit(1)
  ```

### 2. `if __name__ == "__main__":` NUNCA se ejecuta
- **Trampa:** Cuando `freecadcmd script.py` ejecuta un script, le asigna al módulo el nombre del archivo (ej. `script`), nunca `"__main__"`. Si pones la lógica dentro de `if __name__ == "__main__":`, el script terminará instantáneamente sin hacer nada y con código 0.
- **Solución:** Usa la condición dual:
  ```python
  if __name__ in ("__main__", "script"):
      main()
  ```

### 3. `AngularDeflection` en `meshFromShape` se especifica en RADIANES
- **Trampa:** La función `MeshPart.meshFromShape(LinearDeflection=0.05, AngularDeflection=...)` espera radianes, a pesar de que la interfaz gráfica de FreeCAD muestra grados. Si pasas `30` pensando en "30 grados", estás pasando ~1718 grados, lo que produce mallas con cilindros totalmente facetados e inservibles.
- **Solución:** Convierte siempre con `math.radians()`:
  ```python
  import math
  angular_rad = math.radians(8.0)  # 8 grados para agujeros y cilindros suaves
  mesh = MeshPart.meshFromShape(shape, LinearDeflection=0.05, AngularDeflection=angular_rad)
  ```
  *Nota técnica:* En superficies curvas y taladros cilíndricos, la deflexión angular es la restricción activa principal; reducir la deflexión lineal no mejorará la suavidad del agujero si el ángulo es demasiado grande.

### 4. `print()` se pierde tras `sys.exit()`
- **Trampa:** FreeCAD reemplaza `sys.stdout` y `sys.stderr` con buffers internos que se descartan si el proceso termina mediante `sys.exit()`. El script hace su trabajo, pero la salida por consola desaparece.
- **Solución:** Escribir a través del descriptor real sin buffer:
  ```python
  sys.stderr = sys.__stderr__
  sys.stderr.write("Mensaje asegurado\n")
  ```

### 5. Las banderas `--` en argumentos fallan con `--pass`
- **Trampa:** El parser de `freecadcmd` intercepta cualquier argumento que empiece por `--` antes de pasarlo al script:
  `freecadcmd script.py --pass input.step --out dir` falla con `unrecognised option '--out'`.
- **Solución:** Pasar argumentos complejos vía variables de entorno (por ejemplo en formato JSON con `FCAD_ARGS='{"out": "dir"}'`).

### 6. La importación STEP incluye objetos auxiliares que rompen booleanas (`fuse`)
- **Trampa:** `Import.insert()` importa los sólidos y además un contenedor `App::Part` y planos/ejes de coordenadas (`Origin`, `X-axis`, `XY-plane`). Estos objetos tienen el atributo `Shape` pero rompen las operaciones de unión con `ValueError: Null shape`.
- **Solución:** Filtrar exclusivamente los sólidos reales con caras:
  ```python
  solids = [o for o in doc.Objects if o.isDerivedFrom("Part::Feature") and hasattr(o, "Shape") and o.Shape.Faces]
  ```

### 7. Caracteres no ANSI crashean `freecadcmd`
- **Trampa:** Si la ruta del archivo contiene caracteres especiales, tildes o acentos (`José`, `diseño`), FreeCAD puede abortar con `Application unexpectedly terminated` sin traceback alguno.
- **Solución:** Mantener las rutas de trabajo y nombres de archivo en ASCII puro (`diseno_soporte.py`).

### 8. Barrido helicoidal (`makePipeShell`) desplaza el radio de rosca
- **Trampa:** Usar `Part.Wire(helix).makePipeShell([profile], True, True)` para generar roscas ubica el perfil en un radio exterior incorrecto (en roscas M8 termina en radio 7.4 en lugar de 4.1).
- **Solución:** Generar la rosca helicoidal como un `Part.makeLoft` a través de secciones triangulares giradas y elevadas manualmente (con al menos 24 secciones por vuelta).

### 9. La consola usa páginas de códigos legacy (Windows)
- **Trampa:** En Windows, la consola de FreeCAD usa codepages locales (como `cp1252`), arruinando cualquier caracter fuera de ASCII.
- **Solución:** Reconfigurar la codificación explícitamente:
  ```python
  sys.stderr.reconfigure(encoding="utf-8", errors="replace")
  ```

### 10. Módulos disponibles en modo Headless (sin GUI)
- En scripts ejecutados por terminal o agente puedes importar con seguridad: `Part`, `Mesh`, `MeshPart`, `Import`, `Draft`, `Sketcher`, `PartDesign`, `BOPTools`, `OpenSCAD`.
- **No importar:** `ImportGui`, `FreeCADGui` (no disponibles en modo sin pantalla).
