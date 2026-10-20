Set-Location (Join-Path $PSScriptRoot '..')
$env:PATH = "C:\msys64\clang64\bin;$env:PATH"
$p = Start-Process -FilePath out\gpu\jstars_pc.exe -ArgumentList "out\boot-linked.bin","--app0","extracted_game\app0","--import-names","out\import_names.txt" -RedirectStandardOutput out\shot.log -RedirectStandardError out\shot.err -PassThru -NoNewWindow
Add-Type -AssemblyName System.Drawing, System.Windows.Forms
foreach ($s in 25, 45, 70) {
    Start-Sleep -Seconds ($s - $(if ($prev) { $prev } else { 0 })); $prev = $s
    $b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
    $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($b.Location, [System.Drawing.Point]::Empty, $b.Size)
    $bmp.Save("out\shot_$s.png"); $g.Dispose(); $bmp.Dispose()
}
if (!$p.HasExited) { $p.Kill() }
"done"
