# Stato del progetto — punto di partenza per la prossima sessione

Ultimo aggiornamento: 2026-08-14. Leggi questo file per primo quando riprendi,
poi `fase_-1_workflow.md` per il protocollo di esecuzione delle fasi.

## Cos'è FBOAIGate

Gateway di accesso sicuro (senza port forward) verso un **registro di host** — il NUC
Debian con Claude Code è il primo, ma in futuro si aggiungeranno altri server (es. una
VPS già dell'utente). Richiamabile da FBOPortal, da qualunque luogo. In futuro anche un
bot Telegram per inviare comandi.

## Decisioni prese finora

- **Nome**: FBOAIGate (provvisorio anche per il progetto Django che nascerà in Fase 0).
- **Identità visiva**: scudo (canale protetto) + cervello a due emisferi — sinistro
  anatomico, destro fatto di piste da circuito stampato ("umano + macchina") + prompt di
  terminale `>_`. Dettagli e palette in `design/BRAND.md`. File pronti:
  `design/fboaigate-icon.svg` (pieno), `design/fboaigate-icon-small.svg` (sotto 48px),
  `design/fboaigate-portal.svg` (stile card FBOPortal, 100×100, già in produzione).
- **Hub VPN dedicato**, non condiviso con MKRemote — isolamento tra i due progetti
  (profilo di rischio diverso: MKRemote monitora router clienti, FBOAIGate esegue
  comandi).
- **Scope multi-host fin dall'inizio**: modello dati `Target` (nome, IP VPN, chiave
  WireGuard, stato) — il NUC è solo il primo. Vedi `fase_0_fondamenta.md`.
- Ogni host, NUC compreso, si collega all'hub **in uscita** (WireGuard outbound): nessuna
  porta SSH esposta pubblicamente su nessun host, nemmeno su una futura VPS con IP
  pubblico proprio (deciso di default in `fase_8_modifiche_rifinitura.md`, da riconfermare
  quando arriva davvero la prima VPS).
