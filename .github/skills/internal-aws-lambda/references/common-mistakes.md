# Common mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Treating the handler as the business layer | Hard to test, high coupling to AWS events | Keep the handler thin and call testable helpers |
| Parsing every event inline differently | Inconsistent behavior and brittle error handling | Normalize one event contract per trigger type |
| Returning whole-batch failure for one bad SQS record | Causes replay storms and blocks healthy messages | Catch per-record failures and return failed IDs only when supported |
| Ignoring idempotency on async triggers | Duplicate deliveries create data corruption or repeated side effects | Use idempotent writes, dedupe keys, or safe upserts |
| Shipping large shared bundles to every function | Slower cold starts and harder ownership boundaries | Split by function responsibility and keep dependencies narrow |
| Putting secrets directly in environment variables | Rotation and exposure risks | Use Secrets Manager or SSM-backed retrieval patterns |
| Attaching Lambda to a VPC by default | Adds latency and networking failure modes | Keep it out of a VPC unless there is a concrete dependency |
| Mixing HTTP response shaping with core logic | Hard to reuse and easy to break integrations | Keep request mapping and response mapping at the edge |
