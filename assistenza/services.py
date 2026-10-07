"""Stato online/offline dei PC clienti, interrogando il server RustDesk (hbbs).

L'hbbs open source non espone un'API di stato. Si usa lo stesso meccanismo del
client: una richiesta di connessione (PunchHoleRequest, TCP 21116, con la chiave
del server) a cui hbbs risponde subito "OFFLINE" / "ID_NOT_EXIST" se il PC non si
è registrato di recente. Nessuna risposta di errore = il PC è online.
Il controllo si fa solo quando l'operatore apre la lista, non c'è polling.
"""
import asyncio

from django.conf import settings

HBBS_PORT = 21116
TIMEOUT = 2.5

# RendezvousMessage: punch_hole_request = 8, punch_hole_response = 11
# PunchHoleResponse.failure (campo 3): ID_NOT_EXIST=0 (omesso), OFFLINE=2, LICENSE_MISMATCH=3
_FAIL_OFFLINE = 2
_FAIL_LICENSE = 3


def _varint(n):
    out = b''
    while True:
        b = n & 0x7F
        n >>= 7
        out += bytes([b | (0x80 if n else 0)])
        if not n:
            return out


def _field_ld(num, data):
    return _varint(num << 3 | 2) + _varint(len(data)) + data


def _field_vi(num, value):
    return _varint(num << 3) + _varint(value)


def _frame(msg):
    """Framing del bytes_codec di RustDesk: lunghezza<<2 con 1-2 byte di testa."""
    n = len(msg)
    if n < 0x40:
        return bytes([n << 2]) + msg
    return ((n << 2) | 1).to_bytes(2, 'little') + msg


def _read_varint(buf, i):
    shift = result = 0
    while True:
        b = buf[i]
        i += 1
        result |= (b & 0x7F) << shift
        if not b & 0x80:
            return result, i
        shift += 7


def _parse(buf):
    """Decodifica minimale di un messaggio protobuf: {campo: valore (int o bytes)}."""
    fields, i = {}, 0
    while i < len(buf):
        tag, i = _read_varint(buf, i)
        num, wire = tag >> 3, tag & 7
        if wire == 0:
            fields[num], i = _read_varint(buf, i)
        elif wire == 2:
            ln, i = _read_varint(buf, i)
            fields[num] = buf[i:i + ln]
            i += ln
        else:
            raise ValueError('wire type non gestito')
    return fields


def _classify(payload):
    """True = online, False = offline, None = indeterminato."""
    outer = _parse(payload)
    response = outer.get(11)
    if response is None:
        return True  # risposta diversa da un errore (es. punch hole in corso)
    failure = _parse(response).get(3)
    if failure is None:
        # nessun campo failure: ID_NOT_EXIST (valore 0 omesso) oppure risposta di successo
        return False if not response else True
    if failure == _FAIL_LICENSE:
        return None
    return False if failure == _FAIL_OFFLINE else None


async def _probe(rustdesk_id):
    host = settings.RUSTDESK_STATUS_HOST or settings.RUSTDESK_ID_SERVER
    request = (
        _field_ld(1, rustdesk_id.encode())
        + _field_vi(2, 0)
        + _field_ld(3, settings.RUSTDESK_PUBLIC_KEY.encode())
        + _field_vi(4, 0)
    )
    writer = None
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, HBBS_PORT), TIMEOUT)
        writer.write(_frame(_field_ld(8, request)))
        await writer.drain()
        try:
            first = (await asyncio.wait_for(reader.readexactly(1), TIMEOUT))[0]
            head = bytes([first]) + await reader.readexactly(first & 3)
            length = int.from_bytes(head, 'little') >> 2
            payload = await asyncio.wait_for(reader.readexactly(length), TIMEOUT)
        except asyncio.TimeoutError:
            return True  # hbbs non ha risposto con un errore: sta contattando il PC
        except asyncio.IncompleteReadError:
            return None
        return _classify(payload)
    except (OSError, asyncio.TimeoutError, ValueError, IndexError):
        return None
    finally:
        if writer is not None:
            writer.close()


async def fetch_online_states(rustdesk_ids):
    """{id: True/False/None} — None se non è stato possibile stabilirlo."""
    results = await asyncio.gather(*(_probe(i) for i in rustdesk_ids))
    return dict(zip(rustdesk_ids, results))
