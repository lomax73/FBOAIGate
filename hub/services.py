import stat as stat_module
import socket

import asyncssh
from django.conf import settings
from django.utils import timezone

SSH_PORT = 22
CHECK_TIMEOUT_SECONDS = 1.5
RESOURCE_USAGE_COMMAND = (
    "cat /proc/loadavg && echo '---' && free -m && echo '---' && df -h / "
    "&& echo '---' && (grep '^PRETTY_NAME=' /etc/os-release 2>/dev/null || uname -sr) "
    "&& echo '---' && cat /proc/uptime "
    # Sensore termico non garantito (tipicamente assente sulle VPS
    # virtualizzate, presente su hardware fisico come il NUC): riga vuota se
    # manca, gestita come "n/d" invece di inventare un valore.
    "&& echo '---' && (cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo '')"
)


def _connect(target):
    """Apre una connessione SSH verso il Target con la chiave di servizio
    della console. Va usata come `async with`."""
    return asyncssh.connect(
        target.vpn_ip,
        username=target.ssh_user,
        client_keys=[settings.CONSOLE_SSH_PRIVATE_KEY_PATH],
        known_hosts=None,
    )


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
    async with _connect(target) as conn:
        result = await conn.run(RESOURCE_USAGE_COMMAND, check=True)
    return _parse_resource_usage(result.stdout)


def _parse_resource_usage(output: str) -> dict:
    loadavg_section, free_section, df_section, os_section, uptime_section, temp_section = output.split('---')

    load1, load5, load15 = loadavg_section.split()[:3]

    mem_line = next(line for line in free_section.splitlines() if line.startswith('Mem:'))
    _, mem_total, mem_used, mem_free = mem_line.split()[:4]

    df_line = [line for line in df_section.strip().splitlines() if line][-1]
    _, disk_size, disk_used, disk_avail, disk_percent = df_line.split()[:5]

    return {
        'load': {'1min': float(load1), '5min': float(load5), '15min': float(load15)},
        'memory': {'total_mb': int(mem_total), 'used_mb': int(mem_used), 'free_mb': int(mem_free)},
        'disk': {'size': disk_size, 'used': disk_used, 'avail': disk_avail, 'percent': disk_percent},
        'os': _parse_os(os_section),
        'uptime': _parse_uptime(uptime_section),
        'temperature_c': _parse_temperature(temp_section),
    }


def _parse_os(section: str) -> str:
    """PRETTY_NAME="Ubuntu 22.04.3 LTS" da /etc/os-release, oppure l'output
    di `uname -sr` (es. "Linux 5.15.0-92-generic") se /etc/os-release manca."""
    line = section.strip().splitlines()[0] if section.strip() else ''
    if line.startswith('PRETTY_NAME='):
        return line.split('=', 1)[1].strip().strip('"')
    return line


def _parse_uptime(section: str) -> str:
    """/proc/uptime: secondi dall'avvio (primo campo) in formato leggibile."""
    seconds = int(float(section.split()[0]))
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60
    parts = []
    if days:
        parts.append(f'{days}g')
    if hours or days:
        parts.append(f'{hours}h')
    parts.append(f'{minutes}min')
    return ' '.join(parts)


def _parse_temperature(section: str) -> float | None:
    """thermal_zone0/temp è in millesimi di grado. None se il sensore non
    è disponibile (comune sulle VPS virtualizzate) invece di un valore
    inventato — il chiamante lo mostra come "n/d"."""
    raw = section.strip()
    if not raw:
        return None
    return round(int(raw) / 1000, 1)


async def sftp_list_dir(target, path: str) -> dict:
    """Elenca il contenuto di una cartella remota via SFTP. Path vuoto =
    home dell'utente `ssh_user` sul Target."""
    async with _connect(target) as conn:
        async with conn.start_sftp_client() as sftp:
            real_path = await sftp.realpath(path or '.')
            entries = []
            for entry in await sftp.readdir(real_path):
                if entry.filename in ('.', '..'):
                    continue
                is_dir = stat_module.S_ISDIR(entry.attrs.permissions)
                entries.append({
                    'name': entry.filename,
                    'is_dir': is_dir,
                    'size': None if is_dir else entry.attrs.size,
                })
            entries.sort(key=lambda e: (not e['is_dir'], e['name'].lower()))
            return {'path': real_path, 'entries': entries}


async def sftp_mkdir(target, path: str) -> None:
    async with _connect(target) as conn:
        async with conn.start_sftp_client() as sftp:
            await sftp.mkdir(path)


async def sftp_delete(target, path: str) -> None:
    """Elimina un file, o una cartella (ricorsivamente se non vuota)."""
    async with _connect(target) as conn:
        async with conn.start_sftp_client() as sftp:
            attrs = await sftp.stat(path)
            if stat_module.S_ISDIR(attrs.permissions):
                await sftp.rmtree(path)
            else:
                await sftp.remove(path)


async def sftp_upload(target, remote_dir: str, filename: str, django_file) -> None:
    remote_path = remote_dir.rstrip('/') + '/' + filename
    async with _connect(target) as conn:
        async with conn.start_sftp_client() as sftp:
            async with sftp.open(remote_path, 'wb') as remote_f:
                for chunk in django_file.chunks():
                    await remote_f.write(chunk)
