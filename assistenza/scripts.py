"""Generatori degli script di onboarding RustDesk per i PC dei clienti.

Gli script installano il client, lo puntano al server self-hosted e impostano
una password permanente casuale, poi stampano ID e password: vanno annotati
dall'operatore (la password non viene mai trasmessa a FBOAIGate).
"""
import re

from django.conf import settings

_SAFE = re.compile(r'[^A-Za-z0-9._ -]')


def _server_values():
    return {
        'id_server': settings.RUSTDESK_ID_SERVER,
        'relay_server': settings.RUSTDESK_RELAY_SERVER or settings.RUSTDESK_ID_SERVER,
        'key': settings.RUSTDESK_PUBLIC_KEY,
    }


def is_configured():
    return bool(settings.RUSTDESK_ID_SERVER and settings.RUSTDESK_PUBLIC_KEY)


def windows_script():
    v = _server_values()
    return f'''# Onboarding RustDesk (FBOAIGate) - eseguire come Amministratore.
# powershell -ExecutionPolicy Bypass -File fbo-rustdesk-windows.ps1
$ErrorActionPreference = 'Stop'
$IdServer    = '{v["id_server"]}'
$RelayServer = '{v["relay_server"]}'
$Key         = '{v["key"]}'

$tmp = Join-Path $env:TEMP 'rustdesk-setup.exe'
$release = Invoke-RestMethod 'https://api.github.com/repos/rustdesk/rustdesk/releases/latest'
$asset = $release.assets | Where-Object {{ $_.name -match 'x86_64\\.exe$' }} | Select-Object -First 1
if (-not $asset) {{ throw 'Installer RustDesk non trovato nella release.' }}
Write-Host "Scarico $($asset.name)"
Invoke-WebRequest $asset.browser_download_url -OutFile $tmp

# Niente "-Wait": l'installer lascia RustDesk avviato come processo figlio e
# Start-Process -Wait aspetterebbe anche quello, bloccandosi per sempre.
$exe = Join-Path ${{env:ProgramFiles}} 'RustDesk\\rustdesk.exe'
Write-Host 'Installo RustDesk...'
$inst = Start-Process $tmp -ArgumentList '--silent-install' -PassThru
for ($i = 0; $i -lt 60; $i++) {{
    if ((Test-Path $exe) -and (Get-Service -Name RustDesk -ErrorAction SilentlyContinue)) {{ break }}
    Start-Sleep -Seconds 2
}}
if (-not (Test-Path $exe)) {{ throw 'RustDesk non risulta installato.' }}
Start-Sleep -Seconds 5

# rustdesk.exe e' un'app grafica: lanciato direttamente puo' non restituire mai il
# controllo. Ogni chiamata passa da qui, con timeout.
function Invoke-Rd {{
    param([string[]]$ArgList, [int]$TimeoutSec = 20)
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $exe
    $psi.Arguments = ($ArgList | ForEach-Object {{ '"' + $_ + '"' }}) -join ' '
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardOutput = $true
    $p = [System.Diagnostics.Process]::Start($psi)
    if (-not $p.WaitForExit($TimeoutSec * 1000)) {{ try {{ $p.Kill() }} catch {{}}; return '' }}
    return $p.StandardOutput.ReadToEnd().Trim()
}}

Write-Host 'Configuro il server...'
Invoke-Rd @('--option', 'custom-rendezvous-server', $IdServer) | Out-Null
Invoke-Rd @('--option', 'relay-server', $RelayServer) | Out-Null
Invoke-Rd @('--option', 'key', $Key) | Out-Null

$chars = (48..57) + (65..90) + (97..122)
$Password = -join ($chars | Get-Random -Count 16 | ForEach-Object {{ [char]$_ }})
Invoke-Rd @('--password', $Password) | Out-Null

# La password si stampa subito: se il resto si blocca, non va persa.
Write-Host ''
Write-Host '=== ANNOTA QUESTI DATI ==='
Write-Host "Password    : $Password"

Restart-Service -Name RustDesk -ErrorAction SilentlyContinue
Start-Sleep -Seconds 4

$Id = ''
for ($i = 0; $i -lt 8 -and -not $Id; $i++) {{
    $Id = Invoke-Rd @('--get-id') 10
    if (-not $Id) {{ Start-Sleep -Seconds 2 }}
}}
if (-not $Id) {{
    # Riserva: legge l'ID dal file di configurazione del servizio
    $files = @(
        "$env:WINDIR\\ServiceProfiles\\LocalService\\AppData\\Roaming\\RustDesk\\config\\RustDesk.toml",
        "$env:APPDATA\\RustDesk\\config\\RustDesk.toml"
    )
    foreach ($f in $files) {{
        if (Test-Path $f) {{
            $m = Select-String -Path $f -Pattern "^id\\s*=\\s*'([^']+)'" | Select-Object -First 1
            if ($m) {{ $Id = $m.Matches[0].Groups[1].Value; break }}
        }}
    }}
}}
if (-not $Id) {{ $Id = '(non letto: aprire RustDesk e copiare l ID mostrato)' }}
Write-Host "ID RustDesk : $Id"
Write-Host ''
Write-Host 'Fatto. Questa finestra si puo chiudere.'
'''


def linux_script():
    v = _server_values()
    return f'''#!/usr/bin/env bash
# Onboarding RustDesk (FBOAIGate) - eseguire come root su Debian/Ubuntu (x86_64).
set -euo pipefail
[[ "$EUID" -eq 0 ]] || {{ echo "Esegui come root (sudo)." >&2; exit 1; }}

ID_SERVER='{v["id_server"]}'
RELAY_SERVER='{v["relay_server"]}'
KEY='{v["key"]}'

apt-get update -qq
apt-get install -y -qq curl ca-certificates
URL=$(curl -fsSL https://api.github.com/repos/rustdesk/rustdesk/releases/latest \\
  | grep -oE 'https://[^"]+x86_64\\.deb' | head -n1)
[[ -n "$URL" ]] || {{ echo "Pacchetto .deb non trovato." >&2; exit 1; }}
curl -fsSL "$URL" -o /tmp/rustdesk.deb
apt-get install -y -qq /tmp/rustdesk.deb
rm -f /tmp/rustdesk.deb

rustdesk --option custom-rendezvous-server "$ID_SERVER"
rustdesk --option relay-server "$RELAY_SERVER"
rustdesk --option key "$KEY"

PASSWORD=$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c16)
rustdesk --password "$PASSWORD"
systemctl enable --now rustdesk >/dev/null 2>&1 || true
systemctl restart rustdesk >/dev/null 2>&1 || true
sleep 3
ID=$(rustdesk --get-id)

echo
echo "=== ANNOTA QUESTI DATI ==="
echo "ID RustDesk : $ID"
echo "Password    : $PASSWORD"
'''