- **Direzione futura (2026-08-14)**: FBOAIGate diventerà l'interfaccia unica che aggrega
  sezioni oggi separate — "router" (l'attuale MKRemote) verrà incorporato, insieme a
  "server"/VPS (questo progetto) e altre in futuro. L'isolamento tecnico tra i sottosistemi
  resta (hub VPN separati, profili di rischio diversi) — si unifica solo l'esperienza
  utente. Meccanismo di aggregazione UI non ancora deciso, vedi voce aperta in
  `fase_8_modifiche_rifinitura.md`. Per ora si procede con le fasi già pianificate senza
  bloccarsi su questo.

## Cosa è già stato fatto fuori dalla cartella di progetto

- **FBOPortal** (`/Users/fabriziolomazzi/SVILUPPO/FBOPortal`): card FBOAIGate creata nel
  catalogo, `is_active=True`, badge ambra "In sviluppo", icona `static/img/fboaigate.svg`.
  Fatto sia in locale che **in produzione** (deploy sul VPS completato: commit
  `fd142c6` pushato su GitHub, pullato sul VPS via `ssh mkremote-vps`, migrazioni
  verificate, `collectstatic` + restart di `portal-web.service` fatti, riga creata nel DB
  di produzione). La card è visibile su `https://94.177.161.127:8443/` (URL provvisorio,
  non c'è ancora un dominio vero — vedi `FBOPortal/deploy/README.md`).
  L'URL della card punta a `https://aigate.fbosolution.it/`, che **ora esiste
  davvero** (deploy fatto, vedi sezione Fase 2/deploy più sotto) — cliccandoci
  sopra porta al login di FBOAIGate.
- Durante il deploy è emerso che il VPS aveva una funzionalità ("stati app"/badge
  colorato) sviluppata direttamente in produzione e mai committata su Git. Verificata
  file per file: era identica a quanto già presente su GitHub. Messa al sicuro con
  `git stash` prima di toccare qualsiasi cosa, poi sincronizzata senza perdite.

## Fase 0 — completata (2026-08-14)

- Scaffolding Django `fboaigate` creato: app `hub` (modello `Target` con migrazioni),
  `console`, `bot`, `accounts`. Venv proprio, `requirements.txt`, `.env.example`,
  `.gitignore`, repo git inizializzato con un primo commit locale (nessun push,
  nessun remote configurato ancora).
- Settings env-driven come MKRemote: SQLite in sviluppo di default, Postgres in
  produzione via `DB_ENGINE=postgresql`. Subnet VPN pianificata: `10.20.0.0/24`.
- **NUC**: `unattended-upgrades` installato e attivo; Claude Code installato
  (installer nativo) e **autenticato** (verificato con `claude -p`).
- **IP del NUC reso statico**: `10.0.0.169/24`, gateway `10.0.0.1`, DNS `192.168.1.1`
  (fissato in `/etc/resolv.conf` e reso immutabile con `chattr +i` per evitare che
  venga sovrascritto al boot — vedi incidente e soluzione in
  `fase_8_modifiche_rifinitura.md`).
- **Accesso SSH da questo Mac**: alias `ssh fboaigate-nuc` configurato in
  `~/.ssh/config`, chiave dedicata `~/.ssh/fboaigate_nuc` (separata da quella usata
  per MKRemote/VPS, per coerenza con l'isolamento tra progetti). Funziona solo via
  LAN (IP `10.0.0.169`).
- **Accesso SSH indipendente dalla LAN (2026-08-14)**: alias
  `ssh fboaigate-nuc-tunnel`, salta attraverso il VPS (`ProxyJump mkremote-vps`) e
  arriva al NUC via tunnel WireGuard (`10.20.0.2`), stessa chiave. Serve perché
  questo Mac non è un peer della VPN e non potrebbe raggiungere `10.20.0.2`
  direttamente. Verificato funzionante (comandi + sudo) prima che l'utente
  isolasse il NUC dalla LAN.

Dettagli completi in `fase_0_fondamenta_terminato.md` e `fase_8_modifiche_rifinitura.md`.

## Fase 1 — in corso (2026-08-14): tunnel creato, lockdown SSH sospeso

- **Hub WireGuard**: `wg1` sul VPS di MKRemote (`94.177.161.127`), isolato da `wg0`
  di MKRemote — porta `51821` (vs `51820`), subnet `10.20.0.0/24`, hub IP `10.20.0.1`.
  Deciso di condividere il VPS fisico ma non la configurazione (vedi fase_8).
- **NUC**: `wireguard`/`wireguard-tools` installati, chiave generata sul NUC stesso,
  `wg0` configurato verso l'hub (IP tunnel `10.20.0.2`), `PersistentKeepalive=25`,
  servizio `wg-quick@wg0` abilitato al boot.
- **Verificato**: handshake attivo, ping bidirezionale hub↔NUC, SSH raggiungibile
  attraverso il tunnel (testato dal VPS, che è dentro la VPN).
- **Registrato** come primo `Target` nel database Django (`NUC casa`, `10.20.0.2`).
- **Non ancora fatto, di proposito**: punto 5 della fase (firewall + SSH solo su
  `wg0`, chiusura dell'accesso pubblico) — l'utente ha chiesto di discuterne prima
  di attivarlo, per il rischio di restare tagliati fuori se il tunnel cade. **Non
  procedere senza conferma esplicita.**
- **Da tenere a mente per dopo**: l'utente ha chiesto un pulsante nell'interfaccia
  che generi lo script di onboarding per nuovi host (stesso pattern di MKRemote,
  vedi fase_8) — da fare quando si arriva alla UI (Fase 2/3), non ora.

## Fase 2 — in corso in parallelo (2026-08-14): console browser

Backend Channels (`console` app) + frontend xterm.js, stesso pattern di
`terminal/` in MKRemote ma con autenticazione a chiave (non user/pass): il
backend usa una chiave SSH di servizio propria (`CONSOLE_SSH_PRIVATE_KEY_PATH`,
generata su questo Mac per sviluppo, autorizzata sul NUC), distinta dalle chiavi
personali degli amministratori.

- Login, elenco host, apertura pagina terminale: testati in locale (Daphne, non
  `runserver` — Channels richiede ASGI esplicito).
- Catena WebSocket→consumer→`asyncssh`: verificata cablata correttamente.
- Autenticazione SSH con la chiave di servizio: verificata **funzionante**, ma
  testata dal VPS (dentro la VPN), non dal Mac di sviluppo (fuori dalla VPN,
  non può raggiungere `10.20.0.2`). Il flusso completo dal browser reale non è
  stato ancora provato — richiede deploy su VPS. Vedi dettagli in fase_8.
- Aperto: `Target.online` non è aggiornato da un controllo reale (probabile
  territorio Fase 5) — vedi fase_8.

## Deploy in produzione — stato al 2026-08-14 sera

`https://aigate.fbosolution.it/` — VPS `94.177.161.127` (stesso di MKRemote,
hub `wg1` separato), utente di sistema `fboaigate`, Postgres, Daphne dietro
Nginx (systemd `fboaigate-web.service`). Procedura completa in
`deploy/README.md`.

- **Certificato TLS vero** (Let's Encrypt, rinnovo automatico, scade
  2026-11-12) — il DNS si è propagato durante la sessione, sostituito il
  self-signed provvisorio, rimosso l'accesso via IP:porta usato nel frattempo.
- **Login**: `admin` / `Faba7377` (password cambiata su richiesta esplicita
  dell'utente — nota: stessa password usata per il sudo/SSH del NUC, riuso
  segnalato ma voluto).
- **Fase 2 verificata end-to-end e ampliata oltre i criteri minimi**:
  - terminale via WebSocket → Nginx → Daphne → `asyncssh` → Target, chiave di
    servizio, sessioni loggate in `SessioneTerminale`;
  - stato online/offline **live** (`hub/services.py:refresh_target_status`,
    check TCP sulla porta SSH ad ogni caricamento della lista, non più un
    valore statico);
  - pannello risorse (carico/memoria/disco) nella pagina terminale, aggiornato
    ogni 10s (`hub/services.py:fetch_resource_usage`, endpoint JSON async
    `TargetResourcesView`);
  - rinomina host dalla lista (`TargetRenameView`);
  - **persistenza tramite tmux**: il terminale si aggancia a una sessione
    tmux sull'host (`console/consumers.py:TMUX_SESSION_COMMAND`) — un
    processo lasciato in esecuzione (es. `claude` mentre elabora) sopravvive
    alla chiusura della scheda/WebSocket, verificato empiricamente. Richiede
    `tmux` installato sul Target (fatto sul NUC, annotato come prerequisito
    di onboarding in `deploy/README.md`).
  - integrazione **FBOFlag** (bandierina di segnalazione bug), stesso pattern
    delle altre app FBO — solo snippet client-side in `templates/base.html`.
- Chiave SSH di servizio della console generata **sul VPS stesso**
  (`/opt/fboaigate/.ssh/console_service`), autorizzata sul NUC. Nota: resta
  autorizzata sul NUC anche la chiave di sviluppo generata sul Mac (usata per
  i test locali prima del deploy) — pulizia rimandata, vedi fase_8.
- **Accesso SSH al NUC ora possibile solo via tunnel**: l'utente ha isolato
  il NUC dalla LAN di casa (restava sulla stessa rete, solo non più
  raggiungibile da questo Mac). Uso `ssh fboaigate-nuc-tunnel` (ProxyJump via
  VPS), verificato funzionante prima dell'isolamento.
- **File manager via SFTP** nella console: sfoglia/naviga cartelle remote,
  carica file dal proprio PC, crea/elimina cartelle (eliminazione ricorsiva
  per le cartelle, con conferma). Verificato end-to-end contro il NUC.
- **"Chiudi sessione" nel terminale** ora ripristina davvero l'interfaccia
  (prima chiudeva solo il WebSocket lasciando il riquadro a schermo) — bug
  fix.

## Fase 3 — Integrazione con FBOPortal: **terminata (2026-08-14)**

Obiettivo ridefinito con l'utente: non SSO (scartato esplicitamente), ma
**login separato + gestione utenti centralizzata da FBOPortal**, stesso
pattern già in uso per MKRemote. App `accounts/` espone
`api/internal/users/`, token statico, endpoint raggiungibile solo da
`127.0.0.1` (vhost Nginx dedicato su `127.0.0.1:8452`, più un blocco di
sicurezza identico anche sul vhost pubblico). `AppLink` di FBOAIGate su
FBOPortal configurato. Verificato end-to-end: FBOPortal elenca, crea ed
elimina utenti su FBOAIGate usando lo stesso client già usato per le altre
app (`useradmin/services.py`), nessuna modifica al codice di FBOPortal.
Dettagli in `fase_3_integrazione_portal_terminato.md` e `deploy/README.md`.

## Prossimo passo

1. **Fase 1**: tunnel in osservazione, poi punto 5 (firewall + lockdown SSH
   sul NUC) di `fase_1_tunnel_sicuro_esecuzione.md`. Non procedere senza
   conferma esplicita dell'utente.
2. **Fase 2**: nella pratica ampiamente superata dai criteri minimi (vedi
   sopra) — da chiudere formalmente come `_terminato` quando l'utente
   conferma di non avere altro da aggiungere.
3. **Fase 4** (bot Telegram) e **Fase 5** (hardening/monitoring): non ancora
   iniziate.

## File del progetto

- `fase_-1_workflow.md` — protocollo di esecuzione delle fasi, leggere per primo dopo
  questo.
- `fase_0_fondamenta.md` → `fase_5_hardening_monitoring.md` — fasi di sviluppo in ordine.
- `fase_8_modifiche_rifinitura.md` — dubbi aperti e decisioni chiuse (file vivo).
- `design/` — identità visiva.
- `docs/` — vuota per ora.

## Riferimenti tecnici utili

- Repo FBOAIGate (questo progetto): `https://github.com/lomax73/FBOAIGate`, branch
  `main`. Pubblico, coerente con FBOPortal/MKRemote. Nessun link sulla card
  FBOPortal per scelta esplicita dell'utente (2026-08-14): il repo è ad uso
  interno/sviluppo, non va esposto sulla card pubblica.
- Repo FBOPortal: `https://github.com/lomax73/FBOPortal.git`, branch `main`.
- Alias SSH al VPS di produzione: `ssh mkremote-vps` (config in `~/.ssh/config`,
  `HostName 94.177.161.127`).
- Pattern di deploy: identico a MKRemote — repo separato, utente di sistema dedicato,
  venv proprio, sottodominio proprio (vedi `FBOPortal/deploy/README.md` come modello da
  riusare quando FBOAIGate avrà il suo `deploy/`).
- Progetto analogo già esistente da cui riusare pattern tecnici (VPN hub + console
  browser): `/Users/fabriziolomazzi/SVILUPPO/MKRemote`.
