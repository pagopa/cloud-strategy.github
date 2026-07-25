# Review Usefulness Replay Fixture

Use this illustrative output shape when validating that AI-resource reviews are decision-useful
without becoming long reports.

## Input

- Target: the `local-ai-chatgpt-prompt-creator` skill bundle behavior.
- Branch diff tightens only the `coach-personale` validator profile.
- Live `coach-personale` prompt pack passes the validator with the required
  support pack.
- No focused `coach-personale` profile test exists.
- Focused pytest execution is unavailable in the active environment.
- Sync and inventory evidence do not show material drift.

## Expected Review Behavior

- Reports no immediate runtime break observed.
- Reports one material low-severity finding or decision note about missing
  profile-specific tests.
- Explains why the low finding matters.
- Uses an evidence digest instead of raw command output.
- Includes a decision trace that rules out unsupported drift or runtime-break
  claims.
- Names unavailable pytest execution as residual risk.
- Recommends the smallest useful next step: add focused `coach-personale`
  pass/fail validator tests.
- Does not invent additional findings to make the review look more substantial.

## Compressed Output Shape

```markdown
🔎 **Esito:** approvabile con un miglioramento facoltativo.
📌 **Perché:** il prompt pack passa il validator, ma il profilo non ha una regressione dedicata.
🧪 **Evidenza:** validator e sync verificati; pytest focalizzato non disponibile.
👉 **Azione richiesta:** nessuna correzione obbligatoria; chiedi una fase separata per aggiungere S1 se vuoi ridurre il rischio.

## 💡 Suggerimenti (1)

- **S1:** aggiungere test pass/fail specifici per il profilo `coach-personale`.
```
