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
