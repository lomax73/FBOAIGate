# Stato del progetto — punto di partenza per la prossima sessione

Ultimo aggiornamento: 2026-08-13 sera. Leggi questo file per primo quando riprendi,
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
  L'URL della card punta a `https://aigate.fbosolution.it/`, che **non esiste ancora**:
  cliccandoci sopra per ora dà errore, normale finché non arriviamo alla Fase 3.
- Durante il deploy è emerso che il VPS aveva una funzionalità ("stati app"/badge
  colorato) sviluppata direttamente in produzione e mai committata su Git. Verificata
  file per file: era identica a quanto già presente su GitHub. Messa al sicuro con
  `git stash` prima di toccare qualsiasi cosa, poi sincronizzata senza perdite.

## Prossimo passo: Fase 0

Prima di scrivere codice devo, per protocollo (`fase_-1_workflow.md`): riassumere cosa
farò, aspettare conferma esplicita.

**Domanda a cui rispondere per iniziare**: il NUC è già acceso con Debian installato e
raggiungibile in locale (sulla LAN di casa), o va ancora fatto anche quello?

## File del progetto

- `fase_-1_workflow.md` — protocollo di esecuzione delle fasi, leggere per primo dopo
  questo.
- `fase_0_fondamenta.md` → `fase_5_hardening_monitoring.md` — fasi di sviluppo in ordine.
- `fase_8_modifiche_rifinitura.md` — dubbi aperti e decisioni chiuse (file vivo).
- `design/` — identità visiva.
- `docs/` — vuota per ora.

## Riferimenti tecnici utili

- Repo FBOPortal: `https://github.com/lomax73/FBOPortal.git`, branch `main`.
- Alias SSH al VPS di produzione: `ssh mkremote-vps` (config in `~/.ssh/config`,
  `HostName 94.177.161.127`).
- Pattern di deploy: identico a MKRemote — repo separato, utente di sistema dedicato,
  venv proprio, sottodominio proprio (vedi `FBOPortal/deploy/README.md` come modello da
  riusare quando FBOAIGate avrà il suo `deploy/`).
- Progetto analogo già esistente da cui riusare pattern tecnici (VPN hub + console
  browser): `/Users/fabriziolomazzi/SVILUPPO/MKRemote`.
