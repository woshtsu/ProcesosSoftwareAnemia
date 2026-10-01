# ADR-005 — API REST JSON con contrato OpenAPI

**Contexto.** La integración futura con el HIS y con los incrementos 3 a 6 exige un contrato estable. El criterio de aceptación pide mensajes comprensibles ante datos inválidos.

**Decisión.** API REST JSON documentada con OpenAPI 3.1 (`docs/openapi.json`, Swagger UI servido localmente en `/docs`). Errores con formato único `{mensaje, errores:[{campo, mensaje}]}` en español: 422 validación, 409 duplicado, 404 no encontrado.

**Consecuencias.** (+) La interfaz marca cada campo con su mensaje. (+) Contrato verificable por pruebas de integración. (−) Sin WebSockets ni gRPC: no hay necesidad de tiempo real en el INC-1.
