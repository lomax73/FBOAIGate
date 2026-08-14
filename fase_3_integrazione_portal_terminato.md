# Fase 3 — Integrazione con FBOPortal

## Obiettivo (ridefinito con l'utente, 2026-08-14)
Non SSO/handoff di sessione (scartato esplicitamente: "voglio che funzioni come le
altre app, login separata ma gestione degli utenti centralizzati su FBOPortal") —
FBOAIGate ha il suo login separato come tutte le altre app della famiglia, ma gli
account si creano/modificano/eliminano centralmente da FBOPortal, stesso pattern già
in uso per MKRemote.

## Prerequisiti
Fase 2 completata.

## Task eseguiti

1. Card `fboaigate` attiva nel catalogo FBOPortal (`is_active=True`) — già fatto in
   Fase 0, confermato funzionante ora che il sottodominio è raggiungibile davvero.
2. API interna di gestione utenti in FBOAIGate (`accounts/`, `api/internal/users/`),
   identica a quella di MKRemote: token statico (`INTERNAL_API_TOKEN`) via header
   `Authorization`, endpoint raggiungibile solo da `127.0.0.1` (vhost Nginx dedicato
   su `127.0.0.1:8452`, bloccato esplicitamente anche sul vhost pubblico).
3. `AppLink` di FBOAIGate su FBOPortal configurato con `internal_base_url =
   https://127.0.0.1:8452` e il token — stesso meccanismo generico già usato per
   le altre app, nessuna modifica al codice di FBOPortal è stata necessaria.

## Criteri di completamento (verificati)
- API bloccata dall'esterno (403), raggiungibile da localhost sul VPS (200) ✓
- FBOPortal riesce a elencare, creare ed eliminare utenti su FBOAIGate usando lo
  stesso client (`useradmin/services.py`) già usato per le altre app — testato
  end-to-end (creazione + eliminazione utente di prova) ✓
