# ADR-001: Arquitectura Hexagonal (Ports & Adapters)

**Estado:** Aceptado  
**Fecha:** 2026-09-25  
**Contexto:** PMV INC-1 Anemia Junín

## Decisión

Se adopta arquitectura hexagonal con tres capas:

1. **Dominio** (`domain/`): entidades, validaciones, clasificador. Sin dependencias externas.
2. **Aplicación** (`application/`): casos de uso y DTOs. Depende solo de interfaces (Protocols) del dominio.
3. **Adaptadores** (`adapters/`): Flask, SQLite, Jinja2. Implementan los puertos definidos en el dominio.

## Interfaces (Protocols)

- `RepositorioNinos` — búsqueda, persistencia y listado de niños
- `RepositorioDosajes` — persistencia y consulta de dosajes
- `UnidadDeTrabajo` — transacciones atómicas (context manager)
- `ProveedorNormativo` — acceso a configuración NTS 213
- `Reloj` — hora UTC actual (testeable)

## Reglas de importación prohibidas

- `domain` NO importa: `flask`, `sqlite3`, ni ningún módulo de `adapters`
- `application` NO importa: `flask`, `sqlite3`, ni ningún módulo de `adapters`
- Templates Jinja2 NO hacen peticiones HTTP internas
- Las reglas de negocio NO se repiten en rutas, templates ni JavaScript

## Consecuencias

- Testabilidad: dominio y casos de uso se testean sin infraestructura
- Intercambiabilidad: SQLite puede reemplazarse sin tocar dominio/aplicación
- Claridad: cada capa tiene responsabilidad única y trazable
