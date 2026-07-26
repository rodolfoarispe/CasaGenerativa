#!/usr/bin/env python3
"""
Casa Generativa — Reconstrucción GIS
=====================================
Reconstruye la poligonal del terreno a partir de rumbos y distancias
del plano topográfico de incorporación del lote.

Reproducible: todos los archivos de salida se generan desde este script.

Uso:
    python gis/reconstruccion.py
"""

import math
import csv
import json
import os
import sqlite3
import struct
import zipfile
from datetime import datetime

# ============================================================
# DATOS DE ENTRADA
# ============================================================

# Puntos de control conocidos: (Norte, Este) en CRTM05 (EPSG:5367)
CONTROL = {
    1: (1014025.65, 652698.82),
    5: (1013952.61, 652626.26),
    8: (1013996.77, 652690.67),
}

# Poligonal: (de, a, distancia_m, NS, grados, minutos, segundos, EW)
POLIGONAL = [
    (1, 2, 20.68, 'S', 42, 58, 17, 'W'),
    (2, 3, 11.99, 'S', 30, 13, 54, 'W'),
    (3, 4, 37.54, 'S', 74, 14, 30, 'W'),
    (4, 5, 60.00, 'S', 15, 45, 30, 'W'),
    (5, 6, 10.00, 'S', 74, 14, 30, 'E'),
    (6, 7, 49.41, 'N', 69, 49,  6, 'E'),
    (7, 8, 31.00, 'N', 15, 45, 10, 'E'),
    (8, 1, 30.00, 'N', 15, 45, 10, 'E'),
]

AREA_PLANO = 2634.29   # m² según plano topográfico
EPSG_CRTM05 = 5367

# Tramos entre puntos de control:
# Tramo A: P1 → P2 → P3 → P4 → P5
# Tramo B: P5 → P6 → P7 → P8
# Tramo C: P8 → P1
TRAMOS = {
    'A (P1→P5)': (POLIGONAL[0:4], CONTROL[1], CONTROL[5]),
    'B (P5→P8)': (POLIGONAL[4:7], CONTROL[5], CONTROL[8]),
    'C (P8→P1)': (POLIGONAL[7:8], CONTROL[8], CONTROL[1]),
}

# ============================================================
# FUNCIONES MATEMÁTICAS
# ============================================================

def gms_a_dd(g, m, s):
    """Grados, minutos, segundos → grados decimales."""
    return g + m / 60 + s / 3600


def rumbo_a_acimut(ns, g, m, s, ew):
    """Convierte rumbo cuadrantal a acimut geográfico en grados decimales."""
    angulo = gms_a_dd(g, m, s)
    if   ns == 'N' and ew == 'E': return angulo
    elif ns == 'S' and ew == 'E': return 180.0 - angulo
    elif ns == 'S' and ew == 'W': return 180.0 + angulo
    elif ns == 'N' and ew == 'W': return 360.0 - angulo
    raise ValueError(f"Rumbo inválido: {ns} {g}°{m}'{s}\" {ew}")


def delta_ne(distancia, ns, g, m, s, ew):
    """ΔN y ΔE a partir de distancia y rumbo."""
    az = math.radians(rumbo_a_acimut(ns, g, m, s, ew))
    return distancia * math.cos(az), distancia * math.sin(az)


def area_shoelace(pts):
    """Área del polígono por fórmula de Gauss (Shoelace).
    pts: lista de (Norte, Este) en orden.
    """
    n = len(pts)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += pts[i][1] * pts[j][0]   # E_i * N_{i+1}
        area -= pts[j][1] * pts[i][0]   # E_{i+1} * N_i
    return abs(area) / 2.0

# ============================================================
# CÁLCULO Y AJUSTE BOWDITCH
# ============================================================

def calcular_tramo(segmentos, inicio):
    """Propaga coordenadas a lo largo de un tramo. Devuelve dict {punto: (N, E)}."""
    coords = {}
    N, E = inicio
    for seg in segmentos:
        _, to_pt, dist, ns, g, m, s, ew = seg
        dN, dE = delta_ne(dist, ns, g, m, s, ew)
        N += dN
        E += dE
        coords[to_pt] = (N, E)
    return coords


