# ROADMAP — F1Analisys

Trabajo planificado y en backlog para la API. Refleja los **12 issues abiertos** en GitHub Issues a fecha **2026-05-19**.

> Esta es la lista de **funcionalidades** y **modificaciones planeadas** (label `enhancement` casi en todos). Para la lista de **bugs / deuda técnica** ya identificados en el código, ver [`KNOWN_ISSUES.md`](./KNOWN_ISSUES.md).
>
> Fuente única de verdad: GitHub Issues. Este fichero es una vista sincronizada manualmente — cuando un issue se cierre, mueve la entrada a la sección _Hecho_ con la fecha y el PR/commit.

---

## Convenciones de los títulos

- `ADD:` → nuevo análisis o endpoint.
- `MDF:` → modificación de un análisis o comportamiento ya existente.

Para referenciar un issue desde un commit/PR, usar `#N` (formato nativo GitHub) — distinto de `KI#N` (usado en `KNOWN_ISSUES.md`).

---

## 1. Nuevos análisis (gráficos)

### #28 — ADD: plot to compare degradation of stint drivers
- **Label:** enhancement
- **Resumen:** El usuario elige métricas y pilotos; el gráfico muestra cuánto se ha degradado el rendimiento dentro del stint.
- **Notas para implementar:** seguramente reutilizable la pipeline de `long_runs_analisys` para detectar y agrupar stints. Falta definir qué métrica concreta refleja "degradación" (tiempos por vuelta normalizados, sector más afectado, dispersión vs. media).

### #32 — ADD: plot comparative average time each driver in each sector
- **Label:** enhancement
- **Resumen:** En una única figura, tres subplots — uno por sector — con la media de tiempos de cada piloto en ese sector, para un compuesto concreto.
- **Notas:** subplot horizontal `1×3`, eje Y categórico (pilotos), barras horizontales o swarm. Filtrar por compuesto en query param. Probablemente se apoye en `laps[["Sector1Time","Sector2Time","Sector3Time","Compound"]]`.

### #33 — ADD: plot to compare consistensy in one stint to specific compound
- **Label:** enhancement
- **Body:** vacío (solo imagen de referencia adjunta en GitHub).
- **Notas:** "consistencia" → métrica natural es desviación estándar (o IQR) de los tiempos de vuelta dentro del stint, filtrando por compuesto. Una entrada por piloto.

### #34 — ADD: plot fastest drivers pit stops
- **Label:** enhancement
- **Body:** vacío (solo imagen de referencia adjunta).
- **Notas:** FastF1 no expone duración de pit stop como columna nativa — toca derivarlo (diff entre `PitInTime` y `PitOutTime`, o de la diferencia de tiempo de la vuelta de entrada vs. la vuelta normal). Aquí cuidado con datos faltantes en sesiones sin reportes oficiales.

### #35 — ADD: plot to compare fuel amount some drivers along of race or sprints
- **Label:** enhancement
- **Body:** _"Fuel amount will be calculated throught stimations or IA. I don't have a exactly idea of plot, when I go to develop, I will design a prototype."_
- **Notas:** FastF1 **no** expone combustible. Toca estimación (ej. tasa de consumo media × distancia recorrida, restada al peso inicial). Antes de codificar nada, fijar el modelo de estimación; documentarlo en docstring para que sea reproducible. Solo aplica a `R` y `S`.

### #36 — ADD: plot to compare performace battery energy along of sessions
- **Label:** enhancement
- **Body:** _"Battery energy will be calculated throght stimations or IA. I don't have a exactly idea of plot, when I go to develop, I will design a prototype."_
- **Notas:** mismo problema que #35 — FastF1 no expone batería. Posible proxy: throttle aplicado en zonas de aceleración + delta de velocidad. Documentar supuestos.

---

## 2. Modificación de análisis existentes

### #27 — MDF: modify track dominance
- **Label:** enhancement
- **Body:**
  > This modification is based in search the defenetly simility to track dominance of others tools.
  > - Understand the problem
  > - Fix it
  > - Check the comparatives are similar to others tools
