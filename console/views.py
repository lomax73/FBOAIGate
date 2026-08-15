from asgiref.sync import async_to_sync
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, UpdateView

from hub.models import Target
from hub.services import (
    fetch_resource_usage,
    refresh_target_status,
    sftp_delete,
    sftp_list_dir,
    sftp_mkdir,
    sftp_upload,
)


class SuperuserRequiredMixin(UserPassesTestMixin):
    """Terminale e file manager danno accesso completo agli host: oltre al
    login, richiede esplicitamente is_superuser (non c'è ancora un modello
    di permessi per-Target, vedi RedFlag id 73)."""

    def test_func(self):
        return self.request.user.is_superuser


class TargetListView(LoginRequiredMixin, ListView):
    model = Target
    template_name = 'console/target_list.html'
    context_object_name = 'targets'

    def get_queryset(self):
        targets = list(super().get_queryset())
        for target in targets:
            refresh_target_status(target)
        return targets


class TerminalView(LoginRequiredMixin, SuperuserRequiredMixin, DetailView):
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
        if not user.is_superuser:
            return JsonResponse({'error': 'permesso negato'}, status=403)

        target = await Target.objects.filter(pk=pk).afirst()
        if target is None:
            return JsonResponse({'error': 'host non trovato'}, status=404)

        try:
            usage = await fetch_resource_usage(target)
        except Exception as exc:
            return JsonResponse({'error': str(exc)}, status=502)
        return JsonResponse(usage)


class FileManagerView(LoginRequiredMixin, SuperuserRequiredMixin, DetailView):
    model = Target
    template_name = 'console/file_manager.html'
    context_object_name = 'target'


class TargetFilesListView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    def get(self, request, pk):
        target = get_object_or_404(Target, pk=pk)
        path = request.GET.get('path', '')
        try:
            result = async_to_sync(sftp_list_dir)(target, path)
        except Exception as exc:
            return JsonResponse({'error': str(exc)}, status=502)
        return JsonResponse(result)


class TargetFilesMkdirView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    def post(self, request, pk):
        target = get_object_or_404(Target, pk=pk)
        path = request.POST.get('path', '').rstrip('/')
        name = request.POST.get('name', '').strip()
        if not name or '/' in name:
            return JsonResponse({'error': 'Nome cartella non valido.'}, status=400)
        full_path = f'{path}/{name}' if path else name
        try:
            async_to_sync(sftp_mkdir)(target, full_path)
        except Exception as exc:
            return JsonResponse({'error': str(exc)}, status=502)
        return JsonResponse({'ok': True})


class TargetFilesDeleteView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    def post(self, request, pk):
        target = get_object_or_404(Target, pk=pk)
        path = request.POST.get('path', '')
        if not path:
            return JsonResponse({'error': 'Percorso mancante.'}, status=400)
        try:
            async_to_sync(sftp_delete)(target, path)
        except Exception as exc:
            return JsonResponse({'error': str(exc)}, status=502)
        return JsonResponse({'ok': True})


class TargetFilesUploadView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    def post(self, request, pk):
        target = get_object_or_404(Target, pk=pk)
        path = request.POST.get('path', '')
        uploaded = request.FILES.get('file')
        if not uploaded:
            return JsonResponse({'error': 'Nessun file ricevuto.'}, status=400)
        try:
            async_to_sync(sftp_upload)(target, path, uploaded.name, uploaded)
        except Exception as exc:
            return JsonResponse({'error': str(exc)}, status=502)
        return JsonResponse({'ok': True})
