"""Fechas y zona horaria del dominio (Perú, UTC-5). Solo biblioteca estándar."""

from datetime import UTC, date, datetime, time, timedelta, timezone

# Perú usa UTC-5 todo el año (sin horario de verano); se fija el desfase para no depender de tzdata.
ZONA_PERU = timezone(timedelta(hours=-5), "America/Lima")


def edad_en_meses(fecha_nacimiento: date, fecha_referencia: date) -> int:
    """Meses cumplidos entre dos fechas."""
    meses = (fecha_referencia.year - fecha_nacimiento.year) * 12 + (fecha_referencia.month - fecha_nacimiento.month)
    if fecha_referencia.day < fecha_nacimiento.day:
        meses -= 1
    return meses


def ahora() -> datetime:
    return datetime.now(UTC)


def fecha_local(momento: datetime) -> date:
    """Fecha calendario en Perú de un instante guardado en UTC (DEF-02)."""
    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=UTC)
    return momento.astimezone(ZONA_PERU).date()


def limites_utc(desde: date, hasta: date) -> tuple[datetime, datetime]:
    """Inicio y fin, en UTC, de los días locales [desde, hasta] (DEF-02)."""
    inicio = datetime.combine(desde, time.min, tzinfo=ZONA_PERU).astimezone(UTC)
    fin = datetime.combine(hasta, time.max, tzinfo=ZONA_PERU).astimezone(UTC)
    return inicio, fin
