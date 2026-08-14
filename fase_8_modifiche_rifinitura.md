# Fase 8 — Modifiche e rifinitura (file vivo)

Dubbi, scelte rimandate, alternative non decise durante l'esecuzione delle fasi. Non
seguire l'ordine numerico: si aggiorna in continuazione.

## Aperti

- **Chiave SSH di sviluppo ancora autorizzata sul NUC** (2026-08-14): durante lo
  sviluppo locale della Fase 2 è stata generata una chiave di servizio sul Mac
  (`~/.ssh/fboaigate_console_service`) e autorizzata sul NUC per i test. Dopo il
  deploy in produzione, il VPS ha la sua chiave dedicata
  (`/opt/fboaigate/.ssh/console_service`, generata lì). La chiave del Mac resta
  autorizzata sul NUC per comodità di test futuri, ma andrebbe rimossa
  (`~/.ssh/authorized_keys` sul NUC) quando non serve più, per igiene.
- **DNS `aigate.fbosolution.it` non ancora propagato** (verificato 2026-08-14
  anche sull'authoritative nameserver Aruba: nessun record A). L'utente ha
  detto di averlo già creato lato pannello Aruba. Deploy fatto comunque con
  certificato self-signed provvisorio (stesso pattern usato inizialmente da
  FBOPortal) — appena il DNS risolve, sostituire con Let's Encrypt
  (`certbot --nginx -d aigate.fbosolution.it` sul VPS).

- **Stato online/offline del Target non è "live"** (Fase 2, 2026-08-14): il campo
  `Target.online` è statico (impostato a mano in fase di registrazione), non
  aggiornato da un controllo periodico reale. Il criterio di completamento della
  Fase 2 ("elenco host mostrato correttamente con stato aggiornato") è quindi solo
  parzialmente soddisfatto: la UI mostra il campo, ma nulla lo tiene sincronizzato
  col tunnel WireGuard vero. Rimandato apposta: un vero controllo di stato
  (heartbeat/polling) sembra territorio della Fase 5 (hardening/monitoring), non
  della Fase 2. Da confermare con l'utente quando si arriva lì, o prima se serve
  prima.
- **Console (Fase 2) testata solo in parte in locale**: il Mac di sviluppo non fa
  parte della VPN `wg1`/`wg0` di FBOAIGate, quindi non può raggiungere
  `10.20.0.2` direttamente. Verificato invece: (1) l'intera catena
  login→WebSocket→consumer è cablata correttamente (WS accettato, `asyncssh`
  invocato con l'host giusto, log lato server confermano il tentativo); (2)
  l'autenticazione SSH con la chiave di servizio funziona davvero, testato con
  uno script `asyncssh` eseguito direttamente dal VPS (che ha la rotta via
  `wg1`) verso il NUC — output: `whoami`/`hostname` corretti. Non è stato
  verificato il flusso completo dal browser reale (xterm.js + digitazione
  interattiva) perché richiederebbe deploy sul VPS o aggiunta del Mac come peer
  VPN — nessuna delle due fatta di proposito, per non allargare lo scope della
  fase. Da fare al primo deploy reale su VPS.

- **Fase 1, punto 5 (firewall + SSH solo su wg0) — rimandato di un paio di giorni**
  (deciso con l'utente 2026-08-14): tunnel WireGuard NUC↔hub verificato e
  funzionante, ma il blocco dell'accesso pubblico SSH è rimandato apposta: prima si
  lascia il tunnel girare qualche giorno per verificarne la stabilità (riconnessione
  automatica dopo cadute di rete, riavvii, ecc.), poi si procede col lockdown.
  Rischio noto: una volta applicato, se il tunnel dovesse cadere il NUC diventerebbe
  irraggiungibile da remoto (richiederebbe accesso fisico). Non procedere senza
  conferma esplicita dell'utente.
- **Hub VPN condiviso fisicamente col VPS di MKRemote, isolato logicamente**
  (2026-08-14, confermato con l'utente): interfaccia `wg1` separata da `wg0`
  (MKRemote), porta `51821` invece di `51820`, subnet `10.20.0.0/24`. Nessuna
  modifica alla configurazione esistente di MKRemote.

- **Pulsante "genera script di onboarding nuovo host" nell'interfaccia** (richiesto
  dall'utente 2026-08-14, Fase 1): quando si aggiunge un nuovo `Target`, l'interfaccia
  dovrà offrire un pulsante che genera lo script da eseguire sull'host per collegarlo
  al tunnel WireGuard — stesso pattern già usato in MKRemote
  (`vpn/scripts.py:generate_wireguard_setup_script` / `generate_firewall_lockdown_script`,
  ma lì per RouterOS/.rsc). Per FBOAIGate gli host sono Linux (Debian/VPS): lo script
  sarà bash + `wg`/`wg-quick`, stessa logica (chiave privata generata sull'host, mai
  trasmessa; firewall lockdown come script separato da eseguire solo dopo verifica
  tunnel). Da implementare nell'app `hub` quando si arriva alla UI (Fase 2/3) — il
  tunnel del NUC (primo Target) in Fase 1 viene fatto a mano via SSH per validare il
  meccanismo prima di scriverne l'automazione.

## Chiusi (continua)

- **Fase 0 completata** (2026-08-14): scaffolding Django (`fboaigate`, app
  `hub`/`console`/`bot`/`accounts`, modello `Target` con migrazioni, venv,
  `requirements.txt`, `.env.example`, repo git inizializzato). Sul NUC:
  `unattended-upgrades` installato/attivo, Claude Code installato e autenticato
  (verificato con `claude -p`). IP del NUC reso statico (`10.0.0.169/24`, gateway
  `10.0.0.1`, DNS `192.168.1.1` fissato e reso immutabile con `chattr +i` dopo un
  incidente in cui un demone `dhcpcd` residuo sovrascriveva la configurazione —
  risolto, backup dei file originali in `/etc/network/*.bak.20260814` sul NUC).
  Alias SSH locale `fboaigate-nuc` configurato (chiave dedicata
  `~/.ssh/fboaigate_nuc`, separata da quella di MKRemote).

- **Incorporamento futuro di MKRemote** (deciso in linea di massima, meccanismo aperto):
  FBOAIGate diventerà l'interfaccia unica che aggrega sezioni oggi separate — "router"
  (l'attuale MKRemote), "server"/VPS (il gateway attuale), e altre in futuro. Confermato
  con l'utente 2026-08-14: mantenere l'isolamento tecnico tra i sottosistemi (hub VPN
  separati, profili di rischio diversi), unificare solo l'esperienza utente. Non ancora
  deciso *come* aggregare le UI (opzioni valutate: menu/link tra domini separati, reverse
  proxy con sessione condivisa, aggregazione via API con UI propria in FBOAIGate) — da
  affrontare quando si arriverà a quella fase, non ora. Per ora si procede con lo sviluppo
  di FBOAIGate secondo le fasi già pianificate, senza bloccarsi su questa decisione.
- **Nome definitivo del progetto Django** (`fboaigate`?): provvisorio, da confermare in
  Fase 0.
- **Audit dei comandi eseguiti in console** (Fase 2): loggare solo le sessioni (chi/quando/
  quale host) o anche il contenuto? Implicazioni di privacy, da decidere con l'utente, non
  di default.
- **Prompt e comportamento del bot Telegram** (Fase 4): in attesa che l'utente lo fornisca.
  Da chiarire anche se il bot dovrà poter scegliere l'host target (come la console) o
  restare per ora scoped al solo NUC.
- **Eccezioni per host con IP pubblico proprio** (Fase 1, nota): una VPS già dell'utente
  potrebbe in teoria bypassare l'hub. Deciso di default di *non* fare eccezioni (tutto
  passa dall'hub) — da confermare quando si aggiungerà davvero la prima VPS.

## Chiusi

- **Hub condiviso con MKRemote vs hub dedicato** (Fase 0): risolto — hub dedicato
  FBOAIGate, per isolamento dal profilo di rischio diverso di MKRemote.
- **Scope dell'app: solo NUC o multi-host** (Fase 0): risolto — FBOAIGate è un gateway
  verso un registro di host (`Target`), il NUC è solo il primo. Vedi modello dati in
  `fase_0_fondamenta.md`.
