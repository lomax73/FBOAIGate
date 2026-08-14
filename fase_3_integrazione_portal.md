# Fase 3 — Integrazione con FBOPortal

## Obiettivo
La card FBOAIGate nel launcher di FBOPortal (già creata) apre la console solo per utenti
già autenticati sul portale, senza un secondo login separato.

## Prerequisiti
Fase 2 completata.

## Task da eseguire

1. Attivare la voce `fboaigate` nel catalogo FBOPortal (`is_active=True`) quando il
   sottodominio `aigate.fbosolution.it` è davvero raggiungibile.
2. Meccanismo di handoff sessione tra FBOPortal e FBOAIGate (token firmato a breve
   scadenza, sul modello già usato dalle altre app con `internal_base_url`/`api_token`
   se applicabile, altrimenti da progettare).
3. Verifica: utente non loggato su FBOPortal → non deve poter aprire la console anche
   conoscendo l'URL diretto.

## Criteri di completamento
- Click sulla card in FBOPortal → console aperta senza ulteriore login
- Accesso diretto all'URL della console, senza passare da FBOPortal, negato
