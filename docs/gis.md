# GIS — Componente Espacial

**Nivel de madurez:** 3 — Medido
**Última actualización:** 2026-07-25

---

## Sistema de Coordenadas

| Parámetro | Valor |
|-----------|-------|
| Proyección | CRTM05 (Costa Rica Transverse Mercator 2005) |
| EPSG | 5367 |
| Unidades | metros |
| Datum | CR05 (compatible con WGS84) |
| Meridiano central | 84° W |
| Factor de escala | 0.9999 |

---

## Metodología de Reconstrucción

La poligonal se reconstruyó matemáticamente a partir de los rumbos y distancias
del plano topográfico de incorporación del lote.

### Proceso

1. Conversión de rumbos cuadrantales a acimutes geográficos según la tabla:

| Cuadrante | Fórmula del acimut |
|-----------|--------------------|
| N α E | α |
| S α E | 180° − α |
| S α W | 180° + α |
| N α W | 360° − α |

2. Cálculo de incrementos por cada tramo:
   - ΔN = distancia × cos(acimut)
   - ΔE = distancia × sin(acimut)

3. Propagación de coordenadas desde los puntos de control.

4. Verificación del cierre en P5, P8 y P1 (tres puntos de control conocidos del plano).

5. Ajuste por el **método de Bowditch (regla de la brújula)**: el error de cierre
   de cada tramo se distribuye proporcionalmente a la longitud de cada segmento.
   Los puntos de control no se modifican.

---

## Puntos de Control

| Punto | Norte | Este | Origen |
|-------|------:|-----:|--------|
| 1 | 1014025.6500 | 652698.8200 | Plano topográfico |
| 5 | 1013952.6100 | 652626.2600 | Plano topográfico |
| 8 | 1013996.7700 | 652690.6700 | Plano topográfico |

---

## Poligonal Reconstruida

| Punto | Norte | Este | Tipo |
|-------|------:|-----:|------|
| 1 | 1014025.6500 | 652698.8200 | conocido |
| 2 | 1014013.7570 | 652684.7234 | calculado (ajustado) |
| 3 | 1014005.2754 | 652678.6861 | calculado (ajustado) |
| 4 | 1014000.9590 | 652642.5562 | calculado (ajustado) |
| 5 | 1013952.6100 | 652626.2600 | conocido |
| 6 | 1013949.8935 | 652635.8834 | calculado (ajustado) |
| 7 | 1013966.9364 | 652682.2562 | calculado (ajustado) |
| 8 | 1013996.7700 | 652690.6700 | conocido |

---

## Error de Cierre por Tramo

### Tramo A (P1→P5)

| Métrica | Valor |
|---------|------:|
| Error ΔN | +20.3908 m |
| Error ΔE | -0.0030 m |
| Cierre lineal | 20.3908 m |
| Longitud del tramo | 130.21 m |
| Precisión relativa | 1:6 |

> **Advertencia:** El error de cierre (20.3908 m) supera los límites típicos de tolerancia topográfica (1:5000 o ~0.03 m para este tramo). Se recomienda verificar los datos originales del plano.


### Tramo B (P5→P8)

| Métrica | Valor |
|---------|------:|
| Error ΔN | -0.0062 m |
| Error ΔE | -0.0067 m |
| Cierre lineal | 0.0091 m |
| Longitud del tramo | 90.41 m |
| Precisión relativa | 1:9906 |


### Tramo C (P8→P1)

| Métrica | Valor |
|---------|------:|
| Error ΔN | +0.0067 m |
| Error ΔE | +0.0054 m |
| Cierre lineal | 0.0086 m |
| Longitud del tramo | 30.00 m |
| Precisión relativa | 1:3478 |


---

## Área

| | Valor |
|---|------:|
| Área según plano | 2634.29 m² |
| Área calculada (Gauss/Shoelace) | 2528.36 m² |
| Diferencia | -105.93 m² |

---

## Archivos del Proyecto

| Archivo | Descripción |
|---------|-------------|
| `gis/vertices.csv` | Coordenadas de todos los vértices |
| `gis/limite.geojson` | Polígono del límite (WGS84 si pyproj disponible) |
| `gis/limite.kml` | Polígono del límite para Google Earth |
| `gis/casa_generativa.gpkg` | GeoPackage con todas las capas del proyecto |
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

1. **Sistema CRTM05:** Se adoptó EPSG:5367 por ser el sistema oficial de Costa Rica
   y por concordar con las coordenadas del plano de incorporación.

2. **Ajuste Bowditch:** Se aplicó la regla de la brújula dentro de cada tramo entre
   puntos de control. No se modificaron las coordenadas conocidas (P1, P5, P8).

3. **Segmentación en tramos:** La poligonal se dividió en tres tramos independientes
   (P1→P5, P5→P8, P8→P1) para aprovechar los tres puntos de control disponibles
   y minimizar la propagación del error.

4. **Error en tramo A:** El error de cierre en el tramo P1→P5 resultó mayor al
   esperado para una levantamiento topográfico de precisión. Se recomienda
   verificar las coordenadas del plano original, en especial el punto P5.
   Una posible fuente de error es una transposición de dígitos en Norte de P5
   (1013952.61 en lugar de 1013932.61), lo cual reduciría el error a ~0.4 m.
   Esta hipótesis no pudo confirmarse sin el plano original.
