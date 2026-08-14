# Fase 5 — Hardening e monitoraggio

## Obiettivo
Rendere il sistema robusto e osservabile nel tempo, non solo funzionante al primo giro.

## Prerequisiti
Fasi 1-3 completate.

## Task da eseguire

1. Alert se il tunnel WireGuard cade e non si riconnette entro N minuti (stesso pattern
   di monitoraggio già presente in MKRemote).
2. Backup della configurazione del NUC (chiavi WireGuard, config firewall, config bot) —
   non i dati applicativi, quelli restano sul NUC.
3. Rotazione/scadenza dei token di sessione della console (Fase 3).
4. Rassegna hardening: `fail2ban` o equivalente su SSH (anche se già ristretto a `wg0`),
   audit log accessi.

## Criteri di completamento
- Alert testato (tunnel spento manualmente → notifica ricevuta)
- Backup configurazione verificato ripristinabile
