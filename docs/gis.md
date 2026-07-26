# GIS — Componente Espacial

**Nivel de madurez:** 3 — Medido (pendiente verificación de campo)
**Última actualización:** 2026-07-26

---

## Sistema de Coordenadas

| Parámetro | Valor |
|-----------|-------|
| Proyección | UTM Zone 17N |
| EPSG | 32617 |
| Datum | WGS 84 |
| Unidades | metros |
| Meridiano central | 81° W |
| Factor de escala | 0.9996 |

Verificado con pyproj: el terreno ubica en 9.17°N, 79.61°W — Chilibre, Panamá.

---

## Contexto del Plano

El plano de incorporación (dic. 2020, Téc. Top. Manuel Rumbo Puga, Lic. 80-304-020)
registra la fusión de dos propiedades. Contiene dos levantamientos:

### Lote "A" — franja incorporada (214.29 m²)

Cedida por la Finca 249115 para dar acceso a Calle Tumba Muerto.

| Estación | Distancia (m) | Rumbo |
|----------|-------------:|-------|
| 1-2 | 20.68 | S 42°58'17" W |
| 2-3 | 11.99 | S 30°13'54" W |
| 3-8 | 12.46 | S 74°14'30" E |
| 8-1 | 30.00 | N 15°45'10" E |

### Incorporación completa (2,634.38 m²)

| Estación | Distancia (m) | Rumbo |
|----------|-------------:|-------|
| 1-2 | 20.68 | S 42°58'17" W |
| 2-3 | 11.99 | S 30°13'54" W |
| 3-4 | 37.54 | S 74°14'30" W |
| 4-5 | 60.00 | S 15°45'30" W |
| 5-6 | 10.00 | S 74°14'30" E |
| 6-7 | 49.41 | N 69°49'06" E |
| 7-8 | 31.00 | N 15°45'10" E |
| 8-1 | 30.00 | N 15°45'10" E |

En P3 los dos levantamientos divergen en direcciones opuestas a lo largo del
rumbo S/N 74°14'30": el Lote A va 12.46m al Este hacia P8 (lindero interno suprimido),
y la incorporación completa va 37.54m al Oeste hacia P4 (lindero externo).

---

## Estrategia de Reconstrucción (v2)

### Anclas disponibles

| Punto | Norte (m) | Este (m) | Confiabilidad |
|-------|----------:|---------:|---------------|
| P1 | 1014025.6500 | 652698.8200 | GPS Garmin (±3–5 m) |
| P5 | 1013952.6100 | 652626.2600 | GPS Garmin (±3–5 m) |
| P8 | 1013996.7700 | 652690.6700 | GPS Garmin (±3–5 m) |
| **P3** | **1014000.1592** | **652678.6869** | **Alta — dos métodos coinciden en 0.01 m** |

