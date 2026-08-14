# Fase 4 — Bot Telegram

## Obiettivo
Inviare comandi al NUC da Telegram. Prompt e comportamento del bot: da definire con
l'utente quando arriva a questa fase (prompt fornito da lui).

## Prerequisiti
Fase 1 completata (tunnel attivo). Non dipende dalle fasi 2/3.

## Task da eseguire (in attesa del prompt dell'utente)

1. Bot Telegram sul NUC, connessione outbound-only verso le API Telegram (polling, non
   webhook — coerente con "nessuna porta esposta").
2. Whitelist esplicita degli `chat_id` autorizzati a inviare comandi.
3. Integrazione con Claude Code sul NUC secondo il prompt che l'utente fornirà.

## Criteri di completamento
Da definire in base al prompt del bot.

## Note
Questa fase resta bloccata finché l'utente non fornisce il prompt del bot: non procedere
autonomamente sul suo comportamento.
