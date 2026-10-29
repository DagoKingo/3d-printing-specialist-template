---
name: snapshot-memory
description: "Entenderse solo con fotos. Verde agrega, rojo borra. El agente adivina la cara desde la foto y espera el sí."
triggers:
  - "te marco en foto"
  - "mira mi captura"
  - "verde agrega"
  - "rojo borra"
  - "adivina la cara"
---

# Skill: Snapshot Memory

## 0. Problema que resuelve

El agente no entiende bien la perspectiva.
El acuerdo se cierra con fotos, no con texto.

## 1. Colores

- Verde = agrega. Lo que se pone.
- Rojo = borra. Lo que se quita.
- Otros colores solo señalan. No obligan.
- El agente en sus fotos usa solo verde y rojo.

## 2. Reglas

- El usuario manda foto marcada. No pica caras.
- El agente adivina la cara desde esa foto.
- El agente responde con su foto desde la misma vista.
- El agente no construye hasta que el usuario lo ordene.
- Sin el sí, no se toca la pieza.

## 3. Pasos

1. Usuario manda foto con verde y rojo.
2. Agente fija desde dónde se tomó: frente, atrás, arriba y lado.
3. Agente guarda su lectura pintada igual en `editions-preview/` y avisa dónde está.
4. Usuario marca encima o da el sí.
5. Solo con orden, el agente construye y verifica cerrado.

## 4. Prohibido

- Dar medidas al usuario.
- Responder solo con texto.
- Adivinar en silencio: ante duda se pregunta antes de tocar.
- Adivinar medidas: nunca se corta a ojo.
- Tocar archivos con el acuerdo abierto.
- Cortar de más: solo la placa marcada, nunca lo vecino.

## 4b. Doctrina: medir antes de borrar

- Antes de borrar cualquier parte se mide su tamaño real por los tres
  lados en la malla.
- Solo se corta lo pedido: lo vecino queda liso, sin ranuras ni escalones.
- El corte cubre todo lo medido y sale un poco al vacío donde hay aire
  para que no quede capa ni pedazo flotando; por el lado del vecino
  va a ras, sin meterse.
- Al final se revisa que la pieza quede de una sola parte y que no
  haya paredes dobles en el mismo plano.

## 5. Lo aprendido (se suma cada vez)

- Corte grande cruza poste y paredes vecinas: el corte va justo a la placa
  marcada en rojo, sin extenderse a lo de al lado.
- Antes y después en la misma vista del usuario para ver lo tocado.
- Solo se avanza con el sí del usuario.
- Corte a ras de la placa: si muerde al vecino deja escalón, y si deja
  rebaba fina se ve como línea punteada con transparencia.
- La línea punteada en vista transparente avisa de rebaba o de cara
  casi pegada a otra: se revisa en vista sólida y se deja lisa.
- El rayado del usuario con lápiz significa el sólido completo, nunca
  se replican sus líneas: la lectura se pinta como volumen sólido.
- El rojo sobre gris transparente hace aguas (parece rayado): mostrar
  el volumen rojo sólido solo más el después, sin aguas.
- Los planos del corte se sacan exactos de la malla sin redondear;
  lo curvo trae pelusa: el corte se extiende al vacío y a ras del sólido.
- Lo naranja con rayas en su visor es el marcado, no la pieza: al
  desmarcar se ve liso. La prueba del corte limpio es el antes y después
  desde la misma vista más el piso que queda de una sola pieza.
- Antes de borrar una pared se mide su grueso real por los tres lados
  en la malla, no se adivina: si el corte queda corto deja una capa fina.
- El corte cubre todo el grueso y sale un poco al vacío para que no
  quede capa; por el lado del vecino va a ras para no morderlo.
- Se mide también el largo de abajo completo: si falta un lado queda
  un pedazo flotando. Al final se revisa que no quede nada suelto
  y que no haya paredes dobles en el mismo plano.
