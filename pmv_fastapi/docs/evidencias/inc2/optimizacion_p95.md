# Optimización de la latencia p95 (acción 1 del ciclo PDCA del Incremento 2)

**Qué se mejoró.** El listado de seguimiento (`GET /api/ninos`) y las alertas (`GET /api/alertas/controles-vencidos`, `GET /api/alertas/resumen`) recorren a todos los niños activos y calculan la agenda de cada uno (ADR-007). Con la versión `v1.5.0-inc2-avance` ese recorrido costaba entre 114 y 170 ms (p50) con 1 000 niños. La optimización reduce el costo de cargar los niños y de sumar meses sin cambiar ninguna regla.

## Qué cambió en el código

1. **Carga de niños por Core, en tres consultas** (`RepositorioSQLAlchemy._cargar`, `app/adapters/outbound/persistence/sqlalchemy_repo.py`). Antes se cargaban entidades ORM (con `selectinload` de las evaluaciones) y luego se copiaban al dominio. Ahora se ejecutan tres `SELECT` con las tablas de Core (niños, evaluaciones y asistencias, estas dos con `JOIN` al filtro de niños) y las filas se convierten directamente en objetos de dominio. Sigue sin haber N+1 (ADR-006). La escritura sigue usando el ORM.
2. **`agregar_meses` sin `calendar.monthrange`** (`app/domain/service/agenda.py`): tabla de días por mes y `calendar.isleap` solo para febrero. Se llama unas 13 400 veces en cada consulta de alertas con 1 000 niños (cProfile: 133 650 llamadas en 10 consultas). Su equivalencia con la versión anterior se verifica día por día entre 1999 y 2031 (CP-187).

El resto del tiempo es la propia función pura `generar_agenda` (≈ 70 % del tiempo de una consulta de alertas en el perfil); no se tocó para no alterar las reglas de ADR-007.

## Método

- Herramienta: `python -m tests.rendimiento.micro_benchmark --ninos 1000 --repeticiones 40` (nuevo, en `tests/rendimiento/`). Crea una base SQLite temporal con 1 000 niños sintéticos (semilla 2026, fecha fija 28-09-2026, 1 714 controles vencidos), pide cada endpoint 40 veces con `TestClient` (en proceso, sin red) y calcula p50 y p95.
- Comparación **en la misma máquina y en la misma sesión**: la versión «antes» es el código de `HEAD` (`v1.5.0-inc2-avance`) exportado con `git archive` a un directorio temporal; la versión «después» es el árbol de trabajo de la `v2.0.0-inc2`. Tres corridas intercaladas de cada una.
- Advertencia: la versión «después» hace más trabajo que la «antes» (consulta además las asistencias y carga las columnas nuevas), de modo que la mejora es neta. Es una medida en proceso y con SQLite: sirve para comparar versiones, no reemplaza la prueba de carga con Locust ni la de PostgreSQL.

## Resultados (ms, 1 000 niños, 40 repeticiones por corrida)

| Endpoint | Métrica | Antes (corridas 1 / 2 / 3) | Mediana antes | Después (corridas 1 / 2 / 3) | Mediana después | Mejora |
|---|---|---|---|---|---|---|
| `GET /api/ninos` | p50 | 128,5 / 117,2 / 124,5 | 124,5 | 97,7 / 98,6 / 99,3 | 98,6 | −20,8 % |
| `GET /api/ninos` | p95 | 173,8 / 149,8 / 159,6 | 159,6 | 122,4 / 133,3 / 128,2 | 128,2 | −19,7 % |
| `GET /api/alertas/controles-vencidos` | p50 | 137,7 / 136,6 / 169,5 | 137,7 | 113,7 / 124,1 / 121,8 | 121,8 | −11,5 % |
| `GET /api/alertas/controles-vencidos` | p95 | 177,1 / 185,7 / 274,9 | 185,7 | 144,5 / 160,0 / 155,3 | 155,3 | −16,4 % |
| `GET /api/alertas/resumen` | p50 | 113,9 / 120,1 / 123,7 | 120,1 | 100,0 / 105,2 / 94,8 | 100,0 | −16,7 % |
| `GET /api/alertas/resumen` | p95 | 147,3 / 205,7 / 162,8 | 162,8 | 142,9 / 141,8 / 121,9 | 141,8 | −12,9 % |

Otras tres corridas de la versión anterior hechas antes de empezar a optimizar dieron p95 de 178,1 / 172,9 / 200,9 ms (`/api/ninos`), 200,1 / 180,6 / 185,3 ms (alertas) y 151,4 / 164,0 / 158,9 ms (resumen), consistentes con la tabla. La dispersión entre corridas es de ±15 % (la máquina es compartida): una mejora de 12 a 21 % en la mediana es real pero modesta; no debe presentarse como una reducción de órdenes de magnitud.

## Tiempos con el dataset DIRESA Junín (SQLite, fecha de referencia 30-06-2024)

Siete solicitudes por ruta, `TestClient`, mismo equipo. «Muestra» = base de la demo (`--muestra 500`, 500 niños); «Completo» = `--completo` (11 686 niños, 29 712 evaluaciones).

| Ruta | Muestra (500 niños), mediana | Completo (11 686 niños), mediana | Tamaño de la respuesta (completo) |
|---|---|---|---|
| `GET /api/ninos` | 69 ms | 1 678 ms | 4,5 MiB |
| `GET /api/agenda` (semana de referencia) | 68 ms | 1 582 ms | 553 KiB |
| `GET /api/agenda?desde=2024-06-01&hasta=2024-06-30` | 78 ms | 1 678 ms | 2,5 MiB |
| `GET /api/alertas/controles-vencidos` | 89 ms | 2 452 ms | 22,2 MiB |
| `GET /api/alertas/resumen` | 75 ms | 1 676 ms | < 1 KiB |

Conclusión: con la base de la demo todo responde en menos de 0,1 s; con el dataset completo la agenda del personal cumple el criterio de 2 s (≈ 1,6 s) pero las alertas lo superan (2,5 s con 22 MiB de respuesta, sin paginar). El dataset completo (11 686 niños) es casi seis veces el criterio de revisión de ADR-007 (2 000 niños activos): para esa escala hay que materializar la agenda o paginar las alertas. Queda como limitación documentada.

## Reproducir

```bash
python -m tests.rendimiento.micro_benchmark --ninos 1000 --repeticiones 40
```
