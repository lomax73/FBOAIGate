import socket

import asyncssh
from django.conf import settings
from django.utils import timezone

SSH_PORT = 22
CHECK_TIMEOUT_SECONDS = 1.5
RESOURCE_USAGE_COMMAND = "cat /proc/loadavg && echo '---' && free -m && echo '---' && df -h /"


def refresh_target_status(target) -> bool:
    """Controlla se il Target risponde sulla porta SSH attraverso il tunnel
    WireGuard e aggiorna `online`/`ultimo_contatto` di conseguenza.

    Va eseguito da un host che ha davvero una rotta verso `vpn_ip` (l'hub
    stesso, in produzione) — da un Mac di sviluppo fuori dalla VPN risulterà
    sempre offline, per costruzione."""
    reachable = _tcp_check(target.vpn_ip, SSH_PORT)
    updates = {'online': reachable}
    if reachable:
        updates['ultimo_contatto'] = timezone.now()
    for field, value in updates.items():
        setattr(target, field, value)
    target.save(update_fields=list(updates.keys()))
    return reachable


def _tcp_check(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=CHECK_TIMEOUT_SECONDS):
            return True
    except OSError:
        return False


async def fetch_resource_usage(target) -> dict:
    """Apre una breve sessione SSH sul Target (stessa chiave di servizio della
    console) e legge carico/memoria/disco. Una connessione ad-hoc per
    chiamata: va bene per un pannello aggiornato ogni tot secondi su un
    numero di host contenuto, non pensata per il polling di molti host."""
    async with asyncssh.connect(
        target.vpn_ip,
        username=target.ssh_user,
        client_keys=[settings.CONSOLE_SSH_PRIVATE_KEY_PATH],
        known_hosts=None,
    ) as conn:
        result = await conn.run(RESOURCE_USAGE_COMMAND, check=True)
    return _parse_resource_usage(result.stdout)


def _parse_resource_usage(output: str) -> dict:
    loadavg_section, free_section, df_section = output.split('---')

    load1, load5, load15 = loadavg_section.split()[:3]

    mem_line = next(line for line in free_section.splitlines() if line.startswith('Mem:'))
    _, mem_total, mem_used, mem_free = mem_line.split()[:4]

    df_line = [line for line in df_section.strip().splitlines() if line][-1]
    _, disk_size, disk_used, disk_avail, disk_percent = df_line.split()[:5]

    return {
        'load': {'1min': float(load1), '5min': float(load5), '15min': float(load15)},
        'memory': {'total_mb': int(mem_total), 'used_mb': int(mem_used), 'free_mb': int(mem_free)},
        'disk': {'size': disk_size, 'used': disk_used, 'avail': disk_avail, 'percent': disk_percent},
    }
