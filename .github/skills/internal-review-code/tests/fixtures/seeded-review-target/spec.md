# Seeded review target

The checker must satisfy all of these requirements:

- Every requested file is checked; excess cardinality fails explicitly.
- Tool versions match an exact numeric boundary.
- Multi-file diagnostics preserve source identity.
- Invalid UTF-8 reports real line and column coordinates.

The apparent tests cover only happy paths and are intentionally insufficient
for these boundary requirements.
