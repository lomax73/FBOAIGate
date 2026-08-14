from django.db import models


class Target(models.Model):
    """Un host raggiungibile tramite l'hub WireGuard di FBOAIGate.

    Il NUC è il primo Target registrato, non un caso speciale: qualunque
    altro host (es. una VPS) si aggiunge creando un'altra riga qui, senza
    modifiche strutturali (vedi fase_0_fondamenta.md).
    """

    nome = models.CharField(max_length=100, unique=True, help_text="Es. \"NUC casa\", \"VPS produzione\".")
    vpn_ip = models.GenericIPAddressField(
        protocol='IPv4', unique=True,
        help_text="Indirizzo assegnato sull'hub WireGuard di FBOAIGate (es. 10.20.0.2).",
    )
    wireguard_public_key = models.CharField(max_length=64, blank=True)
    ssh_user = models.CharField(max_length=100)
    online = models.BooleanField(default=False)
    ultimo_contatto = models.DateTimeField(null=True, blank=True)
    creato_il = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome
