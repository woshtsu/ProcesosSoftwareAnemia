"""
Repositorios SQLite — PMV Anemia Junín.

Implementan los puertos del dominio (RepositorioNinos, RepositorioDosajes, RepositorioIntentos).
Toda conversión entre entidades del dominio y filas SQL ocurre aquí.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import date, datetime

from anemia_junin.domain.entities import (
    Clasificacion,
    Dosaje,
    IntentoRegistro,
    Nino,
    Sexo,
    TipoNacimiento,
)
from anemia_junin.domain.ports import FiltroNinos, PaginaNinos

# Orden de clasificación para la lista (HIST-1.4)
_ORDEN_CLASIFICACION = {
    Clasificacion.SEVERA.value: 0,
    Clasificacion.MODERADA.value: 1,
    Clasificacion.LEVE.value: 2,
    Clasificacion.NO_EVALUABLE.value: 3,
    Clasificacion.SIN_DOSAJE.value: 4,
    Clasificacion.SIN_ANEMIA.value: 5,
}


def _nino_desde_fila(fila: sqlite3.Row) -> Nino:
    return Nino(
        id=uuid.UUID(fila["id"]),
        dni=fila["dni"],
        nombres=fila["nombres"],
        apellidos=fila["apellidos"],
        fecha_nacimiento=date.fromisoformat(fila["fecha_nacimiento"]),
        sexo=Sexo(fila["sexo"]),
        tipo_nacimiento=TipoNacimiento(fila["tipo_nacimiento"]),
        peso_g=fila["peso_g"],
        distrito=fila["distrito"],
        altitud_msnm=fila["altitud_msnm"],
        cuidador=fila["cuidador"],
        telefono=fila["telefono"],
        created_at=datetime.fromisoformat(fila["created_at"]),
        updated_at=datetime.fromisoformat(fila["updated_at"]),
    )


def _dosaje_desde_fila(fila: sqlite3.Row) -> Dosaje:
    return Dosaje(
        id=uuid.UUID(fila["id"]),
        nino_id=uuid.UUID(fila["nino_id"]),
        fecha_dosaje=date.fromisoformat(fila["fecha_dosaje"]),
        hb_observada_ddl=fila["hb_observada_ddl"],
        altitud_msnm=fila["altitud_msnm"],
        ajuste_ddl=fila["ajuste_ddl"],
        hb_ajustada_ddl=fila["hb_ajustada_ddl"],
        edad_meses=fila["edad_meses"],
        clasificacion=Clasificacion(fila["clasificacion"]),
        version_normativa=fila["version_normativa"],
        advertencias=json.loads(fila["advertencias_json"]),
        created_at=datetime.fromisoformat(fila["created_at"]),
    )


class RepositorioNinosSQLite:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def guardar(self, nino: Nino) -> None:
        self._conn.execute(
            """
            INSERT INTO ninos (
                id, dni, nombres, apellidos, fecha_nacimiento,
                sexo, tipo_nacimiento, peso_g, distrito, altitud_msnm,
                cuidador, telefono, created_at, updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                str(nino.id), nino.dni, nino.nombres, nino.apellidos,
                nino.fecha_nacimiento.isoformat(), nino.sexo.value,
                nino.tipo_nacimiento.value, nino.peso_g, nino.distrito,
                nino.altitud_msnm, nino.cuidador, nino.telefono,
                nino.created_at.isoformat(), nino.updated_at.isoformat(),
            ),
        )

    def obtener_por_dni(self, dni: str) -> Nino | None:
        fila = self._conn.execute(
            "SELECT * FROM ninos WHERE dni = ?", (dni,)
        ).fetchone()
        return _nino_desde_fila(fila) if fila else None

    def obtener_por_id(self, id: uuid.UUID) -> Nino | None:
        fila = self._conn.execute(
            "SELECT * FROM ninos WHERE id = ?", (str(id),)
        ).fetchone()
        return _nino_desde_fila(fila) if fila else None

    def actualizar(self, nino: Nino) -> None:
        self._conn.execute(
            """
            UPDATE ninos
               SET peso_g = ?, distrito = ?, altitud_msnm = ?,
                   cuidador = ?, telefono = ?, updated_at = ?
             WHERE id = ?
            """,
            (
                nino.peso_g, nino.distrito, nino.altitud_msnm,
                nino.cuidador, nino.telefono, nino.updated_at.isoformat(),
                str(nino.id),
            ),
        )

    def listar(self, filtro: FiltroNinos) -> PaginaNinos:
        """
        Lista niños de 6–59 meses con el último dosaje.
        Orden: clasificación (severa→sin_anemia), luego apellidos, nombres, DNI.
        """
        hoy = date.today().isoformat()
        params: list = []

        # Subconsulta: último dosaje por niño (por fecha clínica, desempate created_at, id)
        cte_ultimo = """
            WITH ultimo_dosaje AS (
                SELECT d.nino_id,
                       d.clasificacion,
                       ROW_NUMBER() OVER (
                           PARTITION BY d.nino_id
                           ORDER BY d.fecha_dosaje DESC, d.created_at DESC, d.id DESC
                       ) AS rn
                FROM dosajes d
            ),
            ultimo AS (
                SELECT nino_id, clasificacion FROM ultimo_dosaje WHERE rn = 1
            )
        """

        where_clausulas = [
            # Edad 6–59 meses completos respecto a hoy
            """
            (
                (
                    (CAST(strftime('%Y', ?) AS INTEGER) - CAST(strftime('%Y', fecha_nacimiento) AS INTEGER)) * 12
                    + (CAST(strftime('%m', ?) AS INTEGER) - CAST(strftime('%m', fecha_nacimiento) AS INTEGER))
                    - CASE WHEN strftime('%d', ?) < strftime('%d', fecha_nacimiento) THEN 1 ELSE 0 END
                ) BETWEEN 6 AND 59
            )
            """
        ]
        params += [hoy, hoy, hoy]

        if filtro.q:
            where_clausulas.append(
                "(n.dni LIKE ? OR n.nombres LIKE ? OR n.apellidos LIKE ?)"
            )
            q = f"%{filtro.q}%"
            params += [q, q, q]

        if filtro.distrito:
            where_clausulas.append("n.distrito = ?")
            params.append(filtro.distrito)

        if filtro.clasificacion:
            if filtro.clasificacion == "SIN_DOSAJE":
                where_clausulas.append("u.clasificacion IS NULL")
            else:
                where_clausulas.append("u.clasificacion = ?")
                params.append(filtro.clasificacion)

        where_sql = " AND ".join(where_clausulas)

        count_sql = f"""
            {cte_ultimo}
            SELECT COUNT(*) FROM ninos n
            LEFT JOIN ultimo u ON u.nino_id = n.id
            WHERE {where_sql}
        """
        total = self._conn.execute(count_sql, params).fetchone()[0]

        select_sql = f"""
            {cte_ultimo}
            SELECT n.*, COALESCE(u.clasificacion, 'SIN_DOSAJE') AS clasificacion_actual
            FROM ninos n
            LEFT JOIN ultimo u ON u.nino_id = n.id
            WHERE {where_sql}
            ORDER BY
                CASE COALESCE(u.clasificacion, 'SIN_DOSAJE')
                    WHEN 'SEVERA'      THEN 0
                    WHEN 'MODERADA'    THEN 1
                    WHEN 'LEVE'        THEN 2
                    WHEN 'NO_EVALUABLE'THEN 3
                    WHEN 'SIN_DOSAJE'  THEN 4
                    WHEN 'SIN_ANEMIA'  THEN 5
                    ELSE 6
                END,
                n.apellidos COLLATE NOCASE,
                n.nombres   COLLATE NOCASE,
                n.dni
            LIMIT ? OFFSET ?
        """
        params_pag = params + [filtro.tamano, filtro.offset]
        filas = self._conn.execute(select_sql, params_pag).fetchall()

        items = []
        for fila in filas:
            nino = _nino_desde_fila(fila)
            items.append({
                "nino": nino,
                "clasificacion_actual": Clasificacion(fila["clasificacion_actual"]),
            })

        return PaginaNinos(
            items=items,
            total=total,
            pagina=filtro.pagina,
            tamano=filtro.tamano,
        )

    def consultar_reporte(
        self,
        *,
        desde_utc: datetime,
        hasta_utc: datetime,
        desde_iso: str,
        hasta_iso: str,
    ) -> dict:
        """Consulta agregada para el reporte de registros (HIST-1.5)."""
        ninos_reg = self._conn.execute(
            "SELECT COUNT(*) FROM ninos WHERE created_at >= ? AND created_at <= ?",
            (desde_utc.isoformat(), hasta_utc.isoformat()),
        ).fetchone()[0]

        dosajes_reg = self._conn.execute(
            "SELECT COUNT(*) FROM dosajes WHERE fecha_dosaje >= ? AND fecha_dosaje <= ?",
            (desde_iso, hasta_iso),
        ).fetchone()[0]

        filas_clas = self._conn.execute(
            """
            SELECT clasificacion, COUNT(*) as c
            FROM dosajes
            WHERE fecha_dosaje >= ? AND fecha_dosaje <= ?
            GROUP BY clasificacion
            """,
            (desde_iso, hasta_iso),
        ).fetchall()
        dist_clas = {f["clasificacion"]: f["c"] for f in filas_clas}

        filas_dist = self._conn.execute(
            """
            SELECT distrito, COUNT(*) as c
            FROM ninos
            WHERE created_at >= ? AND created_at <= ?
            GROUP BY distrito
            """,
            (desde_utc.isoformat(), hasta_utc.isoformat()),
        ).fetchall()
        dist_dist = {f["distrito"]: f["c"] for f in filas_dist}

        return {
            "ninos_registrados": ninos_reg,
            "dosajes_registrados": dosajes_reg,
            "distribucion_clasificacion": dist_clas,
            "distribucion_distrito": dist_dist,
        }


