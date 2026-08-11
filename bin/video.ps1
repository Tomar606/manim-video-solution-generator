# Run the pipeline on Windows, wherever it happens to be installed.
#
#   .\bin\video.ps1 dashboard
#   .\bin\video.ps1 new "Deriving the quadratic formula"
#   .\bin\video.ps1 build quadratic-formula
#
# Force one runtime with $env:VIDEO_RUNTIME = "venv" | "docker" | "system".

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

$venvPy = ".\.venv\Scripts\python.exe"
$runtime = if ($env:VIDEO_RUNTIME) { $env:VIDEO_RUNTIME } else { "auto" }

function Venv-HasManim {
    if (-not (Test-Path $venvPy)) { return $false }
    & $venvPy -c "import manim" 2>$null
    return ($LASTEXITCODE -eq 0)
}
function Docker-Ok {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { return $false }
    docker info *> $null
    return ($LASTEXITCODE -eq 0)
}

switch ($runtime) {
    "venv"   { & $venvPy video.py @args; exit $LASTEXITCODE }
    "system" { & python video.py @args;  exit $LASTEXITCODE }
    "docker" { & docker compose run --rm --service-ports app python video.py @args; exit $LASTEXITCODE }
}

# Stages that don't need Manim still work in a partial venv.
$lightStages = @("new","script","status","doctor","dashboard","avatar","sfx")

if (Venv-HasManim) {
    & $venvPy video.py @args
} elseif ((Test-Path $venvPy) -and ($args.Count -gt 0) -and ($lightStages -contains $args[0])) {
    & $venvPy video.py @args
} elseif (Docker-Ok) {
    Write-Host "-> running in Docker (no local Manim)" -ForegroundColor Yellow
    & docker compose run --rm --service-ports app python video.py @args
} else {
    Write-Host "No runtime found. Set one up first:" -ForegroundColor Red
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\bin\bootstrap.ps1"
    Write-Host "  docker compose build"
    exit 1
}
exit $LASTEXITCODE