def ajuste_bowditch(segmentos, inicio, fin_conocido, nombre):
    """Aplica ajuste Bowditch (regla de la brújula) a un tramo.

    Distribuye el error de cierre proporcionalmente a la longitud de cada segmento.
    Los puntos de control (inicio y fin) no se modifican.

    Devuelve:
        adjusted: dict {punto: (N, E)} con coordenadas ajustadas
        reporte: dict con métricas del cierre
    """
    raw = calcular_tramo(segmentos, inicio)
    ultimo_pt = segmentos[-1][1]
    calc_N, calc_E = raw[ultimo_pt]
    conoc_N, conoc_E = fin_conocido

    err_N = conoc_N - calc_N
    err_E = conoc_E - calc_E
    cierre = math.sqrt(err_N**2 + err_E**2)
    total_d = sum(s[2] for s in segmentos)
    precision = total_d / cierre if cierre > 0.0001 else float('inf')

    print(f"\n  Tramo {nombre}")
    print(f"    Calculado: N={calc_N:.4f}  E={calc_E:.4f}")
    print(f"    Conocido:  N={conoc_N:.4f}  E={conoc_E:.4f}")
    print(f"    Error N: {err_N:+.4f} m   Error E: {err_E:+.4f} m")
    print(f"    Cierre: {cierre:.4f} m / {total_d:.2f} m  →  1:{precision:.0f}")
    if cierre > 0.3:
        print(f"    *** ADVERTENCIA: cierre {cierre:.4f} m supera tolerancia típica ***")

    # Propagar con corrección acumulada proporcional a distancia
    adjusted = {}
    cum_d = 0.0
    N_raw, E_raw = inicio
    for seg in segmentos:
        _, to_pt, dist, ns, g, m, s, ew = seg
        dN, dE = delta_ne(dist, ns, g, m, s, ew)
        N_raw += dN
        E_raw += dE
        cum_d += dist
        prop = cum_d / total_d
        adjusted[to_pt] = (N_raw + err_N * prop, E_raw + err_E * prop)

    reporte = {
        'nombre': nombre,
        'err_N': err_N,
        'err_E': err_E,
        'cierre_m': cierre,
        'total_m': total_d,
        'precision': precision,
    }
    return adjusted, reporte

# ============================================================
# GENERACIÓN DE ARCHIVOS
# ============================================================

def escribir_csv(coords, ruta):
    with open(ruta, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['punto', 'norte', 'este', 'tipo'])
        for pt in range(1, 9):
            N, E = coords[pt]
            tipo = 'conocido' if pt in CONTROL else 'calculado'
            w.writerow([pt, f'{N:.4f}', f'{E:.4f}', tipo])
    print(f"  ✓ {ruta}")


def escribir_geojson(coords, ruta):
    try:
        from pyproj import Transformer
        t = Transformer.from_crs("EPSG:5367", "EPSG:4326", always_xy=True)
        def xy(pt):
            N, E = coords[pt]
            lon, lat = t.transform(E, N)
            return [lon, lat]
        crs_nota = "WGS84 (EPSG:4326) — transformado desde CRTM05"
    except ImportError:
        def xy(pt):
            N, E = coords[pt]
            return [E, N]
        crs_nota = "CRTM05 (EPSG:5367) — pyproj no disponible, coordenadas locales"

    anillo = [xy(i) for i in range(1, 9)] + [xy(1)]
    area_calc = area_shoelace([coords[i] for i in range(1, 9)])

    features = [
        {
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [anillo]},
            "properties": {
                "nombre": "Límite del terreno",
                "area_calculada_m2": round(area_calc, 2),
                "area_plano_m2": AREA_PLANO,
                "crs_origen": "CRTM05 EPSG:5367",
                "crs_archivo": crs_nota,
            }
        }
    ]
    for pt in range(1, 9):
        N, E = coords[pt]
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": xy(pt)},
            "properties": {
                "punto": pt,
                "norte_crtm05": round(N, 4),
                "este_crtm05": round(E, 4),
                "tipo": "conocido" if pt in CONTROL else "calculado",
            }
        })

    fc = {"type": "FeatureCollection", "features": features}
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(fc, f, indent=2, ensure_ascii=False)
    print(f"  ✓ {ruta}")


def escribir_kml(coords, ruta):
    try:
        from pyproj import Transformer
        t = Transformer.from_crs("EPSG:5367", "EPSG:4326", always_xy=True)
        def coord_str(pt):
            N, E = coords[pt]
            lon, lat = t.transform(E, N)
            return f"{lon:.8f},{lat:.8f},0"
    except ImportError:
        def coord_str(pt):
            N, E = coords[pt]
            return f"{E:.4f},{N:.4f},0"

    anillo = " ".join(coord_str(i) for i in list(range(1, 9)) + [1])

    vertices_kml = ""
    for pt in range(1, 9):
        vertices_kml += f"""
    <Placemark>
      <name>P{pt}</name>
      <styleUrl>#vertex</styleUrl>
      <Point><coordinates>{coord_str(pt)}</coordinates></Point>
    </Placemark>"""

    kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Casa Generativa — Límite del terreno</name>
    <Style id="limite">
      <LineStyle><color>ff0000ff</color><width>2</width></LineStyle>
      <PolyStyle><color>400000ff</color></PolyStyle>
    </Style>
    <Style id="vertex">
      <IconStyle><color>ffff0000</color><scale>0.8</scale></IconStyle>
    </Style>
    <Placemark>
      <name>Límite</name>
      <styleUrl>#limite</styleUrl>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>{anillo}</coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
    {vertices_kml}
  </Document>
