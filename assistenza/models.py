from django.core.validators import RegexValidator
from django.db import models


class Cliente(models.Model):
    nome = models.CharField(max_length=150, unique=True)
    note = models.TextField(blank=True)
    creato_il = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'clienti'

    def __str__(self):
        return self.nome


class Postazione(models.Model):
    """Un PC di un cliente raggiungibile con RustDesk.

    Non è un Target: i PC dei clienti stanno dietro NAT, non hanno SSH e non
    sono nella VPN. Si registra solo l'ID RustDesk — la password permanente
    NON viene salvata qui (resta nel client RustDesk dell'operatore).
    """

    SISTEMI = [('windows', 'Windows'), ('linux', 'Linux')]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='postazioni')
    nome = models.CharField(max_length=100, help_text='Es. "Segreteria", "PC magazzino".')
    rustdesk_id = models.CharField(
        'ID RustDesk', max_length=16, unique=True,
        validators=[RegexValidator(r'^[A-Za-z0-9_-]{6,16}$', 'ID RustDesk non valido.')],
    )
    sistema = models.CharField(max_length=10, choices=SISTEMI, default='windows')
    note = models.TextField(blank=True)
    ultima_connessione = models.DateTimeField(null=True, blank=True)
    creato_il = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['cliente__nome', 'nome']
        verbose_name_plural = 'postazioni'

    def __str__(self):
        return f'{self.cliente} — {self.nome}'
