# Informe de trabajo: CONVERSOR-ENTREGAS (S6-05)

**Fecha:** 2026-10-01  
**Tarea:** Conversión de Informe y Presentación S6 Integrador a PDF y DOCX  
**Rama:** `feature/s6-integrador-final`  
**Ejecutor:** Claude Haiku 4.5  

## Resumen

Conversión exitosa de los entregables Integrador S6 a formatos PDF y DOCX mediante pandoc (a través de `pypandoc_binary`). Se generaron tres archivos:

1. **Informe_Integrador_Anemia_Junin.docx** (5.8 MB)
2. **Informe_Integrador_Anemia_Junin.pdf** (7.2 MB, 50 páginas)
3. **Presentacion_Integrador_Anemia_Junin.pdf** (1.8 MB)

## Herramientas utilizadas

| Herramienta | Versión | Propósito |
| --- | --- | --- |
| Python | 3.14.6 | Entorno de ejecución |
| `pypandoc_binary` | 1.17 | Conversor MD → DOCX/HTML/PDF |
| Microsoft Edge | headless | Renderizado de PDF desde HTML |
| PowerPoint COM | — | Conversión PPTX → PDF |
| `pypdf` | (instalado) | Validación de PDF |

## Procedimiento

### 1. Preparación
- Verificación de Python y herramientas disponibles
- Instalación de `pypandoc_binary` en `herramientas\.venv`
- Creación de directorios: `herramientas\conversion\` y `diagramas\_build\conversion\`

### 2. Generación de DOCX

**Entrada:** `entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md`

**Proceso:**
1. Copiar MD a `diagramas/_build/conversion/` (temporal)
2. Reemplazar referencias SVG → PNG (para que Word las renderice correctamente)
3. Ejecutar: `pandoc <md> -o <docx> --toc --resource-path=.;../..`
4. Incluir imágenes: PNG embebidas desde `diagramas/png/`

**Resultado:** `exportados/semana-06/Informe_Integrador_Anemia_Junin.docx` (5.8 MB)

### 3. Generación de PDF

**Proceso:**
1. Ejecutar `pandoc` con generador HTML: `--standalone --embed-resources`
2. Pasar HTML a Microsoft Edge en modo headless: `msedge --headless --disable-gpu --print-to-pdf=<pdf>`
3. Renderizado de tablas y figuras directamente en el navegador

**Resultado:** `exportados/semana-06/Informe_Integrador_Anemia_Junin.pdf` (7.2 MB, 50 páginas)

### 4. Generación de PDF de Presentación

**Entrada:** `exportados/semana-06/Presentacion_Integrador_Anemia_Junin.pptx` (3.0 MB)

**Proceso:**
1. Detectar instalación de PowerPoint (COM)
2. Abrir PPTX con `PowerPoint.Application`
3. Guardar con formato 32 (PDF)

**Resultado:** `exportados/semana-06/Presentacion_Integrador_Anemia_Junin.pdf` (1.8 MB)

## Validación

### PDF del Informe
- **Páginas:** 50
- **Tamaño:** 7.2 MB
- **Primeros títulos identificados:** ✓ Presentes (INFORME ACADÉMICO..., Resumen ejecutivo, Unidad I, Unidad II, etc.)
- **Imágenes:** ✓ Visibles (diagramas SVG→PNG embebidas)
- **Tablas:** ✓ Renderizadas con bordes
- **[PENDIENTE]:** ✗ No encontrado
- **CARGA_CIERRE:** ✗ No encontrado
- **[COMPLETAR]:** 18 ocurrencias (ver abajo)

### Contenido problemático

El PDF contiene **18 marcadores `[COMPLETAR]`** que deben reemplazarse en el MD fuente antes de entregar al aula virtual:

```
[COMPLETAR: fecha de entrega DD/MM/AAAA — ver PASOS_MANUALES paso 1]
[COMPLETAR: apellidos y nombres del docente — ver PASOS_MANUALES paso 1]
[COMPLETAR: código de alumno — ver PASOS_MANUALES paso 1] (x 3 integrantes)
[COMPLETAR: confirmar o corregir el mapeo de roles...]
[COMPLETAR: texto descriptivo] (otros campos)
```

**Estado:** El PDF actual es un BORRADOR y no está listo para subir al aula virtual mientras contiene estos marcadores.

## Script reproducible

Se creó `herramientas/conversion/exportar_s6.py` con las siguientes características:

- **Entrada:** MD con referencias SVG relativas
- **Proceso:** Copia temporal, reemplazo de rutas, pandoc → DOCX/HTML, Edge headless → PDF
- **Salida:** DOCX y PDF en `exportados/semana-06/`
- **Limpieza:** Archivos temporales removidos
- **Validación:** Reporte de tamaños y páginas

**Comando reproducible:**

```powershell
cd D:\Workspace\IngenieriaWeb\Grupal\semana6\ProcesosSoftwareAnemia
.\herramientas\.venv\Scripts\python.exe .\herramientas\conversion\exportar_s6.py
```

**O con PowerShell:**

```powershell
cd D:\Workspace\...\ProcesosSoftwareAnemia
& .\herramientas\.venv\Scripts\python.exe `
  .\herramientas\conversion\exportar_s6.py
```

