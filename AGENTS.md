# AGENTS.md — F1Analisys

Guía operativa para agentes Claude que trabajen en este repositorio. Lee este fichero antes de tocar código.

---

## 1. Qué es este proyecto

**F1Analisys** es una API REST (FastAPI + Uvicorn) que genera gráficos de análisis de la Fórmula 1 a partir de los datos abiertos de [FastF1](https://docs.fastf1.dev/). Cada endpoint produce una imagen PNG (matplotlib / seaborn) que se devuelve como:

- redirección a la imagen estática servida en `/temp/...` (por defecto),
- string base64 (`?convert_to_bytes=True`),
- URL absoluta (`?get_url=True`).

Se despliega como contenedor Docker en Dokploy mediante GitHub Actions (push a `master` → build & push a GHCR → trigger Dokploy).

**Stack:**

- Python 3.11 (Docker base: `python:3.11-slim`).
- FastAPI + Uvicorn (ASGI).
- `fastf1` (datos), `pandas`/`numpy` (procesado), `matplotlib`/`seaborn`/`scipy` (gráficos), `pillow` (creación del PNG placeholder), `pyjwt` (auth).

---

## 2. Layout

```
F1Analisys/
├── Dockerfile                      # base 3.11-slim, EXPOSE 8000
├── requirements.txt                # SIN versiones pinneadas
├── .github/workflows/deploy.yaml   # CI/CD → GHCR → Dokploy
├── img/                            # banners del README
└── app/
    ├── main.py                     # punto de entrada FastAPI
    ├── temp/                       # cache de PNGs (servido en /temp)
    ├── api/
    │   ├── api_router.py           # router raíz, monta /analisys y /system
    │   ├── analisys_routes.py      # 13 endpoints de análisis
    │   └── system_routes.py        # /health y DELETE /temp/remove
    ├── auth/
    │   └── dependencies.py         # verify_token() vía pyjwt
    ├── middleware/
    │   ├── auth_middleware.py      # Bearer JWT solo para /system/*
    │   └── check_analisys_middleware.py  # cache-hit en /temp si existe el PNG
    ├── utils/
    │   ├── utils.py                # format_time_mmssmmm, send_error_message
    │   ├── fastf1_utils.py         # get_session, try_get_session_laps, get_delta_time, get_request_data
    │   ├── path_utils.py           # get_path_temp_plot, get_info_drivers, exists_plot_in_temp
    │   ├── image_utils.py          # save_img, convert_img_to_bytes, get_return
    │   └── files_utils.py          # gestión del directorio temp/ (limpieza, límite 25 ficheros)
    └── analisys/                   # 13 módulos, uno por análisis
        ├── top_speed_analisys.py
        ├── track_dominance_analisys.py
        ├── lap_time_average_analisys.py
        ├── lap_time_distribution_analisys.py
        ├── team_performace_analisys.py        (sic — "performace")
        ├── fastest_laps_analisys.py
        ├── fastest_drivers_compound_analisys.py
        ├── race_position_evolution_analisys.py
        ├── comparative_lap_time_analisys.py
        ├── braking_analisys.py
        ├── throttle_analisys.py
        ├── long_runs_analisys.py
        └── optimal_lap_impact_analisys.py
```

---

## 3. Flujo de una petición

Antes de nada, al importar `app.main` se carga `python-dotenv` con el fichero indicado por `ENV_FILE` (default `.env`). Las variables clave (`TEMP_PATH_DIRECTORY`, `SECRET_KEY`, `ALGORITHM`, `ID_PAYLOAD_JWT`, `SUB_PAYLOAD_JWT`) tienen que existir o el proceso falla en arranque (mount) o en la primera petición autenticada (JWT).

```
GET /api/analisys/official/top_speed/2024/10/Q
│
├─ AuthMiddleware           (registrado el último → ejecuta primero)
│    if path.startswith("/api/analisys/"): is_analisys=True; pass-through
│    elif path.startswith("/api/system/"): exige Bearer JWT
│    else:                                pass-through  (docs, /temp, /, etc.)
│
├─ CheckAnalisysMiddleware  (cache-hit por path)
│    extrae (type_event, analisys, year, event, session) de la URL,
│    construye ./temp/plot_{type_event}_{analisys}_{year}_{event}_{session}.png,
│    si existe → FileResponse(media_type="image/png"). Fin.
│
├─ Router /api/analisys/{type_event}/{análisis}/{year}/{event}/{session}
│    llama a la función <analisis>_analisys(...)
│    el módulo construye la figura con matplotlib (estado global plt)
│
└─ get_return(request, convert_to_bytes, get_url)
     save_img(file_path)             # plt.savefig + plt.close → guarda en ./temp/
     if convert_to_bytes: convert_img_to_bytes()
     elif get_url:        {"url": request.url_for("temp", path=...)}
     else:                RedirectResponse(url=file_path[1:])
```

**Importante**: `app.main.app` se ejecuta con `cwd = /app` (Dockerfile `WORKDIR /app`). El layout dentro del contenedor es `/app/app/main.py`. El mount estático ahora toma la ruta de `TEMP_PATH_DIRECTORY` (env var), pero `path_utils.get_path_temp_plot` y `files_utils.*` siguen hardcoded a `./temp/...`. Ver `KNOWN_ISSUES.md` → KI#1.

---

## 4. Endpoints

Todos viven bajo `/api`. Tipos de evento: `official` (carreras del calendario oficial) o `pretest` (pretemporada).

| Path | Sesiones válidas |
|------|------------------|
| `/api/analisys/{type_event}/top_speed/{year}/{event}/{session}` | FP1-3, Q, S, SS, SQ, R |
| `/api/analisys/{type_event}/braking/{year}/{event}/{session}` | idem |
| `/api/analisys/{type_event}/throttle/{year}/{event}/{session}` | idem |
| `/api/analisys/{type_event}/lap_time_average/{year}/{event}/{session}` | idem |
| `/api/analisys/{type_event}/team_performace/{year}/{event}/{session}` | idem |
| `/api/analisys/official/lap_time_distribution/{year}/{event}/{session}` | solo official |
| `/api/analisys/{type_event}/fastest_laps/{year}/{event}/{session}` | idem |
| `/api/analisys/official/race_position_evolution/{year}/{event}/{session}` | solo `R` y `S` |
| `/api/analisys/{type_event}/fastest_drivers_compound/{year}/{event}/{session}` | idem |
| `/api/analisys/{type_event}/track_dominance/{year}/{event}/{session}[/compare/{pilotos_info:path}]` | acepta selección custom de vueltas |
| `/api/analisys/{type_event}/comparative_lap_time/{year}/{event}/{session}[/compare/{pilotos_info:path}]` | idem |
| `/api/analisys/{type_event}/long_runs/{year}/{event}/{session}/compare/{pilotos_info:path}` | requiere `pilotos_info`; params extra `indexing`, `threshold` |
| `/api/analisys/official/optimal_lap_impact/{year}/{event}/{session}` | solo `Q`, `SS`, `SQ` |
| `GET  /api/system/health` | health check |
| `DELETE /api/system/temp/remove` | **requiere JWT**: borra todo `./temp/` |

**Query params comunes**: `convert_to_bytes: bool = False`, `get_url: bool = False`.

**Formato `pilotos_info`** (en endpoints `/compare/...`): `VER/3/vs/NOR/5/vs/HAM/7` → `{"VER":[3], "NOR":[5], "HAM":[7]}`. Para `long_runs` se interpreta como rango: lista de dos enteros `[start, end]`.

---

## 5. Convenciones de código a respetar

- **Ortografía intencional**: `analisys` (no `analysis`), `team_performace` (no `team_performance`), `pilotos`, `vueltas`. Mantenlas o se rompen rutas y nombres de fichero en `./temp/`.
- **Idioma mixto**: docstrings y nombres públicos en inglés; comentarios y variables internas frecuentemente en español. Sigue el estilo del fichero que edites.
- Cada análisis vive en su propio fichero `app/analisys/<nombre>_analisys.py`, exporta una sola función pública `<nombre>_analisys(type_event, year, event, session, ...)` y la registra en `app/analisys/__init__.py`.
- **Las funciones de análisis no devuelven nada**: construyen una figura via `plt.subplots()` / pyplot y dejan la figura como `plt.gcf()`. `get_return` la captura. **No hacer `plt.close()` dentro del análisis** (lo hace `save_img`).
- Errores de dominio → `send_error_message(status_code, title, message)` que levanta `HTTPException`. No uses `raise HTTPException` directo dentro de los análisis.
- Para cargar sesiones: **siempre** `get_session(...)` + `try_get_session_laps(session)` desde `app/utils/fastf1_utils.py`. Ambas envuelven excepciones FastF1 en `HTTPException(404)`.

---

## 6. Bugs conocidos

Mantenidos en [`KNOWN_ISSUES.md`](./KNOWN_ISSUES.md). **Léelo antes de tocar código de análisis, caché o autenticación.** Cuando un issue se resuelva, muévelo a la sección _Resueltos_ con la fecha. Si quieres referenciar uno desde un commit/PR, usa el formato `KI#N`.

Estado a la última actualización: 18 abiertos, 4 resueltos.

---

## 7. Calidad / herramientas

**No hay tests** (`tests/` no existe). No hay configuración de `pyproject.toml`, `ruff`, `mypy`, `black`, `pytest`. Cualquier convención de la sección §5 hay que respetarla manualmente.

Recomendado al editar:

```powershell
python -m ruff check app/                 # 47 hallazgos hoy (F401 masivos en __init__, E701, F841)
python -m bandit -r app/                  # 2 hallazgos (B112, B104)
```

`ruff --fix` aplica automáticamente 9 de las 47. Tras tocar imports, re-correr.

**Si abres PR**: el workflow `deploy.yaml` solo se dispara con push a `master`. No corre tests, no corre lint. La rama está vacía de gates de calidad — el reviewer humano es el único guard.

---

## 8. Desarrollo local

### Variables de entorno

La app necesita estas vars al arrancar:

| Variable | Descripción |
|----------|-------------|
| `TEMP_PATH_DIRECTORY` | Ruta (relativa a cwd) donde se monta `/temp` y se cachean los PNG. En Windows `app\\temp`, en Linux/Docker `temp` (con `cwd=/app` se traduce a `/app/temp`). |
| `SECRET_KEY` | Clave para firmar/verificar JWT. |
| `ALGORITHM` | Algoritmo JWT, normalmente `HS256`. |
| `ID_PAYLOAD_JWT` | Valor esperado en el campo `id` del payload. |
| `SUB_PAYLOAD_JWT` | Valor esperado en el campo `sub` del payload. |
| `ENV_FILE` *(opcional)* | Path al fichero .env a cargar. Default: `.env`. |

`app/main.py` llama a `load_dotenv(os.getenv("ENV_FILE", ".env"))` antes de instanciar `FastAPI`. Si la var no existe, `python-dotenv` no falla — caen en silencio y luego `os.environ["..."]` lanza `KeyError`. Esto es deseado: fail-fast.

`.env.example` está en el repo como plantilla pública. **`.env` (y cualquier otro `.env*` que no sea `.env.example`) está en `.gitignore`** — no commitearlo.

### Arranque

```powershell
# --- Docker (producción-like) ---
docker build -t f1analisys:latest .
docker run -p 8000:8000 --env-file .env f1analisys:latest

# --- Sin Docker (iteración rápida) ---
python -m pip install -r requirements.txt
# .env se carga automáticamente al importar app.main
python -m uvicorn app.main:app --reload --port 8000

# Swagger en http://localhost:8000/docs
```

Si quieres usar otro fichero de configuración (`.env.staging`, etc.):

```powershell
$env:ENV_FILE=".env.staging"; python -m uvicorn app.main:app --reload --port 8000
```

En producción (Dokploy) no hay fichero `.env` — las env vars se inyectan desde el panel de Dokploy. `load_dotenv` no encuentra nada, no pasa nada, las vars ya están en `os.environ`.

Primer arranque: `fastf1` cachea descargas en `~/.fastf1` (o equivalente en Docker). Las primeras peticiones a una sesión nueva tardan ~30s.

---

## 9. Tareas frecuentes — receta

### Añadir un nuevo análisis

1. Crear `app/analisys/<nombre>_analisys.py` con una función `<nombre>_analisys(type_event:str, year:int, event:int, session:str, ...)` que use `get_session` + `try_get_session_laps` y deje la figura en `plt.gcf()`.
2. Exportarla en `app/analisys/__init__.py`.
3. Importarla en `app/api/analisys_routes.py` y registrar el endpoint con el patrón `/{type_event}/<nombre>/{year}/{event}/{session}`, llamando a la función y devolviendo `get_return(request, convert_to_bytes, get_url)`.
4. Si necesita parámetros extra (drivers, threshold...), añadirlos como query params con default; si dependen de selección de vueltas, parsearlas con `get_info_drivers`.
5. Actualizar el README con la fila correspondiente y el badge de sesiones válidas.

### Cambiar autenticación

`app/auth/dependencies.py` y `app/middleware/auth_middleware.py`. Las claves se leen con `os.environ["..."]` (fail-fast): **no introducir defaults hardcoded** ni `os.getenv` con valor real como fallback (regla `python/security.md`). Si necesitas una clave nueva, añádela como entrada en `.env.example` (placeholder) y en tu `.env` local (valor real, no commitear).

### Cambiar formato de salida de los gráficos

`app/utils/image_utils.py` (`save_img`, `convert_img_to_bytes`, `get_return`). Cuidado con el orden close/save (`KNOWN_ISSUES.md` → KI#2).

---

## 10. Política para agentes Claude

- **No hacer commit ni push automáticamente.** El owner es quien dispara CI/CD desde `master`. Pide confirmación antes de `git commit` o `git push`.
- **No corregir la ortografía intencional** (`analisys`, `performace`) salvo que el usuario lo pida explícitamente. Está en URLs públicas y en nombres de cache.
- **Antes de "limpiar" código aparentemente raro de los análisis**, comprueba si depende de la API de FastF1 (que cambia entre versiones). Lee `app/utils/fastf1_utils.py` primero.
- **No introducir nuevas dependencias** sin actualizar `requirements.txt` (sin versión pinned salvo necesidad — sigue el estilo actual).
- **Si tocas paths de la carpeta temp**, recuerda que el mount lee `TEMP_PATH_DIRECTORY` pero `path_utils.get_path_temp_plot` y `files_utils.*` siguen hardcoded. Hoy están desincronizados (`KNOWN_ISSUES.md` → KI#1).
- **Si tocas el middleware de cache**, asegúrate de que la clave incluye los parámetros que diferencian la salida (e.g. `pilotos_info` en `track_dominance`).
- **Nunca commitear `.env` ni ningún otro `.env*` salvo `.env.example`**. Está en `.gitignore`; si lo ves trackeado, hay un problema. Para añadir una clave nueva: entrada placeholder en `.env.example` (commiteado) + valor real en `.env` local (no commiteado) + uso con `os.environ["..."]` en código.

---

## 11. Referencias rápidas

- FastF1 docs: https://docs.fastf1.dev/
- Producción: https://f1analisys-production.up.railway.app/ (Swagger en `/`)
- Repo: https://github.com/Maxbleu/F1Analisys
- Despliegue: GHCR + Dokploy (workflow `.github/workflows/deploy.yaml`)
