# GIS — Componente Espacial

**Nivel de madurez:** 3 — Medido
**Última actualización:** 2026-07-25

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
| Cobertura | 78°W–84°W — incluye Panamá |

El plano indica "Norte de Cuadrícula", lo que confirma el uso de norte UTM.
Los puntos de control verificados con pyproj ubican el terreno en 9.17°N, 79.61°W — consistente con Chilibre, Panamá.

---

## Contexto del Plano Topográfico

El plano de incorporación (diciembre 2020, Téc. Top. Manuel Rumbo Puga) registra
la unión de dos propiedades. Contiene **dos levantamientos distintos**:

### Levantamiento 1 — Lote "A" segregado (214.29 m²)

Pequeña franja cedida por la Finca 249115 (colindante norte) e incorporada al terreno.

| Estación | Distancia (m) | Rumbo |
|----------|-------------:|-------|
| 1-2 | 20.68 | S 42°58'17" W |
| 2-3 | 11.99 | S 30°13'54" W |
| 3-8 | 12.46 | S 74°14'30" E |
| 8-1 | 30.00 | N 15°45'10" E |

### Levantamiento 2 — Incorporación completa (2,634.38 m²)

Poligonal exterior de la finca resultante de la incorporación.

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

### Geometría de la fusión

En el punto 3, los dos levantamientos divergen en **direcciones opuestas** sobre el mismo rumbo S 74°14'30":

- Lote A va **12.46 m hacia el Este** (→ P8): era el lindero interno entre ambas fincas, suprimido al fusionar.
- La finca completa va **37.54 m hacia el Oeste** (→ P4): lindero externo del terreno original.

Los segmentos 1-2, 2-3 y 8-1 son compartidos entre ambos levantamientos.

---

## Metodología de Reconstrucción

### Proceso

1. Conversión de rumbos cuadrantales a acimutes geográficos:

| Cuadrante | Fórmula |
|-----------|---------|
| N α E | acimut = α |
| S α E | acimut = 180° − α |
| S α W | acimut = 180° + α |
| N α W | acimut = 360° − α |

2. Incrementos por tramo: ΔN = d·cos(acimut), ΔE = d·sin(acimut)

3. Propagación desde los tres puntos de control conocidos (P1, P5, P8).

4. Verificación del cierre en cada punto de control.

5. Ajuste **Bowditch (regla de la brújula)**: el error de cada tramo se distribuye
   proporcionalmente a la longitud de sus segmentos. Los puntos de control no se modifican.

---

## Puntos de Control

Coordenadas del plano, medidas con GPS Garmin (precisión de consumo, ±3–5 m típico).

| Punto | Norte (m) | Este (m) | Origen |
|-------|----------:|---------:|--------|
| 1 | 1014025.6500 | 652698.8200 | Plano topográfico |
| 5 | 1013952.6100 | 652626.2600 | Plano topográfico |
| 8 | 1013996.7700 | 652690.6700 | Plano topográfico |

---

## Poligonal Reconstruida

| Punto | Norte (m) | Este (m) | Tipo |
|-------|----------:|---------:|------|
| 1 | 1014025.6500 | 652698.8200 | conocido |
| 2 | 1014013.7570 | 652684.7234 | calculado — ajustado |
| 3 | 1014005.2754 | 652678.6861 | calculado — ajustado |
| 4 | 1014000.9590 | 652642.5562 | calculado — ajustado |
| 5 | 1013952.6100 | 652626.2600 | conocido |
| 6 | 1013949.8935 | 652635.8834 | calculado — ajustado |
| 7 | 1013966.9364 | 652682.2562 | calculado — ajustado |
| 8 | 1013996.7700 | 652690.6700 | conocido |

Aproximado en WGS84: 9.17°N, 79.61°W — Chilibre, Panamá.

---

## Error de Cierre por Tramo

### Tramo A — P1 → P5 (segmentos 1-2, 2-3, 3-4, 4-5)

