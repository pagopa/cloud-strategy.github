# Persistence, Transactions, and Testing

Load this file when the Spring Boot task is mainly about repositories, transactions, database integration, or test strategy.

## Data Boundaries

| Problem | Prefer | Avoid |
| --- | --- | --- |
| HTTP layer needs data | Map entities to DTOs or dedicated view models | Returning entities directly unless already established |
| Repository abstraction | Spring Data repositories or small project-local interfaces | Business logic embedded in repository or controller layers |
| Transaction scope | Service-layer `@Transactional` on the narrow behavior that must be atomic | Broad class-level transactions applied by habit |

## Test Selection

| Goal | Prefer | Escalate only when |
| --- | --- | --- |
| Pure business logic | Plain unit tests with mocked collaborators | Spring wiring itself changes behavior |
| MVC endpoint behavior | `@WebMvcTest` | Security, converters, or full application wiring must be proven together |
| JPA mapping/query behavior | `@DataJpaTest` | The database integration depends on infrastructure outside the slice |
| Full application behavior | `@SpringBootTest` | Bootstrap or cross-cutting wiring is the thing being verified |

## Integration Guidance

- Use a plain unit test when Spring wiring is irrelevant.
- Use the smallest focused MVC or data slice when that slice proves the behavior.
- Use the full application context only when bootstrap or cross-cutting wiring is under test.
- Verify that custom scanning or configuration does not defeat slice isolation.
- Use a real Testcontainers database or external service only when the contract matters and a container runtime is available.
- For Boot Testcontainers integration, verify `@ServiceConnection`, `ConnectionDetails` precedence, the required test dependency setup, and the generic-container naming expected by the active Boot line.
- Keep fixture setup explicit and local to the test when possible, and preserve existing package structure and test conventions.
