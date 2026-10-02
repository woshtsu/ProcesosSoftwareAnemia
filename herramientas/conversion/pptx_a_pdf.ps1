# pptx_a_pdf.ps1
# Convierte la presentación S6 de PPTX a PDF con PowerPoint (automatización COM).
# Requiere: Microsoft PowerPoint instalado (Windows). No instala nada.
# Uso (desde la raíz del repositorio):
#   powershell -ExecutionPolicy Bypass -File .\herramientas\conversion\pptx_a_pdf.ps1
#   powershell -ExecutionPolicy Bypass -File .\herramientas\conversion\pptx_a_pdf.ps1 -Pptx otra.pptx -Pdf otra.pdf

param(
    [string]$Pptx = "exportados\semana-06\Presentacion_Integrador_Anemia_Junin.pptx",
    [string]$Pdf = "exportados\semana-06\Presentacion_Integrador_Anemia_Junin.pdf"
)

$ErrorActionPreference = "Stop"

# PowerPoint COM exige rutas absolutas
$pptxAbs = [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $Pptx))
$pdfAbs = [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $Pdf))

if (-not (Test-Path $pptxAbs)) {
    Write-Error "No se encontró el PPTX: $pptxAbs"
    exit 1
}

$ppSaveAsPDF = 32   # PpSaveAsFileType.ppSaveAsPDF
$msoTrue = -1
$msoFalse = 0

$ppt = $null
$pres = $null
$codigo = 0

try {
    Write-Host "Abriendo PowerPoint..."
    $ppt = New-Object -ComObject PowerPoint.Application

    Write-Host "Abriendo $pptxAbs"
    # Open(FileName, ReadOnly, Untitled, WithWindow)
    $pres = $ppt.Presentations.Open($pptxAbs, $msoTrue, $msoFalse, $msoFalse)

    Write-Host "Guardando PDF en $pdfAbs"
    $pres.SaveAs($pdfAbs, $ppSaveAsPDF)

    if (Test-Path $pdfAbs) {
        $mb = (Get-Item $pdfAbs).Length / 1MB
        Write-Host ("PDF generado: {0} ({1:N1} MB)" -f $pdfAbs, $mb)
    } else {
        Write-Error "PowerPoint no generó el PDF."
        $codigo = 1
    }
}
catch {
    Write-Host ("Error en la conversión: {0}" -f $_)
    $codigo = 1
}
finally {
    if ($pres) {
        try { $pres.Close() } catch { }
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($pres)
    }
    if ($ppt) {
        try { $ppt.Quit() } catch { }
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

exit $codigo
