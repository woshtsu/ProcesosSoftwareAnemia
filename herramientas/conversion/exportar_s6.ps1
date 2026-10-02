# exportar_s6.ps1
# Conversor reproducible: Markdown -> DOCX + PDF para S6 Integrador
# Requiere: pypandoc_binary (instalado en herramientas\.venv), Edge browser
# Uso: cd herramientas && .\.venv\Scripts\python.exe -c "import pypandoc_binary"
#      cd ..\.. && .\herramientas\conversion\exportar_s6.ps1

param(
    [string]$RepoRoot = (Get-Location).Path,
    [string]$VenvPath = "$RepoRoot\herramientas\.venv",
    [string]$PandocBinary = "$VenvPath\Scripts\pandoc.exe"
)

$ErrorActionPreference = "Stop"

# Función para ejecutar comandos con el venv
function Invoke-Venv {
    param([string]$Script)
    $PythonExe = "$VenvPath\Scripts\python.exe"
    & $PythonExe -c $Script
}

# Rutas
$EntregableDir = "$RepoRoot\entregables\semana-06-integrador"
$BuildDir = "$RepoRoot\diagramas\_build\conversion"
$ExportDir = "$RepoRoot\exportados\semana-06"
$TempMD = "$BuildDir\Informe_Integrador_Anemia_Junin_temp.md"
$DiagramasDir = "$RepoRoot\diagramas"

Write-Host "=== CONVERSOR S6: MD -> DOCX + PDF ===" -ForegroundColor Cyan
Write-Host "Repo: $RepoRoot"
Write-Host "Venv: $VenvPath"
Write-Host ""

# Verificar que el MD existe
if (-not (Test-Path "$EntregableDir\Informe_Integrador_Anemia_Junin.md")) {
    Write-Error "Informe MD no encontrado en $EntregableDir"
    exit 1
}

Write-Host "[1/5] Copiando Informe a directorio temporal..." -ForegroundColor Yellow
Copy-Item "$EntregableDir\Informe_Integrador_Anemia_Junin.md" -Destination $TempMD -Force

Write-Host "[2/5] Reemplazando referencias SVG -> PNG..." -ForegroundColor Yellow
$Content = Get-Content $TempMD -Encoding UTF8 -Raw
$Content = $Content -replace '\.svg\)', '.png)'
$Content = $Content -replace 'diagramas/svg/', 'diagramas/png/'
Set-Content $TempMD -Value $Content -Encoding UTF8

Write-Host "[3/5] Generando DOCX..." -ForegroundColor Yellow
Push-Location $EntregableDir
try {
    $PandocScript = @"
import pypandoc
import os
os.chdir(r'$EntregableDir')
output = pypandoc.convert_file(
    r'$TempMD',
    'docx',
    outputfile=r'$ExportDir\Informe_Integrador_Anemia_Junin.docx',
    extra_args=['--toc', '--resource-path=.;../..', '--default-image-extension=png']
)
print(f'DOCX generated: {output}')
"@
    Invoke-Venv $PandocScript
} finally {
    Pop-Location
}

Write-Host "[4/5] Generando PDF (HTML + Edge)..." -ForegroundColor Yellow
$PdfScript = @"
import pypandoc
import os
import subprocess
os.chdir(r'$EntregableDir')

# Generar HTML intermedio
html_file = r'$BuildDir\Informe_temp.html'
pypandoc.convert_file(
    r'$TempMD',
    'html',
    outputfile=html_file,
    extra_args=['--toc', '--standalone', '--embed-resources', '--resource-path=.;../..', '--default-image-extension=png']
)

# Imprimir a PDF con Edge
pdf_file = r'$ExportDir\Informe_Integrador_Anemia_Junin.pdf'
edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

if not os.path.exists(edge_path):
    # Intentar ruta alternativa
    edge_path = r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'

if os.path.exists(edge_path):
    cmd = [
        edge_path,
        '--headless',
        '--disable-gpu',
        f'--print-to-pdf={pdf_file}',
        '--no-pdf-header-footer',
        html_file
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f'PDF generated: {pdf_file}')
    else:
        print(f'Error generating PDF: {result.stderr}')
        raise Exception(f'Edge headless failed: {result.returncode}')
else:
    raise Exception('Microsoft Edge not found')
"@
    Invoke-Venv $PdfScript
}

Write-Host "[5/5] Validando archivos..." -ForegroundColor Yellow

# Verificar que existen
if ((Test-Path "$ExportDir\Informe_Integrador_Anemia_Junin.docx") -and
    (Test-Path "$ExportDir\Informe_Integrador_Anemia_Junin.pdf")) {

    $DocxSize = (Get-Item "$ExportDir\Informe_Integrador_Anemia_Junin.docx").Length
    $PdfSize = (Get-Item "$ExportDir\Informe_Integrador_Anemia_Junin.pdf").Length

    Write-Host ""
    Write-Host "=== ÉXITO ===" -ForegroundColor Green
    Write-Host "DOCX: $ExportDir\Informe_Integrador_Anemia_Junin.docx ($($DocxSize / 1MB -as [int]) MB)"
    Write-Host "PDF: $ExportDir\Informe_Integrador_Anemia_Junin.pdf ($($PdfSize / 1MB -as [int]) MB)"
    Write-Host ""

    # Verificar número de páginas del PDF
    $PdfInfoScript = @"
import os
try:
    from pypdf import PdfReader
    pdf_path = r'$ExportDir\Informe_Integrador_Anemia_Junin.pdf'
    if os.path.exists(pdf_path):
        reader = PdfReader(pdf_path)
        pages = len(reader.pages)
        print(f'PDF pages: {pages}')
    else:
        print('PDF not found')
except ImportError:
    print('pypdf not installed; run: pip install pypdf')
except Exception as e:
    print(f'Error reading PDF: {e}')
"@
    Invoke-Venv $PdfInfoScript

    Write-Host "Archivos generados en: $ExportDir" -ForegroundColor Green
} else {
    Write-Error "Falló la generación de archivos."
    exit 1
}

# Limpiar archivos temporales
Remove-Item $TempMD -Force -ErrorAction SilentlyContinue
Remove-Item "$BuildDir\Informe_temp.html" -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Nota: Los archivos contienen [COMPLETAR] que deben reemplazarse manualmente o en el MD fuente." -ForegroundColor Yellow
