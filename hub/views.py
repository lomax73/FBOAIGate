from asgiref.sync import async_to_sync
from django.http import JsonResponse
from django.views import View

from accounts.internal_auth import check_internal_token

from .models import Target
from .services import fetch_resource_usage, refresh_target_status


class InternalTargetListView(View):
    """Elenco dei Target con stato online/offline aggiornato al volo.

    Esposto sulla API interna token-protected (api/internal/targets/) per il
    widget "Server & VPS" del Portale FBO. Come la API utenti, è raggiungibile
    solo via loopback (regola Nginx) e richiede il token statico condiviso.
    """

    def get(self, request):
        if not check_internal_token(request):
            return JsonResponse({'detail': 'Non autorizzato.'}, status=403)

        targets = []
        for target in Target.objects.all():
            refresh_target_status(target)
            targets.append({
                'id': target.pk,
                'nome': target.nome,
                'vpn_ip': target.vpn_ip,
                'online': target.online,
                'ultimo_contatto': (
                    target.ultimo_contatto.isoformat()
                    if target.ultimo_contatto else None
                ),
            })
        return JsonResponse({'targets': targets})


class InternalTargetResourcesView(View):
    """Risorse di un singolo Target (carico/memoria/disco/os/uptime/temperatura).

    Autenticato via token interno anziché sessione, a differenza di
    TargetResourcesView (console). La connessione SSH ad-hoc rende questa
    chiamata più lenta: il widget del Portale la invoca solo su richiesta
    dell'utente, non a ogni caricamento della lista.
    """

    def get(self, request, pk):
        if not check_internal_token(request):
            return JsonResponse({'detail': 'Non autorizzato.'}, status=403)

        target = Target.objects.filter(pk=pk).first()
        if target is None:
            return JsonResponse({'error': 'host non trovato'}, status=404)

        try:
            usage = async_to_sync(fetch_resource_usage)(target)
        except Exception as exc:
            return JsonResponse({'error': str(exc)}, status=502)
        return JsonResponse(usage)
