from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, UpdateView

from hub.models import Target


class TargetListView(LoginRequiredMixin, ListView):
    model = Target
    template_name = 'console/target_list.html'
    context_object_name = 'targets'


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
