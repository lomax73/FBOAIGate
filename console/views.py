from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from hub.models import Target


class TargetListView(LoginRequiredMixin, ListView):
    model = Target
    template_name = 'console/target_list.html'
    context_object_name = 'targets'


class TerminalView(LoginRequiredMixin, DetailView):
    model = Target
    template_name = 'console/terminal.html'
    context_object_name = 'target'