</kml>"""

    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(kml)
    print(f"  ✓ {ruta}")


# ---- GeoPackage ----

def _wkb_punto(x, y):
    return struct.pack('<BIdd', 1, 1, x, y)


def _wkb_poligono(anillos):
    partes = [struct.pack('<BII', 1, 3, len(anillos))]
    for anillo in anillos:
        partes.append(struct.pack('<I', len(anillo)))
        for x, y in anillo:
            partes.append(struct.pack('<dd', x, y))
    return b''.join(partes)


def _gpkg_blob(wkb, srs_id=EPSG_CRTM05):
    # Header GeoPackage: 'GP' + version(0) + flags(0x01=LE sin envelope) + srs_id LE
    return b'GP' + bytes([0, 0x01]) + struct.pack('<i', srs_id) + wkb


def escribir_gpkg(coords, ruta):
    if os.path.exists(ruta):
        os.remove(ruta)

    conn = sqlite3.connect(ruta)
    conn.execute("PRAGMA application_id = 1196444487")   # 0x47504B47 = GPKG
    conn.execute("PRAGMA user_version = 10300")          # versión 1.3.0

    conn.executescript("""
        CREATE TABLE gpkg_spatial_ref_sys (
            srs_name TEXT NOT NULL,
            srs_id INTEGER NOT NULL PRIMARY KEY,
            organization TEXT NOT NULL,
            organization_coordsys_id INTEGER NOT NULL,
            definition TEXT NOT NULL,
            description TEXT
        );
        CREATE TABLE gpkg_contents (
            table_name TEXT NOT NULL PRIMARY KEY,
            data_type TEXT NOT NULL,
            identifier TEXT,
            description TEXT DEFAULT '',
            last_change DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
            min_x REAL, min_y REAL, max_x REAL, max_y REAL,
            srs_id INTEGER,
            CONSTRAINT fk_gc_r_srs_id FOREIGN KEY (srs_id) REFERENCES gpkg_spatial_ref_sys(srs_id)
        );
        CREATE TABLE gpkg_geometry_columns (
            table_name TEXT NOT NULL,
            column_name TEXT NOT NULL,
            geometry_type_name TEXT NOT NULL,
            srs_id INTEGER NOT NULL,
            z TINYINT NOT NULL,
            m TINYINT NOT NULL,
            CONSTRAINT pk_geom_cols PRIMARY KEY (table_name, column_name),
            CONSTRAINT fk_gc_tn FOREIGN KEY (table_name) REFERENCES gpkg_contents(table_name),
            CONSTRAINT fk_gc_srs FOREIGN KEY (srs_id) REFERENCES gpkg_spatial_ref_sys(srs_id)
        );
    """)

    conn.executemany("INSERT INTO gpkg_spatial_ref_sys VALUES (?,?,?,?,?,?)", [
        ('Undefined Cartesian',  -1, 'NONE', -1,
         'undefined', 'undefined cartesian'),
        ('Undefined Geographic',  0, 'NONE',  0,
         'undefined', 'undefined geographic'),
        ('WGS 84', 4326, 'EPSG', 4326,
         'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],'
         'PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]',
         'WGS 84'),
        ('CRTM05', 5367, 'EPSG', 5367,
         'PROJCS["CRTM05",GEOGCS["CR05",DATUM["Costa_Rica_2005",'
         'SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],'
         'UNIT["degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],'
         'PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-84],'
         'PARAMETER["scale_factor",0.9999],PARAMETER["false_easting",500000],'
         'PARAMETER["false_northing",0],UNIT["metre",1]]',
         'Costa Rica Transverse Mercator 2005'),
    ])

    ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
    all_N = [coords[i][0] for i in range(1, 9)]
    all_E = [coords[i][1] for i in range(1, 9)]
    bbox = (min(all_E), min(all_N), max(all_E), max(all_N))

    def reg_capa(nombre, tipo_geom, descripcion):
        conn.execute(
            "INSERT INTO gpkg_contents VALUES (?,?,?,?,?,?,?,?,?,?)",
            (nombre, 'features', nombre, descripcion, ts, *bbox, EPSG_CRTM05)
        )
        conn.execute(
            "INSERT INTO gpkg_geometry_columns VALUES (?,?,?,?,?,?)",
            (nombre, 'geom', tipo_geom, EPSG_CRTM05, 0, 0)
        )

    # --- Capa: boundary ---
    conn.execute("""CREATE TABLE boundary (
        fid INTEGER PRIMARY KEY AUTOINCREMENT,
        geom BLOB, nombre TEXT, area_m2 REAL, fuente TEXT
    )""")
    anillo = [(coords[i][1], coords[i][0]) for i in range(1, 9)]
    anillo.append(anillo[0])
    area_calc = area_shoelace([coords[i] for i in range(1, 9)])
    conn.execute("INSERT INTO boundary (geom, nombre, area_m2, fuente) VALUES (?,?,?,?)", (
        _gpkg_blob(_wkb_poligono([anillo])),
        'Límite del terreno', round(area_calc, 2),
        'Plano topográfico de incorporación'
    ))
    reg_capa('boundary', 'POLYGON', 'Límite del terreno')

    # --- Capa: vertices ---
    conn.execute("""CREATE TABLE vertices (
        fid INTEGER PRIMARY KEY AUTOINCREMENT,
        geom BLOB, punto INTEGER, norte REAL, este REAL, tipo TEXT
    )""")
    for pt in range(1, 9):
        N, E = coords[pt]
        conn.execute("INSERT INTO vertices (geom, punto, norte, este, tipo) VALUES (?,?,?,?,?)", (
            _gpkg_blob(_wkb_punto(E, N)),
            pt, round(N, 4), round(E, 4),
            'conocido' if pt in CONTROL else 'calculado'
        ))
    reg_capa('vertices', 'POINT', 'Vértices de la poligonal')

    # --- Capas vacías ---
    capas_vacias = [
        ('trees',      'POINT',      'Árboles y vegetación relevante'),
        ('water',      'LINESTRING', 'Fuentes de agua y drenajes'),
        ('photos',     'POINT',      'Puntos de registro fotográfico'),
        ('trails',     'LINESTRING', 'Senderos y accesos'),
        ('zones',      'POLYGON',    'Zonas de uso del terreno'),
        ('structures', 'POLYGON',    'Estructuras y construcciones'),
    ]
    for nombre, tipo_geom, desc in capas_vacias:
        conn.execute(f"""CREATE TABLE {nombre} (
            fid INTEGER PRIMARY KEY AUTOINCREMENT,
            geom BLOB, nombre TEXT, descripcion TEXT
        )""")
        reg_capa(nombre, tipo_geom, desc)

    conn.commit()
    conn.close()
    print(f"  ✓ {ruta}")


def escribir_qgz(coords, ruta_gpkg, ruta_qgz):
    gpkg_rel = os.path.basename(ruta_gpkg)
    all_N = [coords[i][0] for i in range(1, 9)]
    all_E = [coords[i][1] for i in range(1, 9)]
    cx = (min(all_E) + max(all_E)) / 2
    cy = (min(all_N) + max(all_N)) / 2
    dx = (max(all_E) - min(all_E)) * 2.0
    dy = (max(all_N) - min(all_N)) * 2.0

    capas = [
        ('boundary',   'POLYGON',    '1'),
        ('vertices',   'POINT',      '1'),
        ('zones',      'POLYGON',    '1'),
        ('structures', 'POLYGON',    '1'),
        ('trees',      'POINT',      '1'),
        ('water',      'LINESTRING', '1'),
        ('trails',     'LINESTRING', '1'),
        ('photos',     'POINT',      '1'),
    ]

    capas_xml = ""
    for nombre, geom, visible in capas:
        lid = f"casagenerativa_{nombre}"
        capas_xml += f"""
      <maplayer type="vector" autoRefreshEnabled="0">
        <id>{lid}</id>
        <datasource>./{gpkg_rel}|layername={nombre}</datasource>
        <layername>{nombre}</layername>
        <srs><spatialrefsys><authid>EPSG:5367</authid></spatialrefsys></srs>
        <provider encoding="UTF-8">ogr</provider>
      </maplayer>"""

    qgs = f"""<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.28.0" projectname="Casa Generativa">
  <title>Casa Generativa</title>
  <projectCrs>
    <spatialrefsys>
      <authid>EPSG:5367</authid>
      <description>CRTM05</description>
    </spatialrefsys>
  </projectCrs>
  <mapcanvas>
    <units>meters</units>
    <extent>
      <xmin>{cx - dx/2:.4f}</xmin>
      <ymin>{cy - dy/2:.4f}</ymin>
      <xmax>{cx + dx/2:.4f}</xmax>
      <ymax>{cy + dy/2:.4f}</ymax>
    </extent>
    <destinationsrs>
      <spatialrefsys><authid>EPSG:5367</authid></spatialrefsys>
    </destinationsrs>
  </mapcanvas>
  <projectlayers>{capas_xml}
  </projectlayers>
