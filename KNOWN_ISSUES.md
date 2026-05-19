# Known Issues — F1Analisys

Lista viva de bugs y deudas técnicas conocidos en el árbol de trabajo. Si tocas un área cercana a uno de estos, intenta arreglarlo en el mismo PR. Cuando un issue se resuelva, muévelo a la sección **Resueltos** con la fecha y el commit/PR de referencia.

Convención: los issues están numerados de forma estable (no renumerar al cerrar uno — solo tachar/mover). Eso permite que `AGENTS.md` y commits puedan referenciarlos por número (`KI#3`) sin que el enlace rote.

---

## Abiertos

### KI#2 — `get_return` + `convert_to_bytes` produce PNG en blanco

`save_img` (`app/utils/image_utils.py`) llama `plt.close()` después de guardar. Si el caller pide `convert_to_bytes=True`, `convert_img_to_bytes` hace `plt.savefig(io)` sobre `plt.gcf()`, que ahora es una figura nueva vacía.

**Fix**: invertir el orden — si `convert_to_bytes`, convertir primero (sobre la figura aún viva) y luego guardar; o no cerrar la figura hasta el final de `get_return`.

### KI#3 — Concurrencia matplotlib (data leak entre peticiones)

`pyplot` mantiene estado global. Dos peticiones simultáneas a `/api/analisys/...` comparten figura → un cliente puede recibir el gráfico de otro. Además, las rutas son `async def` pero las funciones de análisis son síncronas pesadas → bloquean el event loop.

**Mitigaciones (de menos a más invasivo)**:
1. `asyncio.Lock` global para serializar las peticiones de análisis. Resuelve el data leak, pero throughput = 1.
2. Cambiar rutas a `def` (FastAPI las corre en threadpool) + mantener el lock. Libera event loop pero throughput sigue ≈ 1.
3. **Refactor correcto**: usar `matplotlib.figure.Figure` directo (sin `pyplot`). Cada análisis devuelve su `fig`. `get_return` la recibe como parámetro. Rutas en `def`. Cero estado global. Mover `fastf1.plotting.setup_mpl(...)` a startup (`main.py`) — hoy se llama por petición.

**Bloqueante**: hay `plt.scatter`/`plt.gca`/`plt.vlines` sueltos en `race_position_evolution_analisys.py` y `comparative_lap_time_analisys.py` que hay que sustituir por `ax.scatter`/etc. Seaborn (`boxplot`/`violinplot`/`swarmplot`) acepta `ax=` explícito.

### KI#4 — Cache key del middleware no incluye `pilotos_info`

`track_dominance` y `comparative_lap_time` aceptan `/compare/{pilotos_info:path}` (e.g. `/compare/VER/3/vs/NOR/5`), pero `CheckAnalisysMiddleware` solo construye la clave con `(type_event, analisys, year, event, session)`. Dos comparativas distintas en la misma sesión colisionan: el segundo cliente recibe el gráfico del primero.

**Fix**: incluir un hash del segmento `pilotos_info` en el nombre del PNG, o normalizar y serializar el dict `vueltas_pilotos_dict` como sufijo del nombre.

### KI#5 — Inversiones telemétricas dudosas en `braking_analisys` / `throttle_analisys`

Ambos hacen:

```python
telemetry["Brake"]    = 1 - telemetry["Throttle"]   # Brake real es booleano en FastF1
telemetry["Throttle"] = 1 - telemetry["Brake"]      # Throttle real es 0–100
```

Los valores resultantes no son interpretables como % de uso real. Necesita revisión de dominio antes de "limpiar" — puede ser un artifact intencional. Si se confirma como bug, recalcular sobre `telemetry["Brake"]` (bool) y `telemetry["Throttle"]` (0-100) sin inversiones.

### KI#6 — `files_utils.is_temp_under_limits` usa comparación exacta

```python
return len(files) == 25
```

Si el contador se desincroniza (borrado externo, fallo a medias), el límite deja de aplicarse jamás. Cambiar a `>= 25`.

### KI#7 — `files_utils.delete_first_plot` no es FIFO determinista

Usa `os.listdir()[0]`, que no garantiza orden. El "primer" plot borrado es arbitrario, no el más antiguo.

**Fix**: `min(files, key=os.path.getmtime)` si la intención es FIFO por edad.

### KI#8 — `get_request_data` rompe con paths cortos

`app/utils/fastf1_utils.py:67-69` indexa `path_parts[3..7]` sin validar longitud. Está envuelto en try/except dentro de `CheckAnalisysMiddleware`, así que no propaga, pero ensucia logs y oculta bugs reales (`IndexError: list index out of range`).

**Fix**: validar `len(path_parts) >= 8` antes de indexar, y si no, retornar `None` o un sentinel para que el middleware salte la lógica de caché limpiamente.

### KI#9 — Dependencias transitivas no declaradas

