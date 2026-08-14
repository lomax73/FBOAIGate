from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, UpdateView

from hub.models import Target
from hub.services import fetch_resource_usage, refresh_target_status


class TargetListView(LoginRequiredMixin, ListView):
    model = Target
    template_name = 'console/target_list.html'
    context_object_name = 'targets'

    def get_queryset(self):
        targets = list(super().get_queryset())
        for target in targets:
            refresh_target_status(target)
        return targets


class TerminalView(LoginRequiredMixin, DetailView):
    model = Target
    template_name = 'console/terminal.html'
    context_object_name = 'target'


class TargetRenameView(LoginRequiredMixin, UpdateView):
    model = Target
    fields = ['nome']
    template_name = 'console/target_rename.html'
    context_object_name = 'target'
    success_url = reverse_lazy('target-list')


class TargetResourcesView(View):
    """Endpoint JSON per il pannello risorse nella pagina terminale. Non usa
    LoginRequiredMixin (fatto apposta: il mixin sincrono non si combina bene
    con un handler asincrono) — il controllo di autenticazione è fatto a mano."""

    async def get(self, request, pk):
        user = await request.auser()
        if not user.is_authenticated:
            return JsonResponse({'error': 'non autenticato'}, status=401)

        target = await Target.objects.filter(pk=pk).afirst()
        if target is None:
            return JsonResponse({'error': 'host non trovato'}, status=404)

        try:
            usage = await fetch_resource_usage(target)
        except Exception as exc:
            return JsonResponse({'error': str(exc)}, status=502)
        return JsonResponse(usage)
