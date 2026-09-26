# Diagnóstico de Filamentos, Humedad y Secado

El filamento húmedo es el culpable invisible de más del 50% de los fallos de calidad (stringing, piezas frágiles, superficies con burbujas y desprendimientos).

---

## 👂 Cómo Saber si tu Filamento Tiene Humedad

1. **Prueba acústica durante la extrusión:** Se escuchan pequeños chasquidos o "petardeos" rítmicos al salir el plástico por la boquilla (es el agua evaporándose violentamente a 220°C-280°C).
2. **Prueba visual:** La línea extruida sale espumosa o con poros, o al viajar deja un rastro de pelusa que no se corrige ajustando la retracción.
3. **Prueba de flexión en frío (PLA):** Si doblas el filamento con los dedos antes de entrar al extrusor y se quiebra como una rama seca en vez de doblarse elásticamente, el PLA está completamente saturado de agua.

---

## 🌡️ Protocolo de Secado por Material

Utiliza un deshidratador de filamento o un horno con control preciso de temperatura:

| Material | Higroscopia | Temp. de Secado | Tiempo Mínimo | Síntoma de Humedad |
| :--- | :--- | :--- | :--- | :--- |
| **PLA / PLA+** | Baja a Media | 45 °C - 50 °C | 4 a 6 horas | Filamento quebradizo, pérdida de brillo, hilos finos. |
| **PETG** | Alta | 60 °C - 65 °C | 6 a 8 horas | Hilvanado severo (stringing brutal), burbujas en capas. |
| **ABS** | Media | 65 °C - 70 °C | 4 a 6 horas | Grietas inter-capas, menor adhesión. |
| **ASA** | Media | 65 °C - 70 °C | 4 a 6 horas | Poros en superficie, delaminación. |
| **TPU (95A / 85A)**| Muy Alta | 55 °C - 60 °C | 8 a 12 horas | Extrusión espumosa, atascos en engranajes direct-drive. |
| **PA-CF (Nylon+CF)**| Extrema (Horas) | 75 °C - 85 °C | 12 a 24 horas | El Nylon absorbe humedad ambiental en menos de 2 horas. Imprimir siempre desde caja seca (*drybox*). |

> [!WARNING]
> Nunca superes la temperatura máxima de secado indicada. Si calientas el filamento por encima de su temperatura de transición vítrea ($T_g$), las espiras se soldarán entre sí dentro del carrete, arruinando la bobina completa.

---

## 🧽 Adhesión en Placa PEI Texturizada (Centauri Carbon)

1. **Limpieza periódica obligatoria:** Lava la placa con agua tibia y jabón neutro desengrasante una vez por semana o cada 5-10 impresiones. Secar con papel de cocina limpio sin tocar la superficie con los dedos.
2. **Ayudas químicas de adhesión según material:**
   - **PLA / PETG:** Adhesión directa sobre PEI texturizado limpio (a 60°C para PLA y 75°C para PETG).
     > *Nota para PETG:* El PETG puede adherirse con tanta fuerza al PEI que arranque trozos del recubrimiento al retirarlo en caliente. Deja enfriar la placa por debajo de 35°C antes de despegar la pieza.
   - **ABS / ASA:** Se recomienda aplicar una película delgada de pegamento en barra soluble o fijador 3D (Dimafix / 3DLac) para garantizar sujeción a 100°C y permitir despegue fácil al enfriar.
   - **TPU:** Aplicar pegamento en barra como *agente de desmolde* (release agent) para evitar que el poliuretano se fusione permanentemente al PEI.
