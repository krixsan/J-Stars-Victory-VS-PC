$ErrorActionPreference = 'Continue'
Set-Location (Join-Path $PSScriptRoot '..')
$env:PATH = "C:\msys64\clang64\bin;$env:PATH"

$hasTimeout = ($args.Count -gt 0 -and [int]::TryParse($args[0], [ref]$null))
$exePath = if (Test-Path "out\jstars_pc.exe") { "out\jstars_pc.exe" } else { "out\gpu\jstars_pc.exe" }

if ($hasTimeout) {
    $t = [int]$args[0]
    $argList = @("out\boot-linked.bin", "--app0", "extracted_game\app0", "--import-names", "out\import_names.txt", "--timeout", "$t")
    $p = Start-Process -FilePath $exePath -ArgumentList $argList -RedirectStandardOutput out\run.log -RedirectStandardError out\run.err -PassThru -NoNewWindow
    $p | Wait-Process -Timeout ($t + 10) -ErrorAction SilentlyContinue
    if (!$p.HasExited) { $p.Kill(); "killed after timeout ($t s)" }
    "exit: $($p.ExitCode)"
    Get-Content out\run.log | Where-Object { $_ -notmatch 'CollectImageFormatInfo|Guest event wait' } | Select-Object -Last 70
    Get-Content out\run.err -Tail 20
} else {
    Write-Host "Starting J-Stars Victory VS+ PC with NO TIMEOUT (unlimited execution)..." -ForegroundColor Cyan
    $argList = @("out\boot-linked.bin", "--app0", "extracted_game\app0", "--import-names", "out\import_names.txt")
    $p = Start-Process -FilePath $exePath -ArgumentList $argList -PassThru
    $p.WaitForExit()
    "exit: $($p.ExitCode)"
}
