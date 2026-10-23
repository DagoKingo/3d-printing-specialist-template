# Rendimiento de FreeCAD Headless (una sesion, topologia primero)

Cada invocacion de `freecadcmd` (flatpak) cuesta ~1 min solo en arrancar, y
`Shape.isInside()` sobre piezas reales es lento: un barrido fino supera el
timeout aunque el resultado sea trivial. Estas 3 reglas son obligatorias
antes de automatizar FreeCAD; el detalle de trampas sigue en
`freecad_headless_gotchas.md`.

## Regla 1. Una sola sesion por tarea

Junta TODAS las mediciones en un unico script. Prohibido un script por
pregunta: N preguntas = N arranques = N minutos tirados.

## Regla 2. Topologia antes que tanteo

Pregunta por caras, aristas, wires y cajas (`BoundBox`) antes de muestrear
puntos. Prohibidos los barridos finos con `isInside` (paso <= 0.25 mm sobre
areas grandes): causan timeouts. Para medir un borde usa biseccion (20
iteraciones bastan para 0.01 mm):

```python
def filo(y, z, lo, hi, dentro):
    a, b = lo, hi  # a y b a lados opuestos del borde
    for _ in range(20):
        m = (a + b) / 2
        if dentro(m) == dentro(a):
            a = m
        else:
            b = m
    return (a + b) / 2
```

Patrones rapidos comprobados: aristas circulares para agujeros (centro y
radio directos), `Wire.Vertexes` para contornos, caras planas pequenas para
topes de postes.

## Regla 3. OpenSCAD crea, FreeCAD mide

Piezas nuevas en OpenSCAD (compila en segundos). FreeCAD solo para medir lo
existente y para verificar (volumen, caja, interferencia `common`).

## Regla 4. La visibilidad la fija el usuario una vez, el agente la hereda y la preserva

`freecadcmd` no escribe `GuiDocument.xml` (cada `doc.save()` headless lo
elimina del zip): al abrir en la interfaz los cuerpos salen apagados.
PROHIBIDO inventar `GuiDocument.xml` a mano (FreeCAD lo rechaza al abrir).
Procedimiento: el usuario abre, prende todo con Espacio y guarda; el agente
guarda ese `GuiDocument.xml` como
`skills/parametric-cad/references/GuiDocument.template.xml` de la pieza
(los `name=` de cada `ViewProvider` deben coincidir con los objetos) y lo
reinyecta en el zip tras cada guardado headless, verificando con `zipfile`
+ apertura de control (volúmenes intactos). Verificar siempre en coordenadas
GLOBALES (placa aplicada): `o.Shape.BoundBox` ignora `Placement`; componer
con `o.Placement.toMatrix()` antes de afirmar posiciones).
