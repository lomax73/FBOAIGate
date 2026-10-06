# Server RustDesk self-hosted

Usato dalla sezione **Assistenza** di FBOAIGate (manutenzione remota dei PC dei
clienti). Non c'entra con la VPN WireGuard: i PC clienti restano fuori dalla VPN e
si collegano in uscita al server RustDesk.

## Stato in produzione (2026-10-06)

Sul VPS `94.177.161.127`, **binari nativi** `rustdesk-server` 1.1.16 come servizi
systemd (Docker non è installato sul VPS, non l'abbiamo introdotto): utente di
sistema `rustdesk`, cartella `/opt/rustdesk`, servizi `rustdesk-hbbs` e
`rustdesk-hbbr` (unit in questa cartella). Nome del server: `aigate.fbosolution.it`
(nessun DNS nuovo). `-k _` = i client senza la chiave del server vengono rifiutati.

## Installazione (già fatta)

```
adduser --system --group --home /opt/rustdesk rustdesk
# scaricare rustdesk-server-linux-amd64.zip dalla release GitHub, poi:
install -o rustdesk -g rustdesk -m 755 amd64/hbbs amd64/hbbr /opt/rustdesk/
cp deploy/rustdesk/*.service /etc/systemd/system/
systemctl daemon-reload && systemctl enable --now rustdesk-hbbr rustdesk-hbbs
ufw allow 21115:21117/tcp && ufw allow 21116/udp
cat /opt/rustdesk/id_ed25519.pub     # chiave pubblica per i client
```

`.env` di FBOAIGate:
```
RUSTDESK_ID_SERVER=aigate.fbosolution.it
RUSTDESK_RELAY_SERVER=aigate.fbosolution.it
RUSTDESK_PUBLIC_KEY=<contenuto di id_ed25519.pub>
```
poi `migrate` e `systemctl restart fboaigate-web.service`.

**Backup**: `/opt/rustdesk/id_ed25519` è la chiave privata del server. Se si perde,
tutti i client vanno riconfigurati.

## Uso

- **Assistenza → Onboarding**: scarica lo script (Windows `.ps1` / Linux `.sh`) da
  eseguire come amministratore sul PC del cliente. Installa RustDesk, lo punta al
  server, imposta una password permanente casuale e stampa ID + password.
- **Assistenza → + Postazione**: registra cliente e ID RustDesk.
- **Connetti**: apre il client RustDesk locale (`rustdesk://ID`). Serve RustDesk
  installato sul computer dell'operatore, con lo stesso server e la stessa chiave.
  La password permanente **non** è salvata in FBOAIGate.
- Accesso alla sezione: solo `is_superuser`, come terminale e file manager.
