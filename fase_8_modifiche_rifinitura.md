# Fase 8 — Modifiche e rifinitura (file vivo)

Dubbi, scelte rimandate, alternative non decise durante l'esecuzione delle fasi. Non
seguire l'ordine numerico: si aggiorna in continuazione.

## Aperti

- **Fase 1, punto 5 (firewall + SSH solo su wg0) — sospeso, da discutere prima di
  attivarlo** (2026-08-14): tunnel WireGuard NUC↔hub verificato e funzionante (vedi
  sotto), ma il blocco dell'accesso pubblico SSH non è ancora stato applicato su
  richiesta esplicita dell'utente ("il punto 5 ne discutiamo prima di attivarlo").
  Rischio noto: una volta applicato, se il tunnel dovesse cadere il NUC diventerebbe
  irraggiungibile da remoto (richiederebbe accesso fisico). Non procedere senza
  conferma esplicita.
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