P3 fue determinado por dos rutas independientes:
- Desde P1 vía Lote A (P1→P2→P3)
- Desde P8 vía segmento norte (P8 + 12.46m N74°14'30"W)

Ambas dan P3 con solo **0.01 m** de diferencia — el punto más fiablemente conocido.

### Tramos de ajuste

| Tramo | Segmentos | Anclas | Cierre | Precisión |
|-------|-----------|--------|--------|-----------|
| B | P5→P6→P7→P8 | P5, P8 | 0.009 m | **1:9,906** — excelente |
| C | P8→P1 | P8, P1 | 0.009 m | **1:3,478** — buena |
| O (oeste) | P3→P4→P5 | P3, P5 | 20.39 m | **1:5** — error documentado |

---

## Poligonal Reconstruida

| Punto | Norte (m) | Este (m) | Método |
|-------|----------:|---------:|--------|
| 1 | 1014025.6500 | 652698.8200 | GPS (ancla) |
| 2 | 1014010.5186 | 652684.7238 | Lote A, sin ajuste |
| 3 | 1014000.1592 | 652678.6869 | Lote A = segmento norte (0.01 m) |
| 4 | 1013997.8119 | 652642.5567 | Bowditch tramo O (+7.85 m N corregido) |
| 5 | 1013952.6100 | 652626.2600 | GPS (ancla) |
| 6 | 1013949.8935 | 652635.8834 | Bowditch tramo B |
| 7 | 1013966.9364 | 652682.2562 | Bowditch tramo B |
| 8 | 1013996.7700 | 652690.6700 | GPS (ancla) |

---

## Error en el Tramo Oeste (P3→P4→P5)

### Magnitud

| Métrica | Valor |
|---------|------:|
| Error ΔN | +20.39 m |
| Error ΔE | −0.003 m |
| Cierre lineal | 20.39 m |
| Longitud del tramo | 97.54 m |
| Precisión relativa | 1:5 |

### Diagnóstico

El error es **exclusivamente en Norte** — el Este cierra a 3 mm. Este patrón
descarta errores aleatorios y pendiente uniforme (demostrado matemáticamente:
un factor de pendiente uniforme reduce ΔN y ΔE proporcionalmente, pero ΔE ya
cierra perfecto — aplicarlo lo rompería).

**Hipótesis más probable:** El terreno es quebrado con pendientes fuertes. Los
segmentos 3-4 (S74°W, 37.54m) y 4-5 (S15°W, 60m) probablemente provienen de la
parcelación original de 1976, medidos con cinta sobre pendiente sin corrección
horizontal. Al transcribir al plano 2020 se copiaron las distancias de pendiente
como si fueran horizontales. Dado que el segmento 4-5 va casi en dirección N-S
(cos 15°=0.96), su componente norte absorbe casi todo el error.

**Descartado:** transposición de dígito en P5, corrección de pendiente uniforme,
error de bearing, error solo en d(3-4).

### Verificación pendiente — agosto 2026

Lo que medir en campo:

1. **Distancia horizontal P3→P4** — comparar con 37.54 m del plano.
2. **Distancia horizontal P4→P5** — comparar con 60.00 m del plano. Este es el segmento clave.
3. **Desnivel total P3→P5** — con clinómetro o app para estimar corrección de pendiente.
4. **Existencia física de P4** — el plano indica todos los puntos con varilla de acero.
   Si P4 no existe o fue movido, el dato de campo puede ser incorrecto.
5. **Coordenada GPS de P4** — con teléfono o GPS de mano para triangulación inicial.

---

## Área

| | Valor |
|---|------:|
| Área registrada (plano, legal) | 2,634.29 m² |
| Área medida en plano (de rumbos y dist.) | 2,634.38 m² |
| **Lote A calculado** | **214.19 m²** ← preciso (error 0.10 m²) |
| Polígono original estimado | ~2,091 m² |
| Total reconstruido | 2,305 m² |
| Diferencia vs. registrado | −329 m² (13.6%) |

La diferencia de área se debe al error en el tramo O. El área legal vigente
es **2,634.29 m²**. El Lote A (214.19 m²) es la parte más precisa del cálculo.

---

## Archivos del Proyecto

| Archivo | Descripción |
|---------|-------------|
| `gis/vertices.csv` | Coordenadas de todos los vértices (UTM Zone 17N) |
| `gis/limite.geojson` | Polígono del límite (WGS84, convertido con pyproj) |
| `gis/limite.kml` | Polígono del límite para Google Earth |
| `gis/casa_generativa.gpkg` | GeoPackage con todas las capas |
| `gis/proyecto_qgis.qgz` | Proyecto QGIS preconfigurado |
| `gis/reconstruccion.py` | Script de reconstrucción reproducible |

---

## Capas del GeoPackage

| Capa | Tipo | Estado | Descripción |
|------|------|--------|-------------|
| boundary | Polígono | Completa | Límite del terreno |
| vertices | Punto | Completa | Vértices de la poligonal |
| trees | Punto | Vacía | Árboles y vegetación relevante |
| water | Línea | Vacía | Fuentes de agua y drenajes |
| photos | Punto | Vacía | Puntos de registro fotográfico |
| trails | Línea | Vacía | Senderos y accesos |
| zones | Polígono | Vacía | Zonas de uso del terreno |
| structures | Polígono | Vacía | Estructuras y construcciones |

---

## Decisiones Documentadas

1. **UTM Zone 17N (EPSG:32617):** Verificado con pyproj: 9.17°N, 79.61°W.
   Corregido de error inicial que usaba CRTM05 (Costa Rica).

2. **P3 como ancla adicional:** Determinado con 0.01 m de consistencia entre
   dos rutas independientes. Se usa como inicio del tramo O en lugar de P1.

3. **Tramo O ajustado Bowditch entre P3 y P5:** La corrección de 20.39 m se
   distribuye sobre los 97.54 m del tramo. P4 recibe +7.85 m N de corrección.

4. **Lote A sin ajuste:** Los segmentos 1-2, 2-3 no se ajustan — las imprecisiones
   en la franja cedida son aceptadas. P3 queda en su posición natural (0.01 m).

5. **Error en tramo O documentado — pendiente verificación de campo en agosto 2026.**
   Hasta entonces, la posición de P4 es una estimación Bowditch.
