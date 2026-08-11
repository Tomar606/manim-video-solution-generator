# Set this machine up to run the pipeline natively (Windows).
#
# Run from PowerShell in the repo root:
#     powershell -ExecutionPolicy Bypass -File .\bin\bootstrap.ps1
#
# Docker is the other option and needs none of this — see README. This path is
# faster to render on and doesn't need Docker Desktop, but LaTeX is a big
# install, so leave it time on the first run.

param([switch]$Check)

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

function Ok($m)   { Write-Host "  [ok]   $m" -ForegroundColor Green }
function Warn($m) { Write-Host "  [warn] $m" -ForegroundColor Yellow }
function Bad($m)  { Write-Host "  [MISS] $m" -ForegroundColor Red }
function Have($c) { $null -ne (Get-Command $c -ErrorAction SilentlyContinue) }

Write-Host "Video pipeline - native setup (Windows)"
Write-Host "======================================="

# --- Python ---------------------------------------------------------------
# Manim 0.18 does not build on 3.13+, so we need 3.10-3.12 specifically.
$py = $null
foreach ($cand in @("python3.12", "python3.11", "python3.10", "python")) {
    if (Have $cand) {
        $v = & $cand -c "import sys;print('%d.%d'%sys.version_info[:2])" 2>$null
        if ($v -in @("3.10", "3.11", "3.12")) { $py = $cand; break }
    }
}
if (-not $py -and (Have "py")) {
    foreach ($v in @("3.12", "3.11", "3.10")) {
        & py "-$v" -c "1" 2>$null
        if ($LASTEXITCODE -eq 0) { $py = "py -$v"; break }
    }
}
if (-not $py) {
    Bad "No Python 3.10-3.12 found (Manim 0.18 does not support 3.13+)."
    Write-Host "     winget install Python.Python.3.12"
    exit 1
}
Ok "python: $py"

# --- system tools ---------------------------------------------------------
$missing = @()
if (Have "ffmpeg") { Ok "ffmpeg" } else { Bad "ffmpeg missing"; $missing += "ffmpeg" }
if ((Have "latex") -or (Have "pdflatex")) { Ok "latex" }
else { Bad "LaTeX missing (equations will not render)"; $missing += "latex" }
if (Have "node")   { Ok "node" }   else { Warn "node missing (needed for the Claude CLI)" }
if (Have "claude") { Ok "claude CLI" } else { Warn "claude CLI missing" }

if ($missing.Count -gt 0) {
    Write-Host ""
    Write-Host "Install the missing pieces (then reopen PowerShell so PATH updates):"
    if ($missing -contains "ffmpeg") { Write-Host "  winget install Gyan.FFmpeg" }
    if ($missing -contains "latex")  { Write-Host "  winget install MiKTeX.MiKTeX" }
}
if (-not (Have "claude")) {
    Write-Host ""
    Write-Host "For Claude access on your subscription (no API key needed):"
    Write-Host "  npm install -g @anthropic-ai/claude-code"
    Write-Host "  claude          # log in once"
}

if ($Check) { Write-Host ""; Write-Host "Check complete."; exit 0 }

# --- venv -----------------------------------------------------------------
Write-Host ""
if (-not (Test-Path ".venv")) {
    Write-Host "Creating .venv ..."
    Invoke-Expression "$py -m venv .venv"
}
$venvPy = ".\.venv\Scripts\python.exe"
& $venvPy -m pip install --quiet --upgrade pip
Write-Host "Installing Python dependencies (a few minutes the first time)..."
& $venvPy -m pip install --quiet -r requirements.txt
Ok "dependencies installed"

# --- env ------------------------------------------------------------------
if ((-not (Test-Path ".env")) -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
    Ok ".env created from .env.example - add your ELEVENLABS_API_KEY"
}

# --- sound effects --------------------------------------------------------
& $venvPy video.py sfx *> $null
if ($LASTEXITCODE -eq 0) { Ok "sound effect library built" }
else { Warn "could not build the sound effects (ffmpeg?)" }

Write-Host ""
Write-Host "======================================="
& $venvPy video.py doctor
Write-Host ""
Write-Host "Ready. Try:"
Write-Host "  .\bin\video.ps1 dashboard"
Write-Host '  .\bin\video.ps1 new "Deriving the quadratic formula"'
