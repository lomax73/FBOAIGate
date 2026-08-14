# Fase 1 — Tunnel sicuro per gli host registrati

## Obiettivo
Ogni host (`Target`) apre lui stesso la connessione verso l'hub (WireGuard, outbound) —
nessuna porta aperta sul lato host, nessun port forward, che si tratti del NUC di casa o
di una VPS con IP pubblico. Da fuori, l'host è irraggiungibile via SSH finché non è lui a
chiamare l'hub.

## Prerequisiti
Fase 0 completata (hub dedicato + modello `Target`).

## Task da eseguire

1. **Hub WireGuard**: interfaccia `wg0` sull'hub, un peer per ogni `Target` registrato,
   provisioning della chiave e dell'IP VPN automatizzato quando si aggiunge un host.
2. **WireGuard su ciascun host**: chiave privata generata *sull'host stesso* (mai
   trasmessa altrove), configurata per connettersi all'hub su UDP.
3. **Firewall su ciascun host** (`nftables`/`ufw`): deny all in entrata di default,
   eccetto sulla sola interfaccia `wg0`.
4. **SSH su ciascun host**: binding solo su `wg0` (non su `0.0.0.0`), autenticazione a
   sola chiave, niente password.
5. **Verifica di rottura**, ripetuta per ogni host aggiunto: da fuori tramite interfaccia
   pubblica → SSH deve fallire/non rispondere. Dall'hub via `wg0` → deve funzionare.

## Criteri di completamento
- Tunnel WireGuard stabile per il NUC, si riconnette da solo se cade
- SSH raggiungibile solo tramite `wg0` su tutti gli host registrati
- Nessuna porta SSH in ascolto sull'interfaccia pubblica (verificato con `nmap` esterno)
- Procedura di onboarding di un nuovo host documentata e ripetibile (per quando arriverà
  la VPS)

## Note
Il "protetto" richiesto dall'utente si gioca qui: il tunnel cifra il traffico, il
firewall impedisce qualunque accesso che non passi dal tunnel — indipendentemente da
quanti e quali host vengono aggiunti nel tempo.
