# ADR-002 — Cliente PWA web adaptable

**Contexto.** Las postas usan equipos heterogéneos (PC y teléfonos Android antiguos, riesgo identificado en el plan S3-S4). Publicar en una tienda de aplicaciones retrasaría el piloto.

**Decisión.** Interfaz web adaptable instalable como PWA (manifest + service worker que guarda la interfaz en caché). El borrador del formulario se conserva en el dispositivo (`localStorage`) para no perder datos si se corta la conexión antes de guardar.

**Consecuencias.** (+) Un solo código para PC y móvil; actualización inmediata al desplegar. (+) La interfaz abre aunque la red sea intermitente. (−) El registro definitivo aún requiere conexión: la cola de sincronización con resolución de conflictos es alcance del INC-3 (no se adelanta para respetar la priorización).
