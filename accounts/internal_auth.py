from django.conf import settings


def check_internal_token(request) -> bool:
    """Verifica il token statico condiviso con FBOPortal (INTERNAL_API_TOKEN).

    Gli endpoint interni sono già protetti a monte da Nginx (solo loopback);
    il token è la seconda linea di difesa, stesso pattern di MKRemote/FBOPortal.
    Usata sia dalla API interna di gestione utenti (accounts) sia dalla API
    interna dello stato host (hub).
    """
    expected = getattr(settings, 'INTERNAL_API_TOKEN', '')
    provided = request.headers.get('Authorization', '')
    return bool(expected) and provided == f'Token {expected}'
