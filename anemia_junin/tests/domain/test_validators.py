"""
Pruebas del dominio: validadores — PMV Anemia Junín.

Casos indispensables según el plan:
- DNI con cero inicial, múltiples errores
- Límites de peso, Hb, altitud, fechas
- Meses completos: límites de 6, 24, 60 meses; bisiestos
"""

from __future__ import annotations

from datetime import date

import pytest

from anemia_junin.domain.validators import (
    ErrorValidacion,
    meses_completos,
    normalizar_nombre,
    validar_altitud,
    validar_dni,
    validar_fecha_dosaje,
    validar_fecha_nacimiento,
    validar_hb_gdl,
    validar_nombre,
    validar_peso_kg,
    validar_telefono,
)

# ─── meses_completos ──────────────────────────────────────────────────────────

class TestMesesCompletos:
    def test_mismo_dia(self):
        assert meses_completos(date(2023, 1, 1), date(2023, 1, 1)) == 0

    def test_un_mes_exacto(self):
        assert meses_completos(date(2023, 1, 15), date(2023, 2, 15)) == 1

    def test_un_mes_menos_un_dia(self):
        assert meses_completos(date(2023, 1, 15), date(2023, 2, 14)) == 0

    def test_seis_meses_exacto(self):
        nacimiento = date(2023, 1, 1)
        seis_meses = date(2023, 7, 1)
        assert meses_completos(nacimiento, seis_meses) == 6

    def test_seis_meses_menos_un_dia(self):
        nacimiento = date(2023, 1, 1)
        antes = date(2023, 6, 30)
        assert meses_completos(nacimiento, antes) == 5

    def test_veinticuatro_meses(self):
        assert meses_completos(date(2021, 3, 10), date(2023, 3, 10)) == 24

    def test_cincuenta_y_nueve_meses(self):
        nacimiento = date(2021, 1, 1)
        # 59 meses completos = 2025-12-01 (4 años 11 meses)
        assert meses_completos(nacimiento, date(2025, 12, 1)) == 59

    def test_sesenta_meses(self):
        nacimiento = date(2021, 1, 1)
        assert meses_completos(nacimiento, date(2026, 1, 1)) == 60

    def test_nacimiento_29_febrero_bisiesto(self):
        # Nacimiento 29-feb-2020; cumpleaños 2023 (no bisiesto) → cuenta el 28-feb
        nacimiento = date(2020, 2, 29)
        en_2023 = date(2023, 2, 28)
        assert meses_completos(nacimiento, en_2023) == 36

    def test_nacimiento_29_febrero_antes_del_aniversario(self):
        nacimiento = date(2020, 2, 29)
        antes = date(2023, 2, 27)
        assert meses_completos(nacimiento, antes) == 35

    def test_fecha_fin_anterior_a_inicio(self):
        assert meses_completos(date(2024, 6, 1), date(2024, 1, 1)) == 0


# ─── DNI ──────────────────────────────────────────────────────────────────────

class TestValidarDni:
    def test_dni_valido(self):
        assert validar_dni("12345678") == []

    def test_dni_con_cero_inicial(self):
        assert validar_dni("01234567") == []

    def test_dni_todos_ceros(self):
        assert validar_dni("00000000") == []

    def test_dni_siete_digitos(self):
        assert validar_dni("1234567") != []

    def test_dni_nueve_digitos(self):
        assert validar_dni("123456789") != []

    def test_dni_con_letras(self):
        assert validar_dni("1234567A") != []

    def test_dni_vacio(self):
        assert validar_dni("") != []

    def test_dni_no_string(self):
        assert validar_dni(12345678) != []


# ─── Nombres ──────────────────────────────────────────────────────────────────

class TestValidarNombre:
    def test_nombre_valido(self):
        assert validar_nombre("Ana María") == []

    def test_nombre_con_tildes(self):
        assert validar_nombre("Óscar René") == []

    def test_nombre_con_guion(self):
        assert validar_nombre("Juan-Carlos") == []

    def test_nombre_muy_corto(self):
        assert validar_nombre("A") != []

    def test_nombre_muy_largo(self):
        assert validar_nombre("A" * 81) != []

    def test_nombre_con_numeros(self):
        assert validar_nombre("Ana123") != []

    def test_normalizar_espacios(self):
        assert normalizar_nombre("  Ana   María  ") == "Ana María"


# ─── Fecha de nacimiento ──────────────────────────────────────────────────────

class TestValidarFechaNacimiento:
    _HOY = date(2026, 9, 25)

    def test_recien_nacido(self):
        assert validar_fecha_nacimiento(self._HOY, self._HOY) == []

    def test_nino_de_cuatro_anos(self):
        nacimiento = date(2022, 5, 10)
        assert validar_fecha_nacimiento(nacimiento, self._HOY) == []

    def test_exactamente_cinco_anos(self):
        # 60 meses completos → rechazado
        nacimiento = date(2021, 9, 25)
        assert validar_fecha_nacimiento(nacimiento, self._HOY) != []

    def test_cincuenta_y_nueve_meses(self):
        nacimiento = date(2021, 10, 25)
        assert validar_fecha_nacimiento(nacimiento, self._HOY) == []

    def test_fecha_futura(self):
        assert validar_fecha_nacimiento(date(2027, 1, 1), self._HOY) != []

    def test_no_fecha(self):
        assert validar_fecha_nacimiento("2023-01-01", self._HOY) != []


# ─── Peso ─────────────────────────────────────────────────────────────────────

