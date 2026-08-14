from django.contrib import admin

from .models import SessioneTerminale


@admin.register(SessioneTerminale)
class SessioneTerminaleAdmin(admin.ModelAdmin):
    list_display = ('target', 'utente', 'aperta_il', 'chiusa_il')
    list_filter = ('target',)
    readonly_fields = ('target', 'utente', 'aperta_il', 'chiusa_il', 'errore')

    def has_add_permission(self, request):
        return False