- `scipy` se usa en `long_runs_analisys.py` (`scipy.interpolate.make_interp_spline`).
- `timple` se usa en `fastest_laps_analisys.py` y `fastest_drivers_compound_analisys.py` (`timple.timedelta.strftimedelta`).

Funcionan porque `fastf1` las arrastra como deps transitivas. Si `fastf1` cambia sus deps, se rompe el arranque. Pinear explícitamente en `requirements.txt`.

### KI#10 — `requirements.txt` sin versiones pinneadas

Reproducibilidad nula entre builds. `fastf1` rompe API entre versiones menores y `pandas`/`matplotlib` también. Mínimo fijar `fastf1==X.Y` y `pandas==X.Y`.

### KI#11 — Cero tests

No hay `tests/`, ni `pyproject.toml`, ni configuración de `pytest`/`ruff`/`black`/`mypy`. Smoke tests mínimos a añadir: `get_info_drivers`, `format_time_mmssmmm`, `get_path_temp_plot`, y un test del router `/api/system/health`.

### KI#12 — `SettingWithCopyWarning` latentes en varios análisis

- `top_speed_analisys.py:22-23`: `df_top_speeds = laps[["Driver","Team"]]` → `df_top_speeds["TopSpeed"] = 0`.
- `race_position_evolution_analisys.py:142`: `laps_in_period["LapNumber"] = ...`.
- `fastest_drivers_compound_analisys.py:35`: `compound_laps["TotalLaps"] = ...`.

Falla silenciosamente con pandas 2.x cuando el modo `copy_on_write` está activo. Encadenar `.copy()` o usar `.loc[...]`.

### KI#13 — `print()` en lugar de `logging` en analizadores telemétricos

`braking_analisys.py:33-34` y `throttle_analisys.py:33-34` usan `print(...)` dentro de `except Exception`. Migrar a `logger = logging.getLogger(__name__); logger.exception(...)`.

### KI#14 — Excepciones tragadas sin contexto

- `race_position_evolution_analisys.py:83-84`: `except Exception as e: ...` (no-op).
- `race_position_evolution_analisys.py:109-110`: `except Exception as e: continue` (detectado por bandit B112).

Oculta bugs reales. Al menos `logger.warning(...)` o re-raise selectivo.

### KI#15 — `uvicorn.run(host="0.0.0.0")` hardcoded

`app/main.py:21` (`if __name__ == "__main__"`) bindea a todas las interfaces sin posibilidad de override. Detectado por bandit B104. Aceptable en contenedor, pero conviene parametrizar (`os.getenv("HOST", "0.0.0.0")`).

### KI#16 — `DELETE /api/system/temp/remove` sin rate-limit ni soft-delete

Un token comprometido vacía todo el caché de un solo golpe. Considerar:
- Rate-limit por IP/token.
- Scope JWT específico para operaciones destructivas.
- Confirmación obligatoria (query param `?confirm=true`).

### KI#17 — Type hints ausentes en utils

Funciones públicas en `app/utils/utils.py` (`format_time_mmssmmm`, `send_error_message`), `fastf1_utils.py` (`get_team_colors`, `get_session`, `try_get_session_laps`) sin anotaciones. La regla `python/coding-style.md` las exige.

### KI#18 — Imports no usados / orden roto

47 hallazgos de `ruff` hoy:
- `F401` masivos en `app/*/__init__.py` (re-exports sin `__all__`).
- `E401`: imports múltiples en una línea (`app/utils/fastf1_utils.py:3`, `app/utils/image_utils.py:6`).
- `E701`: statements en una sola línea con `:`.
- `F841`: variables `e` capturadas y nunca usadas.

`ruff --fix` aplica 9 de los 47 automáticamente.

---

## Resueltos

| Fecha | Issue | Notas |
|---|---|---|
| 2026-05-19 | Secretos hardcoded en `app/auth/dependencies.py` | Migrado a `os.environ["..."]` fail-fast. Valores cargados desde `.env` (local, en `.gitignore`) o entorno del contenedor (prod). |
| 2026-05-19 | Mount estático con backslash literal (`directory="app\\temp"`) | Ahora `directory=os.environ["TEMP_PATH_DIRECTORY"]`, válido en Windows y Linux. |
| 2026-05-19 | Bypass de auth por substring (`"analisys" in path`) | Ahora `request.url.path.startswith("/api/analisys/")`. |
| 2026-05-19 | Segundo check del middleware con prefijo equivocado (`/system/` invertido) | Ahora `if not path.startswith("/api/system/"): pass-through`. Validado con TestClient: `/docs` → 200, `/api/system/*` sin token → 401, `/api/analisys/*` → bypass. |
| 2026-05-19 | KI#1 — Inconsistencia de rutas de caché entre escritura y servido | `path_utils.get_path_temp_plot` y `files_utils.delete_first_plot` ahora leen `TEMP_PATH_DIRECTORY` vía `os.path.join`. `image_utils` usa `os.path.basename(file_path)` y construye la URL de redirect explícita (`/temp/<file>`). Validado en local con cache miss + hit. |
