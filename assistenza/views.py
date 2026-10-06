from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from console.views import SuperuserRequiredMixin

from . import scripts
from .forms import ClienteForm, PostazioneForm
from .models import Cliente, Postazione


class Base(LoginRequiredMixin, SuperuserRequiredMixin):
    """La manutenzione remota dà controllo completo del PC del cliente:
    stesso livello di accesso (is_superuser) del terminale sui Target."""


class PostazioneListView(Base, ListView):
    model = Postazione
    template_name = 'assistenza/postazione_list.html'
    context_object_name = 'postazioni'

    def get_queryset(self):
        qs = super().get_queryset().select_related('cliente')
        q = self.request.GET.get('q', '').strip()
        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(nome__icontains=q) | Q(rustdesk_id__icontains=q) | Q(cliente__nome__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class PostazioneCreateView(Base, CreateView):
    model = Postazione
    form_class = PostazioneForm
    template_name = 'assistenza/form.html'
    success_url = reverse_lazy('assistenza-list')
    extra_context = {'titolo': 'Nuova postazione'}


class PostazioneUpdateView(Base, UpdateView):
    model = Postazione
    form_class = PostazioneForm
    template_name = 'assistenza/form.html'
    success_url = reverse_lazy('assistenza-list')
    extra_context = {'titolo': 'Modifica postazione'}


class PostazioneDeleteView(Base, DeleteView):
    model = Postazione
    template_name = 'assistenza/conferma_elimina.html'
    success_url = reverse_lazy('assistenza-list')


class ClienteCreateView(Base, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'assistenza/form.html'
    success_url = reverse_lazy('assistenza-list')
    extra_context = {'titolo': 'Nuovo cliente'}


class ClienteUpdateView(Base, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'assistenza/form.html'
    success_url = reverse_lazy('assistenza-list')
    extra_context = {'titolo': 'Modifica cliente'}


class ConnettiView(Base, View):
    """Registra l'accesso e rimanda al client RustDesk locale (rustdesk://).
    POST per evitare che un prefetch/anteprima del link conti come connessione."""

    def post(self, request, pk):
        postazione = get_object_or_404(Postazione, pk=pk)
        postazione.ultima_connessione = timezone.now()
        postazione.save(update_fields=['ultima_connessione'])
        response = HttpResponse(status=302)
        response['Location'] = f'rustdesk://{postazione.rustdesk_id}'
        return response


class OnboardingView(Base, TemplateView):
    template_name = 'assistenza/onboarding.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['configurato'] = scripts.is_configured()
        return ctx


class ScriptDownloadView(Base, View):
    def get(self, request, sistema):
        if not scripts.is_configured():
            messages.error(request, 'Server RustDesk non configurato (RUSTDESK_ID_SERVER / RUSTDESK_PUBLIC_KEY nel .env).')
            return HttpResponseRedirect(reverse('assistenza-onboarding'))
        if sistema == 'windows':
            body, name = scripts.windows_script(), 'fbo-rustdesk-windows.ps1'
        elif sistema == 'linux':
            body, name = scripts.linux_script(), 'fbo-rustdesk-linux.sh'
        else:
            return HttpResponse(status=404)
        response = HttpResponse(body, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{name}"'
        return response
