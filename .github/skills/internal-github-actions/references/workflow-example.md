# Minimal Workflow Example

```yaml
name: CI
on: [pull_request]

permissions:
  contents: read
  id-token: write

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<FULL_SHA>
      - run: terraform fmt -check -recursive
```
