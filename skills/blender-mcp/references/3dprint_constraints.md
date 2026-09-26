# Restricciones FDM para Scripts de Blender

Cuando generes o manipules mallas dentro de Blender para la Elegoo Centauri Carbon, utiliza este bloque estándar de verificación y exportación en Python:

```python
import bpy

def preparar_y_exportar_para_fdm(filepath_stl, objeto_nombre=None):
    """
    Limpia la malla, aplica transformaciones y colapsa modificadores
    garantizando un archivo STL hermético (manifold).
    """
    # 1. Seleccionar objeto
    if objeto_nombre:
        obj = bpy.data.objects.get(objeto_nombre)
        bpy.context.view_layer.objects.active = obj
    else:
        obj = bpy.context.active_object
        
    if not obj or obj.type != 'MESH':
        raise ValueError("No hay un objeto tipo MESH activo seleccionado.")

    # 2. Modo objeto: Aplicar modificadores
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    for mod in obj.modifiers:
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception as e:
            print(f"No se pudo aplicar modificador {mod.name}: {e}")

    # 3. Aplicar escala y rotación (Fundamental para dimensiones exactas en el Slicer)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    # 4. Modo edición: Reparación y normales
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Recalcular normales hacia afuera
    bpy.ops.mesh.normals_make_consistent(inside=False)
    
    # Eliminar geometría degenerada (caras de área cero, vértices huérfanos)
    bpy.ops.mesh.dissolve_degenerate()
    
    # Rellenar pequeños orificios no intencionados
    bpy.ops.mesh.fill_holes(sides=4)

    bpy.ops.object.mode_set(mode='OBJECT')

    # 5. Exportar a STL en unidades milimétricas
    # Blender 4.0+ usa el nuevo exportador wm.stl_export
    try:
        bpy.ops.wm.stl_export(filepath=filepath_stl, export_selected_objects=True)
    except AttributeError:
        # Fallback para Blender < 4.0
        bpy.ops.export_mesh.stl(filepath=filepath_stl, use_selection=True)

    print(f"✅ STL exportado con éxito para FDM: {filepath_stl}")
```

---

## 📋 Checklist Post-Generación en Blender

Indica siempre al usuario los pasos recomendados tras modelar en Blender:
1. Activar la superposición de orientación de caras: **Viewport Overlays > Face Orientation** (todas las caras deben verse **azules**; si hay rojo, están invertidas).
2. Comprobar aristas no herméticas: En modo edición: **Select > Select All by Trait > Non Manifold**. Si se ilumina algún vértice, la malla necesita soldarse (`Merge by Distance`).
3. Verificar que las partes más delgadas tengan al menos 1.2 mm de grosor antes de enviar a OrcaSlicer.