class TestValidarPeso:
    def test_peso_valido_entero(self):
        errores, gramos = validar_peso_kg(8)
        assert errores == []
        assert gramos == 8000

    def test_peso_valido_decimal(self):
        errores, gramos = validar_peso_kg("8.500")
        assert errores == []
        assert gramos == 8500

    def test_peso_minimo(self):
        errores, gramos = validar_peso_kg(1)
        assert errores == []
        assert gramos == 1000

    def test_peso_maximo(self):
        errores, gramos = validar_peso_kg(30)
        assert errores == []
        assert gramos == 30000

    def test_peso_bajo_minimo(self):
        errores, _ = validar_peso_kg(0.9)
        assert errores != []

    def test_peso_sobre_maximo(self):
        errores, _ = validar_peso_kg(30.001)
        assert errores != []

    def test_peso_precision_excesiva(self):
        # 4 decimales → rechazado sin redondear
        errores, _ = validar_peso_kg("8.1234")
        assert errores != []

    def test_tres_decimales_ok(self):
        errores, gramos = validar_peso_kg("8.125")
        assert errores == []
        assert gramos == 8125

    def test_peso_texto_invalido(self):
        errores, _ = validar_peso_kg("abc")
        assert errores != []


# ─── Altitud ──────────────────────────────────────────────────────────────────

class TestValidarAltitud:
    def test_cero(self):
        assert validar_altitud(0) == []

    def test_maximo(self):
        assert validar_altitud(4999) == []

    def test_sobre_maximo(self):
        assert validar_altitud(5000) != []

    def test_negativo(self):
        assert validar_altitud(-1) != []

    def test_string_numerico(self):
        assert validar_altitud("3271") == []


# ─── Hemoglobina ──────────────────────────────────────────────────────────────

class TestValidarHb:
    def test_hb_valida(self):
        errores, ddl = validar_hb_gdl(10.5)
        assert errores == []
        assert ddl == 105

    def test_hb_minima(self):
        errores, ddl = validar_hb_gdl(2.0)
        assert errores == []
        assert ddl == 20

    def test_hb_maxima(self):
        errores, ddl = validar_hb_gdl(25.0)
        assert errores == []
        assert ddl == 250

    def test_hb_bajo_minimo(self):
        errores, _ = validar_hb_gdl(1.9)
        assert errores != []

    def test_hb_sobre_maximo(self):
        errores, _ = validar_hb_gdl(25.1)
        assert errores != []

    def test_hb_dos_decimales_rechazado(self):
        errores, _ = validar_hb_gdl("10.55")
        assert errores != []

    def test_hb_un_decimal_ok(self):
        errores, ddl = validar_hb_gdl("10.5")
        assert errores == []
        assert ddl == 105

    def test_hb_entero_ok(self):
        errores, ddl = validar_hb_gdl(10)
        assert errores == []
        assert ddl == 100


# ─── Fecha de dosaje ──────────────────────────────────────────────────────────

class TestValidarFechaDosaje:
    _HOY = date(2026, 9, 25)
    _NACIMIENTO = date(2022, 9, 25)  # 4 años exactos → 48 meses

    def test_dosaje_valido(self):
        errores, edad = validar_fecha_dosaje(date(2026, 9, 1), self._NACIMIENTO, self._HOY)
        assert errores == []
        assert edad == 47

    def test_dosaje_igual_a_nacimiento(self):
        errores, edad = validar_fecha_dosaje(self._NACIMIENTO, self._NACIMIENTO, self._HOY)
        assert errores == []
        assert edad == 0

    def test_dosaje_anterior_a_nacimiento(self):
        errores, _ = validar_fecha_dosaje(date(2022, 9, 24), self._NACIMIENTO, self._HOY)
        assert errores != []

    def test_dosaje_futuro(self):
        errores, _ = validar_fecha_dosaje(date(2027, 1, 1), self._NACIMIENTO, self._HOY)
        assert errores != []

    def test_dosaje_a_los_59_meses(self):
        nacimiento = date(2021, 10, 25)
        fecha = date(2026, 9, 25)  # 59 meses
        errores, edad = validar_fecha_dosaje(fecha, nacimiento, self._HOY)
        assert errores == []
        assert edad == 59

    def test_dosaje_a_los_60_meses_rechazado(self):
        nacimiento = date(2021, 9, 25)
        fecha = date(2026, 9, 25)  # 60 meses
        errores, _ = validar_fecha_dosaje(fecha, nacimiento, self._HOY)
        assert errores != []


# ─── Teléfono ─────────────────────────────────────────────────────────────────

class TestValidarTelefono:
    def test_telefono_valido(self):
        assert validar_telefono("987654321") == []

    def test_telefono_none(self):
        assert validar_telefono(None) == []

    def test_telefono_vacio(self):
        assert validar_telefono("") == []

    def test_telefono_ocho_digitos(self):
        assert validar_telefono("12345678") != []

    def test_telefono_diez_digitos(self):
        assert validar_telefono("1234567890") != []

    def test_telefono_con_letras(self):
        assert validar_telefono("98765432A") != []


# ─── ErrorValidacion ──────────────────────────────────────────────────────────

class TestErrorValidacion:
    def test_lanza_cuando_hay_errores(self):
        with pytest.raises(ErrorValidacion) as exc_info:
            ErrorValidacion.si_hay_errores({"dni": ["error"]})
        assert "dni" in exc_info.value.errores

    def test_no_lanza_cuando_no_hay_errores(self):
        ErrorValidacion.si_hay_errores({"dni": [], "nombres": []})  # sin excepción

    def test_multiples_errores(self):
        errores = {
            "dni": ["Debe tener 8 dígitos"],
            "nombres": ["Muy corto"],
            "peso_kg": ["Fuera de rango"],
        }
        with pytest.raises(ErrorValidacion) as exc_info:
            ErrorValidacion.si_hay_errores(errores)
        assert len(exc_info.value.errores) == 3
