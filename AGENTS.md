# Gestión del Conocimiento

Casa Generativa es un proyecto de investigación y desarrollo de largo plazo.

El repositorio constituye la memoria oficial del proyecto. Las conversaciones con el usuario son únicamente una fuente de información; el conocimiento permanente debe incorporarse a la documentación correspondiente.

## Principio General

Al finalizar cada sesión de trabajo, el agente deberá:

1. Identificar el conocimiento nuevo generado.
2. Clasificarlo por dominio.
3. Actualizar el documento correspondiente.
4. Crear nuevos documentos cuando aparezcan nuevos dominios.
5. Registrar las decisiones relevantes.
6. Registrar el avance del proyecto.

Nunca deberá dejar conocimiento importante únicamente en la conversación.

---

# Modelo de Madurez del Conocimiento

Cada documento temático deberá comenzar con un nivel de madurez.

Los niveles representan la calidad y confiabilidad del conocimiento acumulado.

## Nivel 0 — No documentado

No existe información.

Solo existe la intención de estudiar ese tema.

Ejemplo:

- Energía
- Biodiversidad
- Manejo de aguas

---

## Nivel 1 — Hipótesis

Existe información preliminar.

Proviene de observaciones, recuerdos o conversaciones.

Todavía no existe evidencia suficiente.

Ejemplos:

- "Existe un pozo."
- "Hay una quebrada."
- "Existe un bambusal."

---

## Nivel 2 — Observado

La existencia fue confirmada.

Existen fotografías, visitas de campo o inspecciones.

Todavía no existen mediciones completas.

Ejemplos:

- Se fotografió el pozo.
- Se identificó el recorrido de la quebrada.
- Se confirmó la especie dominante del bambú.

---

## Nivel 3 — Medido

Ya existen datos cuantitativos.

Ejemplos:

- Coordenadas GIS.
- Dimensiones.
- Inventarios.
- Caudales.
- Alturas.
- Cantidades.
- Levantamientos topográficos.

En este nivel el conocimiento puede utilizarse para análisis.

---

## Nivel 4 — Validado

Los datos fueron revisados y comprobados.

Ejemplos:

- Validación por especialista.
- Comparación con estudios técnicos.
- Ensayos de laboratorio.
- Verificación en múltiples visitas.

La información puede utilizarse como referencia oficial del proyecto.

---

## Nivel 5 — Operativo

El conocimiento ya forma parte del funcionamiento normal del proyecto.

Existe mantenimiento y actualización continua.

Ejemplos:

- Inventario GIS completo.
- Sistema de captación de agua documentado.
- Manual de mantenimiento.
- Procedimientos operativos.

---

# Evolución del Conocimiento

El agente deberá intentar aumentar gradualmente el nivel de madurez de cada dominio.

Nunca disminuirá un nivel sin registrar la razón.

Cuando una nueva información permita avanzar un nivel:

- actualizar el documento;
- registrar la fecha;
- describir qué permitió el cambio.

---

# Organización por Dominios

Cada dominio tendrá un documento independiente.

Ejemplos:

docs/

- water.md
- vegetation.md
- soils.md
- biodiversity.md
- materials.md
- construction.md
- energy.md
- gis.md
- digital_twin.md
- automation.md

Si durante una sesión aparece un nuevo dominio que no existe:

1. Crear automáticamente el documento.
2. Agregarlo al índice del proyecto.
3. Inicializarlo en Nivel 0.
4. Incorporar el conocimiento obtenido durante la sesión.

---

# Actualización Automática

Al finalizar cada sesión el agente deberá revisar:

- PROJECT.md
- DECISIONS.md
- CHANGELOG.md
- docs/*.md afectados

Si hubo información nueva:

- actualizar el documento correspondiente;
- evitar duplicar información;
- conservar el historial de decisiones;
- mantener enlaces cruzados entre documentos relacionados.

El objetivo es que el repositorio represente siempre el estado más actualizado del conocimiento del proyecto.
