# Verificación reproducida (S6-08) — 2026-10-01

Entorno: Windows 11, Python 3.14.6 (venv pmv_fastapi/.venv), SQLite (sin Docker), dependencias de requirements-dev.txt.
Comando de pruebas: pytest --cov=app --cov-report=term-missing (testpaths: tests/unitarias + tests/integracion)

## ruff
```
Python 3.14.6
All checks passed!
33 files already formatted
```

## pytest

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: pmv_fastapi
configfile: pyproject.toml
testpaths: tests/unitarias, tests/integracion
plugins: anyio-4.15.1, locust-2.46.6, cov-7.1.0
collected 73 items
tests\unitarias\test_casos_uso.py ..............                         [ 19%]
tests\unitarias\test_entidades.py ........................               [ 52%]
tests\unitarias\test_reglas_clinicas.py ........................         [ 84%]
tests\integracion\test_api.py ..........                                 [ 98%]
tests\integracion\test_zona_horaria.py .C:\Users\USER\AppData\Local\Python\pythoncore-3.14-64\Lib\ast.py:46: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x000001BD81671A80>
  return compile(source, filename, mode, flags,
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Users\USER\AppData\Local\Python\pythoncore-3.14-64\Lib\collections\__init__.py:455: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x000001BD814AE5C0>
  result = tuple_new(cls, iterable)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Users\USER\AppData\Local\Python\pythoncore-3.14-64\Lib\collections\__init__.py:455: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x000001BD812EB880>
  result = tuple_new(cls, iterable)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Users\USER\AppData\Local\Python\pythoncore-3.14-64\Lib\collections\__init__.py:455: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x000001BD815393F0>
  result = tuple_new(cls, iterable)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Users\USER\AppData\Local\Python\pythoncore-3.14-64\Lib\collections\__init__.py:455: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x000001BD8153A890>
  result = tuple_new(cls, iterable)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Users\USER\AppData\Local\Python\pythoncore-3.14-64\Lib\collections\__init__.py:455: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x000001BD812EB970>
  result = tuple_new(cls, iterable)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Users\USER\AppData\Local\Python\pythoncore-3.14-64\Lib\collections\__init__.py:455: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x000001BD8153AE30>
  result = tuple_new(cls, iterable)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Users\USER\AppData\Local\Python\pythoncore-3.14-64\Lib\collections\__init__.py:455: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x000001BD815D85E0>
  result = tuple_new(cls, iterable)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
                                 [100%]pmv_fastapi\.venv\Lib\site-packages\_pytest\unraisableexception.py:33: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x000001BD812E9C60>
  gc.collect()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
============================== warnings summary ===============================
.venv\Lib\site-packages\fastapi\testclient.py:1
  pmv_fastapi\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa
tests/integracion/test_api.py::test_registro_exitoso_devuelve_expediente
  pmv_fastapi\.venv\Lib\site-packages\sqlalchemy\sql\compiler.py:4049: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x000001BD8122AA70>
    if bp.key in cksm:
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.
tests/integracion/test_api.py::test_consultar_expediente_por_id_y_dni
  C:\Users\USER\AppData\Local\Python\pythoncore-3.14-64\Lib\typing.py:1284: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x000001BD81229D50>
    raise AttributeError(attr)
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.
-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.14.6-final-0 _______________
Name                                                  Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------------------------------------------------
app\__init__.py                                           0      0      0      0   100%
app\adapters\__init__.py                                  0      0      0      0   100%
app\adapters\entrada\__init__.py                          0      0      0      0   100%
app\adapters\entrada\http\__init__.py                     0      0      0      0   100%
app\adapters\entrada\http\api.py                         81      0      6      0   100%
app\adapters\entrada\http\esquemas.py                    28      0      0      0   100%
app\adapters\salida\__init__.py                           0      0      0      0   100%
app\adapters\salida\persistencia\__init__.py              0      0      0      0   100%
app\adapters\salida\persistencia\memoria.py              42      0     12      0   100%
app\adapters\salida\persistencia\sqlalchemy_repo.py     108      1     10      3    97%   152->154, 207->209, 237
app\application\__init__.py                               0      0      0      0   100%
app\application\casos_uso.py                            101      0     22      0   100%
app\application\puertos.py                                5      0      0      0   100%
app\domain\__init__.py                                    0      0      0      0   100%
app\domain\entidades.py                                 105      1     36      1    99%   101
app\domain\errores.py                                    10      0      0      0   100%
app\domain\reglas_clinicas.py                            38      0     12      0   100%
app\main.py                                              30      0      0      0   100%
-------------------------------------------------------------------------------------------------
TOTAL                                                   548      2     98      4    99%
Required test coverage of 80.0% reached. Total coverage: 99.07%
======================= 73 passed, 3 warnings in 5.43s ========================
```

## Resumen de cifras reales

| Conjunto | Resultado |
| --- | --- |
| Unitarias (`tests/unitarias`) | 62 pasadas |
| Integración (`tests/integracion`, SQLite) | 11 pasadas |
| Suite por defecto (`pytest`) | **73 pasadas, 0 fallidas, 0 saltadas** |
| E2E Playwright (`tests/e2e`, 4 pruebas) | **No ejecutadas**: 4 errores de entorno (falta `chromium_headless_shell-1194`; instalarlo requiere descargar el navegador, no autorizado en esta sesión). Declaradas como pasadas en `v1.0-PMV` (77 = 73 + 4) |
| Integración contra PostgreSQL | No ejecutada (no hay Docker ni PostgreSQL local); corre en el CI con `postgres:16` |
| Cobertura (sentencias + ramas) | **99,07 %** (548 sentencias, 2 sin cubrir; 98 ramas, 4 parciales); umbral 80 % superado |
| ruff check / format | 0 hallazgos / 33 archivos formateados |
| Humo manual | `python -m scripts.cargar_datos_prueba` (14 niños), `GET /api/salud` 200 `{"estado":"ok"}`, `/` 200, `/docs` 200, `GET /api/ninos` 200 |

Nota de compatibilidad: con Python 3.14 todo funciona sin cambios. Aparecen solo avisos (`ResourceWarning` de SQLite sin cerrar y `StarletteDeprecationWarning` por usar `httpx`). El conteo de sentencias (548) difiere del declarado en `cobertura.txt` (641) porque coverage cuenta distinto las sentencias multilínea en 3.14 (`esquemas.py` 28 vs 96; `entidades.py` 105 vs 123); el porcentaje total es el mismo (99 %).
