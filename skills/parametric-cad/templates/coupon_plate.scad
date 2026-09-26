// =====================================================================
// Probeta Paramétrica de Calibración de Holguras (Fit Test Coupon)
// Inspirado en el flujo de ingeniería de 'kilatev/design-parametric-3d-prints'
// =====================================================================

// Permite validar tolerancias FDM reales en tu Elegoo Centauri Carbon
// en una impresión rápida de 10-15 minutos antes del modelo definitivo.

// === PARÁMETROS CONFIGURABLES ===
tipo_probeta     = "orificio"; // "orificio" (cilindros/tornillos/rodamientos) o "ranura" (correderas)
nominal          = 8.0;        // Dimensión nominal exacta del objeto (ej. 8mm rodamiento 608)
espesor_probeta  = 4.0;        // Altura de la placa
paso_holguras    = [0.10, 0.15, 0.20, 0.25, 0.30]; // Holguras diametrales de prueba
margen_borde     = 6.0;
separacion       = 14.0;

$fn = ($preview) ? 32 : 96;

num_pruebas = len(paso_holguras);
ancho_total = (num_pruebas * nominal) + ((num_pruebas - 1) * separacion) + (2 * margen_borde);
profundo_total = nominal + (2 * margen_borde) + 6.0; // Espacio extra para texto

module probeta() {
    difference() {
        // Placa base
        cube([ancho_total, profundo_total, espesor_probeta]);

        // Alojamientos de prueba con holgura escalonada
        for (i = [0 : num_pruebas - 1]) {
            c = paso_holguras[i];
            pos_x = margen_borde + (nominal / 2) + i * (nominal + separacion);
            pos_y = margen_borde + (nominal / 2);

            if (tipo_probeta == "orificio") {
                // Taladro cilíndrico
                translate([pos_x, pos_y, -1])
                    cylinder(d = nominal + c, h = espesor_probeta + 2);
            } else if (tipo_probeta == "ranura") {
                // Ranura cuadrada / corredera
                translate([pos_x - (nominal + c)/2, pos_y - (nominal + c)/2, -1])
                    cube([nominal + c, nominal + c, espesor_probeta + 2]);
            }

            // Marcador de texto con la tolerancia (+0.10, +0.15, etc.)
            translate([pos_x, profundo_total - 4.5, espesor_probeta - 0.6])
                linear_extrude(1.0)
                    text(str("+", c), size = 2.8, halign = "center", valign = "center", font = "Liberation Sans:style=Bold");
        }
    }
}

probeta();
