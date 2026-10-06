# Server RustDesk self-hosted

Usato dalla sezione **Assistenza** di FBOAIGate (manutenzione remota dei PC dei
clienti). Non c'entra con la VPN WireGuard: i PC clienti restano fuori dalla VPN e
si collegano in uscita al server RustDesk.

## Installazione sul VPS

1. DNS: nessun record nuovo, si riusa `aigate.fbosolution.it` (già puntato al VPS; le porte RustDesk non confliggono con Nginx su 80/443). Se in futuro si cambia nome, da
   riportarlo nel compose e nel `.env`.
2. `cd deploy/rustdesk && docker compose up -d`
3. Firewall (ufw o equivalente) — porte da aprire:
   - TCP `21115`, `21116`, `21117` (rendezvous/relay)
   - UDP `21116`
   - TCP `21118`, `21119` solo se serve il web client (non usato da FBOAIGate)
4. Chiave pubblica generata al primo avvio: `cat data/id_ed25519.pub`
5. `.env` di FBOAIGate:
   ```
   RUSTDESK_ID_SERVER=aigate.fbosolution.it
   RUSTDESK_RELAY_SERVER=aigate.fbosolution.it
   RUSTDESK_PUBLIC_KEY=<contenuto di id_ed25519.pub>
   ```
   poi `systemctl restart fboaigate-web.service`.
6. Migrazione: `venv/bin/python manage.py migrate` (app `assistenza`).

**Backup**: la cartella `data/` contiene la chiave privata del server. Se si perde,
tutti i client vanno riconfigurati. Non versionarla (è in `.gitignore`).

## Uso

- **Assistenza → Onboarding**: scarica lo script (Windows `.ps1` / Linux `.sh`) da
  eseguire come amministratore sul PC del cliente. Installa RustDesk, lo punta al
  server, imposta una password permanente casuale e stampa ID + password.
- **Assistenza → + Postazione**: registra cliente e ID RustDesk.
- **Connetti**: apre il client RustDesk locale (`rustdesk://ID`). Serve RustDesk
  installato sul computer dell'operatore, configurato con lo stesso server e chiave.
  La password permanente **non** è salvata in FBOAIGate: va salvata nel client RustDesk
  dell'operatore (o in un password manager).
- Accesso alla sezione: solo `is_superuser`, come terminale e file manager.
