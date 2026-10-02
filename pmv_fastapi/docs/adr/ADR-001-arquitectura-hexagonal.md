# ADR-001 — Arquitectura hexagonal en un monolito modular

**Contexto.** El roadmap tiene 6 incrementos. Los siguientes agregan adaptadores nuevos sobre el mismo núcleo: cola de sincronización offline (INC-3), canal WhatsApp (INC-4) y servicio de modelo predictivo (INC-5). El equipo es de 3 personas y el PMV debe probarse sin depender de la base de datos.

**Decisión.** Núcleo de dominio (`app/domain`) y casos de uso (`app/application`) sin dependencias de frameworks. El núcleo define el puerto `RepositorioNinos`; los adaptadores de entrada (HTTP/FastAPI) y de salida (SQLAlchemy, memoria) lo implementan. Se despliega como un solo servicio (monolito modular), no como microservicios.

**Consecuencias.** (+) 62 pruebas unitarias del núcleo corren en < 1 s con el adaptador en memoria. (+) Cambiar SQLite↔PostgreSQL no toca el dominio (verificado: la misma suite de integración pasa en ambos). (+) INC-3/4/5 se incorporan como adaptadores. (−) Más archivos y mapeos ORM↔entidad que un CRUD directo. Microservicios se descartan: su costo operativo no se justifica para 3 desarrolladores y una sola posta piloto.
