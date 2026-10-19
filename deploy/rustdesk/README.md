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

- **Assistenza → + Cliente / + Postazione**: registra cliente, nome del PC e ID RustDesk.
- **Stato**: la colonna Stato (Online/Offline/n/d) e "Visto online" si aggiornano solo
  quando si apre o ricarica la lista, senza polling. Il server open source non ha
  un'API di stato: si invia a hbbs una richiesta di connessione (porta 21116, con la
  chiave) e si legge la risposta `OFFLINE`/`ID_NOT_EXIST`. `n/d` = non è stato
  possibile stabilirlo (server non raggiungibile o chiave errata).
- **Connetti**: apre il client RustDesk locale (`rustdesk://ID`). Serve RustDesk
  installato sul computer dell'operatore, con lo stesso server e la stessa chiave
  (vedi sotto). La password permanente **non** è salvata in FBOAIGate.
- Accesso alla sezione: solo `is_superuser`, come terminale e file manager.

## Postazione operatore (Mac o altro)

1. Installa RustDesk (Mac: `brew install --cask rustdesk` o `.dmg`; scegliere la
   versione Apple Silicon/Intel corretta).
2. ⋮ accanto all'ID → **Rete** → sblocca → imposta Server ID e Server relay
   `aigate.fbosolution.it` e la chiave pubblica (`cat /opt/rustdesk/id_ed25519.pub`
   sul VPS). Deve comparire "Pronto".

## Onboarding di un PC cliente

Due modalità equivalenti. Il risultato è sempre: RustDesk installato **con servizio
attivo**, puntato al nostro server, password permanente impostata, ID annotato.

### A. Con lo script (consigliata, password casuale)
**Assistenza → Onboarding** → scarica lo script.
- **Windows**: PowerShell **come Amministratore**, nella cartella dove è stato scaricato lo script.
  1. **Sblocca il file** (Windows lo marca come scaricato da Internet): `Unblock-File .\rd-win.ps1`
  2. Lancialo: `powershell -ExecutionPolicy Bypass -File .\rd-win.ps1`
  3. Se continua a bloccare (policy imposta da criterio di gruppo/antivirus, verifica con
     `Get-ExecutionPolicy -List`): aprire lo script in Blocco note, copiare tutto e
     **incollarlo nella finestra PowerShell** (non passa dal controllo sui file). Metodo verificato.
- **Linux (Debian/Ubuntu)**: `sudo bash rd-linux.sh` (non ancora provato su
  una macchina reale).

Lo script stampa ID e password sotto "ANNOTA QUESTI DATI": salvare la password nel
password manager.

### B. Manuale (nessuno script, utile se le policy bloccano gli script)
1. Scarica l'installer da rustdesk.com e scegli **Installa** (non "Esegui senza
   installare": serve il servizio per l'accesso con utente scollegato e dopo riavvio).
2. ⋮ → **Rete** → sblocca (serve Amministratore) → Server ID e Server relay
   `aigate.fbosolution.it`, Key = chiave pubblica del server → Applica → "Pronto".
3. ⋮ → **Sicurezza** → sblocca → verifica **solo password permanente** → imposta una
   password lunga e casuale (salvarla nel password manager).
4. Sempre in Sicurezza verificare che il **servizio** sia abilitato/installato.
5. Copiare l'ID dalla finestra principale.

### Dopo l'onboarding (entrambe le modalità)
Registrare la postazione in **Assistenza → + Postazione**, poi provare **Connetti**.
Controllo consigliato: riavviare il PC cliente e riconnettersi senza nessuno davanti.
