from django.contrib import admin

from .models import Cliente, Postazione


class PostazioneInline(admin.TabularInline):
    model = Postazione
    extra = 0


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'creato_il')
    search_fields = ('nome',)
    inlines = [PostazioneInline]


@admin.register(Postazione)
class PostazioneAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cliente', 'rustdesk_id', 'sistema', 'ultima_connessione')
    list_filter = ('cliente', 'sistema')
    search_fields = ('nome', 'rustdesk_id', 'cliente__nome')
