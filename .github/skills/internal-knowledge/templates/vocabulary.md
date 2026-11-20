<!-- knowledge:managed:start -->
# Knowledge Vocabulary

This layout is DDD-inspired. Use the plain names, not DDD names as identities.

| Plain term | Meaning | Closest DDD concept |
| --- | --- | --- |
| Area | Durable responsibility with a Purpose and ownership boundary | Domain |
| Purpose | Why an Area exists, whom it serves, and what it excludes | Domain Vision Statement |
| Topic | A language and Rules boundary within an Area; usually aligned with one Subdomain, not required | Bounded Context |
| Glossary | A Topic's resolved definitions | Ubiquitous Language |
| Rules | Evidenced normative requirements | Invariants |
| Glossary Map | Topic index and evidenced relationships | Context Map |
| Shared Terms | Identical meanings across Topics; not itself a Topic | Shared Kernel only with declared joint ownership |
| Core / Supporting / Commodity | A Topic's strategic role listed in its Area README | Core / Supporting / Generic Subdomain |

Same word with different meanings stays in separate Topic glossaries. Create
Shared Terms only on the first real shared meaning. An Area has no Glossary.
Do not invent relationship patterns or classify Areas as Core or Commodity.

Propose definitions and Rules in conversation. Write them only after an
explicit user "yes"; never create an Area or Topic without approval.
<!-- knowledge:managed:end -->