| Métrica | Valor |
|---------|------:|
| Error ΔN | +20.3908 m |
| Error ΔE | −0.0030 m |
| Cierre lineal | 20.3908 m |
| Longitud del tramo | 130.21 m |
| Precisión relativa | **1:6** |

> **Error anómalo documentado.** El error es casi exclusivamente en Norte (+20.39 m)
> con Este prácticamente perfecto (−0.003 m). Este patrón apunta a una discrepancia
> entre instrumentos: los rumbos provienen de la estación total (Topcon 229, precisa)
> y las coordenadas de control del GPS Garmin de mano (±3–5 m). Una diferencia de
> 20 m en Norte es posible si el GPS tuvo condiciones adversas de cobertura satelital,
> o si hubo un error de transcripción al pasar las coordenadas al plano.
>
> **Hipótesis descartada:** cambiar Norte de P5 a 1013932.61 mejora el tramo A
> (1:333) pero colapsa el tramo B (1:5). La inconsistencia es estructural.
>
> **Acción recomendada:** verificar con el topógrafo (Lic. Manuel Rumbo Puga,
> CED 8-211-1821) las coordenadas originales registradas en el GPS.

### Tramo B — P5 → P8 (segmentos 5-6, 6-7, 7-8)

| Métrica | Valor |
|---------|------:|
| Error ΔN | −0.0062 m |
| Error ΔE | −0.0067 m |
| Cierre lineal | 0.0091 m |
| Longitud del tramo | 90.41 m |
| Precisión relativa | **1:9,906** |

Excelente precisión — consistente con estación total.

### Tramo C — P8 → P1 (segmento 8-1)

| Métrica | Valor |
|---------|------:|
| Error ΔN | +0.0067 m |
| Error ΔE | +0.0054 m |
| Cierre lineal | 0.0086 m |
| Longitud del tramo | 30.00 m |
| Precisión relativa | **1:3,478** |

Buena precisión — consistente con estación total.

---

## Área

| | Valor |
|---|------:|
| Área registrada (plano) | 2,634.29 m² |
| Área medida en plano (de rumbos y distancias) | 2,634.38 m² |
| Área calculada con poligonal ajustada | 2,528.36 m² |
| Diferencia vs. registrada | −105.93 m² |

La diferencia de área (−106 m²) se explica por el error del tramo A: el punto P5
ajustado queda desplazado ~20 m al sur de su posición registrada, comprimiendo el polígono.
El área legal vigente es **2,634.29 m²**.

---

## Archivos del Proyecto

| Archivo | Descripción |
|---------|-------------|
| `gis/vertices.csv` | Coordenadas de todos los vértices (UTM Zone 17N) |
| `gis/limite.geojson` | Polígono del límite (WGS84, convertido con pyproj) |
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

1. **Sistema UTM Zone 17N (EPSG:32617):** Las coordenadas del plano ubican el terreno
   en 9.17°N, 79.61°W (verificado con pyproj), consistente con Chilibre, Panamá.
   Se corrigió un error inicial que usaba CRTM05 (EPSG:5367, Costa Rica).

2. **Ajuste Bowditch por tramos:** La poligonal se dividió en tres tramos anclados
   en los puntos de control (P1→P5, P5→P8, P8→P1). El ajuste distribuye el error
   proporcionalmente a la longitud de cada segmento sin modificar los puntos de control.

3. **Puntos de control no modificados:** P1, P5 y P8 se mantienen exactamente
   como aparecen en el plano.

4. **Dos levantamientos en un mismo plano:** El plano contiene los datos del
   Lote A (214.29 m²) y los de la incorporación completa (2,634.38 m²).
   La reconstrucción usa exclusivamente los datos de incorporación.

5. **Error de tramo A documentado pero no resuelto:** El error de 20.39 m en Norte
   en el tramo P1→P5 está documentado. Requiere verificación con el topógrafo antes
   de poder considerarse resuelto. Hasta entonces, la poligonal actual es la mejor
   aproximación posible con los datos disponibles.
