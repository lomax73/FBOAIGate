import socket

from django.utils import timezone

SSH_PORT = 22
CHECK_TIMEOUT_SECONDS = 1.5


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