class RepositorioDosajesSQLite:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def guardar(self, dosaje: Dosaje) -> None:
        self._conn.execute(
            """
            INSERT INTO dosajes (
                id, nino_id, fecha_dosaje, hb_observada_ddl, altitud_msnm,
                ajuste_ddl, hb_ajustada_ddl, edad_meses, clasificacion,
                version_normativa, advertencias_json, created_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                str(dosaje.id), str(dosaje.nino_id),
                dosaje.fecha_dosaje.isoformat(),
                dosaje.hb_observada_ddl, dosaje.altitud_msnm,
                dosaje.ajuste_ddl, dosaje.hb_ajustada_ddl,
                dosaje.edad_meses, dosaje.clasificacion.value,
                dosaje.version_normativa,
                json.dumps(dosaje.advertencias, ensure_ascii=False),
                dosaje.created_at.isoformat(),
            ),
        )

    def listar_por_nino(self, nino_id: uuid.UUID) -> list[Dosaje]:
        filas = self._conn.execute(
            """
            SELECT * FROM dosajes WHERE nino_id = ?
            ORDER BY fecha_dosaje DESC, created_at DESC, id DESC
            """,
            (str(nino_id),),
        ).fetchall()
        return [_dosaje_desde_fila(f) for f in filas]

    def ultimo_por_nino(self, nino_id: uuid.UUID) -> Dosaje | None:
        fila = self._conn.execute(
            """
            SELECT * FROM dosajes WHERE nino_id = ?
            ORDER BY fecha_dosaje DESC, created_at DESC, id DESC
            LIMIT 1
            """,
            (str(nino_id),),
        ).fetchone()
        return _dosaje_desde_fila(fila) if fila else None


class RepositorioIntentosSQLite:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def guardar(self, intento: IntentoRegistro) -> None:
        self._conn.execute(
            """
            INSERT INTO intentos_registro (id, momento, operacion, resultado, codigos_error)
            VALUES (?,?,?,?,?)
            """,
            (
                str(intento.id),
                intento.momento.isoformat(),
                intento.operacion,
                intento.resultado,
                json.dumps(intento.codigos_error, ensure_ascii=False),
            ),
        )

    def contar_en_periodo(self, desde: datetime, hasta: datetime) -> dict[str, int]:
        filas = self._conn.execute(
            """
            SELECT resultado, COUNT(*) as c
              FROM intentos_registro
             WHERE momento >= ? AND momento <= ?
               AND operacion = 'CREAR_NINO'
             GROUP BY resultado
            """,
            (desde.isoformat(), hasta.isoformat()),
        ).fetchall()
        resultado: dict[str, int] = {"ACEPTADO": 0, "RECHAZADO": 0}
        for fila in filas:
            resultado[fila["resultado"]] = fila["c"]
        return resultado