- **Notas:** comparar la salida actual de `track_dominance_analisys.py` con herramientas referencia (F1Tempo, FastF1 examples). Probablemente afecta a la segmentación de microsectores (¿cada cuántos metros?) y al criterio de "ganador" del microsector.
- **Relacionado:** `KNOWN_ISSUES.md` → KI#4 (cache key no incluye `pilotos_info` — afecta a este endpoint).

### #31 — MDF: modify long runs plot
- **Label:** enhancement
- **Body:**
  > Display the driver's lap time points filled with the color corresponding to the tire compound used in those laps. Provide the option to compare them on the right X-axis with some features:
  > - Temperature
  > - Humidity
  > - Wind
- **Notas:** dos cambios independientes — colorear puntos por compuesto (ya hay paleta en `fastf1.plotting`), y añadir eje secundario opcional con datos meteorológicos (que vienen en `session.weather_data`). Los tres features (temp/hum/wind) deberían ir como query param opcional (`weather_overlay=temperature`).

---

## 3. UX / formato común a todos los gráficos

### #30 — MDF: change title plots
- **Label:** enhancement
- **Body:** _"We need to change tytle plots and put this format `year` `Session` `Country` Grand Prix"_
- **Notas:** afecta a **los 13 análisis**. Mejor introducir un helper `build_plot_title(year, session, event_name)` en `app/utils/utils.py` y llamarlo desde cada `<x>_analisys.py`. Aprovechar para revisar fontsize/posición y dejarlo centralizado.

---

## 4. Robustez / validación de la API

### #26 — MDF: Validate Data Types and Structure in /compare Routes with Representative Messages
- **Label:** ninguna
- **Body:** _"We need to ensure that the data type is correctly validated whenever data modifications are required. Additionally, we should check that the structure is correctly written in routes using /compare, displaying a representative message if any discrepancies are found."_
- **Notas:** afecta a `track_dominance`, `comparative_lap_time` y `long_runs` (los tres que aceptan `/compare/{pilotos_info:path}`). Actualmente `get_info_drivers` parsea el path sin schema explícito; si el cliente envía `VER/3/vs/NOR` (sin segunda vuelta), revienta tarde. Solución: validar shape de `pilotos_info` antes de cualquier I/O de FastF1 y devolver `400` con mensaje claro (vía `send_error_message`).
- **Relacionado:** `KNOWN_ISSUES.md` → KI#8 (`get_request_data` rompe con paths cortos — patrón paralelo).

### #25 — ADD: new endpoint not found
- **Label:** enhancement
- **Body:** vacío.
- **Notas:** el título ambiguo sugiere dos lecturas posibles: (a) "añadir un endpoint que devuelva 404 representativo cuando el recurso no existe" — handler global de 404; o (b) "añadir un endpoint que aún no he documentado y se llama _not found_". Pedir contexto al owner antes de empezar.

---

## 5. Off-topic / pendiente de aclarar

### #38 — ADD: Put the name of workspace pluss number how conversation's name
- **Label:** ninguna
- **Body:** vacío.
- **Notas:** el título no encaja con la API de F1Analisys (habla de "workspace" y "conversation"). Coherente con los issues cerrados #37–#48 que también van de chat/workspaces — parece que el repo se usó/se usa para otro proyecto. **Acción:** verificar si pertenece aquí o debería migrar a otro repositorio, y cerrarlo en su caso.

---

## Resumen

| Categoría | Issues abiertos |
|---|---|
| Nuevos análisis (`ADD:`) | #28, #32, #33, #34, #35, #36 — **6** |
| Modificaciones de análisis (`MDF:`) | #27, #31 — **2** |
| UX común a gráficos | #30 — **1** |
| Robustez de API | #26, #25 — **2** |
| Off-topic / a aclarar | #38 — **1** |
| **Total abiertos** | **12** |

Bloqueantes conocidos para empezar nuevos análisis: ver `KNOWN_ISSUES.md` → KI#3 (estado global de matplotlib en rutas async) — todo análisis nuevo nace ya con ese bug si no se refactoriza primero.

---

## Hecho

Issues cerrados: ver GitHub Issues (filtro `is:closed`). Cuando muevas algo aquí, formato:

| Fecha | Issue | PR/Commit | Notas |
|---|---|---|---|
| _yyyy-mm-dd_ | #N | `commit-sha` | breve descripción del cierre |
