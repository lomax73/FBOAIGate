# Fase 0 — Fondamenta: hub, registro host, scheletro progetto

## Obiettivo
Preparare l'infrastruttura di base su cui costruire tunnel, console browser e bot
Telegram: hub VPN dedicato e un **registro di host** — non solo il NUC, ma qualunque
server l'utente voglia aggiungere in futuro (es. una VPS già sua), ciascuno raggiungibile
in SSH dal browser tramite FBOAIGate, da qualunque luogo, senza porte esposte.

## Prerequisiti
Nessuno. Prima fase del progetto. Richiede accesso fisico/locale al NUC per
l'installazione iniziale (prima che il tunnel remoto esista).

## Decisione architetturale (presa)

**Hub dedicato FBOAIGate**, indipendente dall'hub WireGuard di MKRemote. Isolamento tra
i due progetti: un problema su MKRemote (gestione router clienti) non deve poter toccare
l'accesso ai server con Claude/Telegram, che ha un profilo di rischio diverso (esecuzione
comandi, non solo monitoraggio).

## Modello dati: registro host (`Target`)

FBOAIGate non è "la console del NUC": è un gateway verso **N host**, ciascuno registrato
con:
- nome/etichetta (es. "NUC casa", "VPS produzione")
- indirizzo VPN assegnato sull'hub (es. `10.20.0.2`)
- chiave pubblica WireGuard dell'host
- utente SSH da usare
- stato (online/offline, ultimo contatto)

Il NUC è semplicemente il primo `Target` registrato. Aggiungere la VPS in futuro significa
solo: installare il client WireGuard sulla VPS, farla dialogare con l'hub, registrarla —
nessuna modifica strutturale all'app.

## Task da eseguire

1. **NUC — sistema base**:
   - Debian stable, minimal (no desktop environment)
   - Utente non-root dedicato, accesso iniziale via chiave SSH (in locale, non esposto)
   - `unattended-upgrades` per le patch di sicurezza
   - Claude Code installato e autenticato

2. **Scaffolding progetto** (nome provvisorio `fboaigate`, da confermare):
   - Django, come gli altri progetti FBO (coerenza con FBOPortal/MKRemote)
   - App interne separate per dominio: `hub` (registro `Target` + stato WireGuard),
     `console`, `bot`, `accounts`
   - `requirements.txt`, `.env` per i secret (mai committato)

3. **Pianificazione subnet VPN**:
   - Subnet privata dedicata, es. `10.20.0.0/24`
   - `.1` riservato all'hub
   - `.2` in su assegnati progressivamente ai `Target` (NUC = `.2`, prossimo host = `.3`, ...)

## Criteri di completamento
- NUC raggiungibile solo in locale (nessuna porta esposta pubblicamente)
- Claude Code funzionante sul NUC
- Modello `Target` progettato e migrazioni create
- Scheletro progetto avviabile in locale/dev

## Note
Questa fase non espone nulla in produzione. Una VPS "già sua" con IP pubblico potrebbe in
teoria essere raggiunta anche senza WireGuard (SSH diretto) — ma per tenere lo stesso
invariante di sicurezza su tutti gli host ("nessuna porta SSH esposta pubblicamente, tutto
passa dall'hub") conviene farla dialogare col hub allo stesso modo del NUC. Se in futuro
serve un'eccezione per un host specifico, va discussa esplicitamente, non assunta.