</qgis>"""

    with zipfile.ZipFile(ruta_qgz, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('proyecto.qgs', qgs)
    print(f"  ✓ {ruta_qgz}")


def escribir_doc(coords, reportes, ruta):
    area_calc = area_shoelace([coords[i] for i in range(1, 9)])
    hoy = datetime.now().strftime('%Y-%m-%d')

    filas_control = "\n".join(
        f"| {pt} | {N:.4f} | {E:.4f} | Plano topográfico |"
        for pt, (N, E) in CONTROL.items()
    )
    filas_vertices = "\n".join(
        f"| {pt} | {coords[pt][0]:.4f} | {coords[pt][1]:.4f} | "
        f"{'conocido' if pt in CONTROL else 'calculado (ajustado)'} |"
        for pt in range(1, 9)
    )

    secciones_cierre = ""
    for r in reportes:
        advertencia = ""
        if r['cierre_m'] > 0.3:
            advertencia = (
                f"\n> **Advertencia:** El error de cierre ({r['cierre_m']:.4f} m) supera los "
                f"límites típicos de tolerancia topográfica (1:5000 o ~0.03 m para este tramo). "
                f"Se recomienda verificar los datos originales del plano.\n"
            )
        secciones_cierre += f"""
### Tramo {r['nombre']}

