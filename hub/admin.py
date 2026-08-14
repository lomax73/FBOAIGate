from django.contrib import admin

from .models import Target


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ('nome', 'vpn_ip', 'ssh_user', 'online', 'ultimo_contatto')
    list_filter = ('online',)
    search_fields = ('nome', 'vpn_ip')
