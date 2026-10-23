// Patrón completo obligatorio para todo .scad (importador o paramétrico).
// Copiar este archivo al iniciar una pieza y rellenar los bloques.
// Ningún .scad queda sin RENDER, aunque la geometría ya venga centrada.
//
// 1. Encabezado: fuente (FCStd/objeto), malla STL (ASCII, PASS), espec medida
//    (caja X/Y/Z, centro, volumen). Si la fuente cambia, actualizar aquí.
// 2. Vars: todo número sale de aquí. Prohibido hardcodear en los módulos.
// 3. RENDER: "cama" (IMPRIMIBLE, Z=0) | "ensamble" (posición final).
//    En ensambles multicomponente: "preview" | un valor por pieza.
// 4. Módulos: pieza() + cama() + ensamble() (o uno por pieza).
// 5. Selector if/else final. Sin geometría suelta fuera de módulos.
//
// Regla de clip: ENSAMBLE se mide del FCStd y NO se mueve sin orden directa.

// --- Vars: todo sale de aquí ---
// ENSAMBLE = [X, Y, Z]; // sitio medido en el FCStd. NO mover sin orden.

RENDER = "cama"; // "cama" | "ensamble"

module pieza() import("pieza.stl", convexity=4);
module cama() pieza();
module ensamble() pieza();

if (RENDER == "ensamble") {
  ensamble();
} else {
  cama();
}
