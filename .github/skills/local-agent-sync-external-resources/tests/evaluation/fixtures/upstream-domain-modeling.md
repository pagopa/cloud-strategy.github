---
name: domain-modeling
description: Build and sharpen a project's domain model.
---

# Domain Modeling

## File structure

```
/
├── GLOSSARY-MAP.md
├── docs/
│   └── adr/
├── src/
│   ├── ordering/
│   │   ├── GLOSSARY.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── billing/
│       ├── GLOSSARY.md
│       └── docs/adr/
```

Create files lazily when the first term is resolved.

## During the session

When a term is resolved, update `GLOSSARY.md` right there.
Use `GLOSSARY-FORMAT.md`.
