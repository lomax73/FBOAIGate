# FBOAIGate — identità visiva

## Nome

**FBOAIGate** — gateway di accesso sicuro al NUC Debian, con Claude dietro.
Nel wordmark le lettere `AI` vanno in accento blu: FBO**AI**Gate.

## Icona

Scudo (canale protetto, nessun port forward) contenente un cervello a due emisferi —
sinistro anatomico, destro fatto di piste da circuito stampato — sopra un prompt di
terminale `>_`.

Lettura: sicurezza + umano/macchina + riga di comando.

## File

| File | Uso |
|---|---|
| `fboaigate-icon.svg` | versione piena, da 48px in su |
| `fboaigate-icon-small.svg` | versione semplificata, sotto i 48px (favicon, launcher portale) |

Sotto i 48px i tratti sottili delle circonvoluzioni e delle piste si chiudono: usare
sempre la variante `-small`, dove l'emisfero sinistro è a massa piena e le piste sono
ridotte a tre linee spesse.

## Palette

| Ruolo | Hex | Note |
|---|---|---|
| Accento (scudo, cervello) | `#1f8fc4` | derivato dal blu FBOPortal `#27a5de`, scurito per reggere il contrasto su fondo notte |
| Spark (nodi circuito) | `#e0a340` | unico accento caldo: segna l'attività dell'AI |
| Simbolo (prompt) | `#eaf4f8` | l'input umano |
| Fondo tile | `#0f2029` → `#16303d` | gradiente diagonale |

L'ambra è riservata all'AI, il blu alla sicurezza, il bianco all'input: i tre colori non
vanno mescolati tra i tre ruoli.

## Tipografia

Wordmark e UI in monospace (`ui-monospace`, SF Mono, JetBrains Mono): è una console,
il monospace non è decorativo ma coerente col contenuto.