| Métrica | Valor |
|---------|------:|
| Error ΔN | {r['err_N']:+.4f} m |
| Error ΔE | {r['err_E']:+.4f} m |
| Cierre lineal | {r['cierre_m']:.4f} m |
| Longitud del tramo | {r['total_m']:.2f} m |
| Precisión relativa | 1:{r['precision']:.0f} |
{advertencia}
"""

    doc = f"""# GIS — Componente Espacial

**Nivel de madurez:** 3 — Medido
**Última actualización:** {hoy}

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
{filas_control}

---

## Poligonal Reconstruida

| Punto | Norte | Este | Tipo |
|-------|------:|-----:|------|
{filas_vertices}

---

## Error de Cierre por Tramo
{secciones_cierre}
---

## Área

| | Valor |
|---|------:|
| Área según plano | {AREA_PLANO:.2f} m² |
| Área calculada (Gauss/Shoelace) | {area_calc:.2f} m² |
| Diferencia | {area_calc - AREA_PLANO:+.2f} m² |

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
"""

    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(doc)
    print(f"  ✓ {ruta}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("Casa Generativa — Reconstrucción GIS")
    print("=" * 60)

    os.makedirs('gis', exist_ok=True)
    os.makedirs('docs', exist_ok=True)

    print("\n>>> Ajuste Bowditch por tramos:")
    reportes = []
    adj_all = {}

    for nombre, (segs, inicio, fin) in TRAMOS.items():
        adj, reporte = ajuste_bowditch(segs, inicio, fin, nombre)
        adj_all.update(adj)
        reportes.append(reporte)

    # Coordenadas finales: control exacto, calculados ajustados
    coords = {}
    for pt in range(1, 9):
        coords[pt] = CONTROL[pt] if pt in CONTROL else adj_all[pt]

    area_calc = area_shoelace([coords[i] for i in range(1, 9)])
    print(f"\n>>> Área calculada: {area_calc:.2f} m²  (plano: {AREA_PLANO:.2f} m²)")

    print("\n>>> Generando archivos:")
    escribir_csv(coords, 'gis/vertices.csv')
    escribir_geojson(coords, 'gis/limite.geojson')
    escribir_kml(coords, 'gis/limite.kml')
    escribir_gpkg(coords, 'gis/casa_generativa.gpkg')
    escribir_qgz(coords, 'gis/casa_generativa.gpkg', 'gis/proyecto_qgis.qgz')
    escribir_doc(coords, reportes, 'docs/gis.md')

    print("\n>>> Archivos generados:")
    for f in sorted(os.listdir('gis')):
        size = os.path.getsize(f'gis/{f}')
        print(f"  gis/{f:40s} {size:>8,d} bytes")
    print(f"  docs/gis.md")
    print("\n¡Reconstrucción completada!")


if __name__ == '__main__':
    main()
