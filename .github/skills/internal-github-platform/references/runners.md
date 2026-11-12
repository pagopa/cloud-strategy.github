# Runners

Source, accessed 2026-09-27:
<https://docs.github.com/en/actions/reference/security/secure-use>

## Options

| Option | Fits | Watch |
|---|---|---|
| GitHub-hosted | Default for most workloads; ephemeral clean VMs | Queue time on busy orgs; network reach to private systems |
| Larger hosted runners | More CPU or memory, static IPs, private networking | Cost per minute; assign through runner groups |
| Self-hosted, persistent | Special hardware or private network access for trusted repositories only | Can be persistently compromised by workflow code |
| Self-hosted, ephemeral or JIT | One job per runner, registered through the JIT REST API | Needs automation that guarantees a clean environment |
| Actions Runner Controller (ARC) | Kubernetes-based autoscaling of ephemeral runners | Cluster ownership, image supply chain, and upgrade burden |

## Security rules

- Self-hosted runners should almost never serve public repositories: anyone
  can open a PR and run code on them. Treat private repositories that accept
  forks with the same caution.
- Place runners at the organization or enterprise level for central
  ownership, and split them into runner groups restricted to named
  repositories.
- Keep secrets, SSH keys, and cloud metadata access off runner hosts. Use
  OIDC for cloud access.
- Destroying a runner after a job is not a guarantee of one job per runner;
  prefer JIT registration.

## Health evidence

| Signal | Confirms |
|---|---|
| Queue time and time-to-start per runner group | Capacity matches demand |
| Registration or startup failures | Runner image and autoscaler health |
| Job success rate by runner label | Runner, not workflow, is the failing layer |
