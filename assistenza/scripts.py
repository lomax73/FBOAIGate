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

Start-Process $tmp -ArgumentList '--silent-install' -Wait
Start-Sleep -Seconds 8
$exe = Join-Path ${{env:ProgramFiles}} 'RustDesk\\rustdesk.exe'
if (-not (Test-Path $exe)) {{ throw 'RustDesk non risulta installato.' }}

& $exe --option custom-rendezvous-server $IdServer
& $exe --option relay-server $RelayServer
& $exe --option key $Key

$chars = (48..57) + (65..90) + (97..122)
$Password = -join ($chars | Get-Random -Count 16 | ForEach-Object {{ [char]$_ }})
& $exe --password $Password
Restart-Service -Name RustDesk -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
$Id = (& $exe --get-id | Out-String).Trim()

Write-Host ''
Write-Host '=== ANNOTA QUESTI DATI ==='
Write-Host "ID RustDesk : $Id"
Write-Host "Password    : $Password"
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
