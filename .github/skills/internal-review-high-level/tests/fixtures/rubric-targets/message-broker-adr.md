# ADR 0007: Scelta del broker di messaggi

## Stato

Proposta.

## Contesto

I servizi ordini e fatturazione scambiano eventi tramite chiamate HTTP
sincrone. I picchi di carico causano timeout a catena.

## Decisione

Adottiamo un broker di messaggi gestito per tutti gli eventi tra servizi.

## Conseguenze

- I servizi diventano disaccoppiati nel tempo.
- Serve un nuovo runbook per la gestione delle code.
