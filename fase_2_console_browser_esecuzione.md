# Fase 2 — Console richiamabile dal browser, con selezione host

## Obiettivo
L'app che l'utente clicca su FBOPortal: mostra l'elenco degli host registrati (NUC, VPS,
futuri server) e apre nel browser un terminale reale collegato a quello scelto, da
qualunque luogo, senza che l'utente debba mai configurare un client SSH o un tunnel
manuale.

## Prerequisiti
Fase 1 completata (tunnel attivo e verificato su almeno un host).

## Task da eseguire

1. **Backend**: servizio (sull'hub, non sugli host) che accetta una sessione WebSocket
   autenticata, riceve quale `Target` aprire, e la inoltra via SSH a quell'host
   attraverso `wg0`. Stesso pattern già collaudato in MKRemote
   (`fase_6_accesso_remoto_browser`).
2. **Frontend**: pagina con elenco host (nome, stato online/offline) → click apre il
   terminale (xterm.js o equivalente) per quell'host specifico, niente da installare
   lato utente.
3. **Autenticazione della sessione**: chi apre la console deve essere autenticato — vedi
   Fase 3 per l'integrazione con il login di FBOPortal.
4. **Logging**: ogni sessione registrata (chi, quando, quale host, durata) — non il
   contenuto dei comandi per default, salvo decisione esplicita successiva.

## Criteri di completamento
- Elenco host mostrato correttamente con stato aggiornato
- Apertura console su un host specifico → terminale funzionante su quell'host
- Sessione persa/chiusa lato server se il WebSocket cade
- Log delle sessioni consultabile, con host coinvolto

## Note
Il contenuto delle sessioni (audit dei comandi) è una scelta di privacy/sicurezza non
banale: da discutere con l'utente prima di implementarla, non da decidere di default.
