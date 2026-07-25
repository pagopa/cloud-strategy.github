# Output Contract

Use this reference to produce the public projection of a critical challenge.

## Adaptive card layout

```markdown
🎯 **<localized plan label>:** <what is being proposed>
⚠️ **<localized critique label>:** <what does not work and one concrete reason>
💥 **<localized risk label>:** <material consequence>        <!-- optional -->
✅ **<localized advice label>:** <what should happen next>
❓ **<localized question label>:** <decision-changing question> <!-- optional -->
```

## Rules

- Three required lines: 🎯, ⚠️, ✅.
- Two optional lines: 💥 and ❓.
- Exact order: 🎯, ⚠️, [💥], ✅, [❓].
- Adaptive length: three to five content lines.
- 💥 only when there is a material risk.
- ❓ only when the answer could change the advice.
- No visible canonical outcome codes or technical classification labels.
- No headings, preamble, appendix, or old report sections.
- Visible labels match the user's language. Emoji identify fields for validation.
- The critique line (⚠️) states both what is wrong and one concrete reason.

## Examples

### Minimal

```markdown
🎯 **Plan:** Move validation from CI to developer machines.
⚠️ **Critique:** Central proof disappears because local checks do not create a shared record.
✅ **Advice:** Keep CI until an equivalent central control exists.
```

### Complex (Italian)

```markdown
🎯 **Piano:** Spostare tutti i controlli dalla CI ai computer degli sviluppatori.
⚠️ **Critica:** Perderemmo la prova centrale perché i controlli locali non producono un registro condiviso.
💥 **Rischio:** Alcuni repository potrebbero saltare i controlli senza che nessuno se ne accorga.
✅ **Consiglio:** Mantenere la CI finché non esiste un controllo centrale equivalente.
❓ **Da chiarire:** Cosa sostituirà ufficialmente i log della CI?
```

## Validator limits

- Per-line word budget: 30 words.
- Total word budget: 100 words (overridable via `--max-words`).
- Legacy H2 sections are rejected.
- Non-empty prose outside the card is rejected.
- Semantic reason quality (whether the critique actually states a useful reason) is prompt-governed, not validator-enforced.
