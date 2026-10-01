from datetime import date

HOY = date(2026, 9, 28)


def datos_nino(**cambios):
    base = dict(dni="71234567", nombres="Luz Mery", apellidos="Quispe Rojas", sexo="F",
                fecha_nacimiento=date(2025, 10, 15), establecimiento="P. S. Chongos Alto",
                distrito="Chongos Alto", comunidad="Palmayoc", altitud_m=3720,
                tutor_nombre="Rosa Rojas Pérez", tutor_celular="987654321")
    base.update(cambios)
    return base


def datos_eval(**cambios):
    base = dict(fecha=date(2026, 9, 20), hemoglobina_observada=12.4, peso_kg=8.1, talla_cm=69.5)
    base.update(cambios)
    return base
