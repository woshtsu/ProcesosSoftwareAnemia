# ADR-002: Decisiones explícitas del PMV

**Estado:** Aceptado  
**Fecha:** 2026-09-25  
**Contexto:** PMV INC-1 Anemia Junín

## Alcance

Esta implementación es una **demostración académica local con datos sintéticos**.  
No implementa: agenda, alertas, sincronización móvil, WhatsApp, integración HIS, predicción IA, prescripción, paneles territoriales ni cuentas con permisos diferenciados.

## Decisiones de datos

| Campo | Decisión |
|-------|----------|
| DNI, teléfono | Texto (preserva ceros iniciales) |
| Hb | Entero en décimas de g/dL internamente; API en g/dL |
| Peso | Gramos internamente; API en kg |
| Ajuste altitud | Tabulado (no fórmula continua); 0–499 m → ajuste 0.0 |
| Fechas clínicas | `YYYY-MM-DD` |
| Timestamps | UTC |
| Filtros de reporte | Interpretados en `America/Lima` |

## Decisiones de negocio

- **Colores/clasificación**: representan clasificación de Hb, NO riesgo predictivo
- **Menores de 6 meses**: `NO_EVALUABLE` (no se implementan reglas neonatales)
- **Sin dosajes**: `SIN_DOSAJE` ≠ `SIN_ANEMIA`
- **Hb ajustada negativa**: se conserva y marca `NO_EVALUABLE` con advertencia
- **Edición**: solo peso, distrito, altitud, cuidador y teléfono
- **Historial**: inmutable; un dosaje antiguo insertado después no reemplaza el último
- **Transacción**: niño + dosaje inicial son atómicos; si falla uno, no se guarda ninguno
- **Intento rechazado**: se registra DESPUÉS del rollback
- **HIST-1.5**: conserva su identificador aunque el reporte se implemente dentro de INC-1
- **Actores funcionales**: personal de salud y coordinador sin cuentas diferenciadas en esta versión

## Decisiones de infraestructura

- Servidor: Waitress en `127.0.0.1:8000` para demostración; Flask dev server para desarrollo
- Sin CORS habilitado
- Sin React, Node ni CDN externo
- Formularios HTML con CSRF (Flask-WTF); API JSON sin CORS
- Aviso visible: "Demostración académica con datos sintéticos"

## Actualización 2026-09-25 (T-008, verificación del PMV)

- **Punto de entrada:** `python -m anemia_junin` (Waitress por defecto; `--dev` para Flask). Configuración por variables `ANEMIA_*`.
- **CSRF efectivo:** `CSRFProtect` se inicializa en `bootstrap.py` (antes solo existía el campo oculto en las plantillas). La API JSON queda exenta: no usa cookies ni CORS.
- **Transacciones de escritura con `BEGIN IMMEDIATE`:** la prueba de carga con Locust (20 usuarios) reveló `500 database is locked` en `POST /dosajes` cuando dos transacciones pasaban de lectura a escritura. Los casos de uso de escritura usan ahora una unidad de trabajo inmediata; los de lectura mantienen `BEGIN` diferido.
- **Sin valores por defecto silenciosos:** los adaptadores de entrada ya no sustituyen fecha, sexo, tipo de nacimiento o altitud mal formados por valores por defecto; pasan los errores de conversión al caso de uso (`errores_entrada`), que rechaza y registra el intento.
- **Tiempo testeable:** el listado de 6–59 meses usa el puerto `Reloj` (`FiltroNinos.fecha_referencia`), no `date.today()`.
- **Bandas de altitud no verificadas:** filas ≥ 4000 msnm con `"verificada": false`; el clasificador añade una advertencia y la UI la muestra en el expediente.
- **Salud de la BD:** `GET /api/v1/salud` usa `verificar_conexion` del adaptador SQLite inyectada por `bootstrap` (el adaptador de entrada ya no importa `sqlite3`).