## Archivos generados

| Archivo | Tamaño | Ubicación | Notas |
| --- | --- | --- | --- |
| `Informe_Integrador_Anemia_Junin.docx` | 5.8 MB | `exportados/semana-06/` | Apto para edición en Word |
| `Informe_Integrador_Anemia_Junin.pdf` | 7.2 MB (50 pp.) | `exportados/semana-06/` | Contiene 18 `[COMPLETAR]` |
| `Presentacion_Integrador_Anemia_Junin.pdf` | 1.8 MB | `exportados/semana-06/` | Convertido de PPTX |

## Problemas y mitigación

| Problema | Impacto | Solución |
| --- | --- | --- |
| Pandoc no instalado | Bloqueante | Usar `pypandoc_binary` desde PyPI |
| SVG no renderiza bien en Word | DOCX poco legible | Reemplazar por PNG en copia temporal del MD |
| PDF con marcadores `[COMPLETAR]` | No apto para entrega | Actualizar MD fuente y regenerar |
| Edge no encuentra rutas relativas | PDF vacío potencial | Usar `--embed-resources` en pandoc HTML |

## Próximos pasos

1. **Equipo de redacción:** Completar los campos `[COMPLETAR]` en:
   - `entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md`
   
2. **Regeneración:** Ejecutar nuevamente el script una vez completados:
   ```powershell
   .\herramientas\.venv\Scripts\python.exe .\herramientas\conversion\exportar_s6.py
   ```

3. **Validación:** Verificar que el nuevo PDF no contiene `[COMPLETAR]`:
   ```powershell
   .\herramientas\.venv\Scripts\python.exe -c "
   from pypdf import PdfReader
   reader = PdfReader('exportados/semana-06/Informe_Integrador_Anemia_Junin.pdf')
   text = ''.join(p.extract_text() for p in reader.pages)
   count = text.count('[COMPLETAR')
   print(f'[COMPLETAR] found: {count}')
   "
   ```

4. **Entrega:** Una vez que los archivos estén limpios (sin marcadores), subirlos al aula virtual.

## Criterios de terminado

- [x] DOCX generado y abre sin errores
- [x] PDF generado y contiene todas las secciones
- [x] Imágenes visibles en PDF
- [x] Script reproducible en `herramientas/conversion/exportar_s6.py`
- [x] Informe de validación generado
- [ ] PDF sin marcadores `[COMPLETAR]` ← **Pendiente en MD fuente**

## Observaciones

1. **Calidad de imágenes:** Las imágenes (diagramas SVG convertidos a PNG) se ven correctas en ambos formatos (DOCX y PDF).

2. **Tablas:** Las tablas con múltiples columnas se renderizan adecuadamente en ambos formatos.

3. **Tipografía:** Serif académica en PDF (via HTML), proporción helvetica en DOCX.

4. **Tamaños:** Los archivos están en rangos normales para documentos de 50 pp. con 12 imágenes embebidas.

5. **Presentación:** El PDF de la presentación se generó correctamente desde PPTX con PowerPoint COM.

---

**Generado por:** conversor-entregas (Claude Haiku 4.5)  
**Comando:** `exportar_s6.py`  
**Estado:** ✓ Archivos generados | ⚠ Requiere limpieza de `[COMPLETAR]` en MD fuente
