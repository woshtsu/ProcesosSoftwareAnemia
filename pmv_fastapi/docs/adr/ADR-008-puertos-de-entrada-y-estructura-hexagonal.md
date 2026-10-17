# ADR-008 — Puertos de entrada y estructura hexagonal explícita

**Contexto.** En el Incremento 1 (ADR-001) el adaptador HTTP importaba directamente la clase concreta `ServicioExpediente` y el dominio y los puertos vivían en archivos únicos (`entidades.py`, `puertos.py`, `casos_uso.py`). Para el Incremento 2 se suman casos de uso nuevos (agenda y alertas) y los incrementos 3 a 5 agregarán adaptadores (cola offline, WhatsApp, modelo predictivo). La guía de la Sesión 9 pide que las dependencias apunten siempre hacia el dominio y que eso se pueda comprobar.

**Decisión.** Estructura por capas, con las dependencias permitidas verificadas por pruebas automáticas:

```
app/
├── domain/model/        entidades y objetos de valor puros
├── domain/service/      servicios de dominio: reglas clínicas, validaciones, agenda, alertas
├── ports/inbound/       interfaces (typing.Protocol) de los casos de uso
├── ports/outbound/      interfaces de persistencia y reloj
├── application/         implementación de los casos de uso (implementa ports.inbound, usa ports.outbound)
├── adapters/inbound/http/          FastAPI y DTO; depende solo de ports.inbound y domain.model
├── adapters/outbound/persistence/  SQLAlchemy y memoria (implementan ports.outbound)
├── web/                 PWA estática
└── main.py              raíz de composición: único módulo que conoce las implementaciones concretas
```

Reglas de dependencia (se comprueban con `tests/arquitectura/test_dependencias.py`, análisis AST de los `import`, casos CP-37 a CP-43):

1. `domain` no importa fastapi, pydantic, sqlalchemy, starlette, uvicorn ni psycopg2, ni `ports`, `application` o `adapters`.
2. `ports` solo importa `domain`, la biblioteca estándar y `typing`.
3. `application` no importa `adapters` ni frameworks.
4. `adapters.inbound` no importa `application` ni `adapters.outbound` (y solo habla con `ports.inbound` y `domain.model`).
5. `adapters.outbound` no importa `application` ni `adapters.inbound`.
6. Solo `main.py` importa a la vez `application` y `adapters`.
7. No quedan módulos «puente» en las rutas anteriores (`adapters/entrada`, `adapters/salida`, `application/casos_uso.py`, `application/puertos.py`, `domain/entidades.py`, `domain/errores.py`, `domain/reglas_clinicas.py`).

Puertos de entrada: `GestionarExpediente`, `ConsultarSeguimiento`, `GenerarReporte`, `GenerarAgenda` y `ConsultarControlesVencidos`. El adaptador HTTP resuelve cada puerto desde `app.state` (inyectado en `main.py`) y se tipa contra el `Protocol`, de modo que puede probarse con un caso de uso falso. Los puertos de salida son `RepositorioNinos` y `Reloj`.

**Consecuencias.** (+) Una violación de la arquitectura rompe la compilación del pipeline (las pruebas de arquitectura corren con `pytest`). (+) Los casos de uso se prueban con el repositorio en memoria y un reloj fijo, sin base de datos ni HTTP. (+) Agregar un adaptador (por ejemplo WhatsApp en el INC-4) es un paquete nuevo bajo `adapters/`. (−) Más archivos que el Incremento 1. (−) La regla 4 es estricta: si un adaptador de entrada necesita una regla del dominio (por ejemplo calcular la edad), debe recibirla ya resuelta por el caso de uso o usar solo `domain.model`, no `domain.service`.
