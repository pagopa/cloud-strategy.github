from __future__ import annotations

import json
import os
import stat
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").is_file() and (parent / ".github").is_dir()
)
RESOLVER = REPO_ROOT / ".github/skills/internal-terraform-import/scripts/resolve-aws-identity-center-import.sh"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _make_aws_mock(tmp_path: Path, *, mode: str = "ok") -> tuple[Path, Path]:
    log = tmp_path / "aws.log"
    aws = tmp_path / "aws"
    _write_executable(
        aws,
        "#!/usr/bin/env bash\n"
        "set -eu\n"
        f"printf '%s\\n' \"$*\" >> {log!s}\n"
        f"mode={mode!r}\n"
        "case \"$*\" in\n"
        "  *'sts get-caller-identity'*)\n"
        "    [[ \"$mode\" != wrong-account ]] && printf '%s\\n' '{\"Account\":\"111111111111\"}' || printf '%s\\n' '{\"Account\":\"999999999999\"}'\n"
        "    ;;\n"
        "  *'sso-admin list-instances'*)\n"
        "    case \"$mode\" in zero) printf '%s\\n' '{\"Instances\":[]}' ;; multiple) printf '%s\\n' '{\"Instances\":[{\"IdentityStoreId\":\"d-1\"},{\"IdentityStoreId\":\"d-2\"}]}' ;; *) printf '%s\\n' '{\"Instances\":[{\"IdentityStoreId\":\"d-1\"}]}' ;; esac\n"
        "    ;;\n"
        "  *'identitystore get-group-id'*)\n"
        "    [[ \"$mode\" != group-failure ]] && printf '%s\\n' '{\"GroupId\":\"g-1\"}' || { printf '%s\\n' 'lookup failed' >&2; exit 2; }\n"
        "    ;;\n"
        "  *'identitystore get-user-id'*) printf '%s\\n' '{\"UserId\":\"u-1\"}' ;;\n"
        "  *'identitystore get-group-membership-id'*)\n"
        "    [[ \"$mode\" != incomplete ]] && printf '%s\\n' '{\"MembershipId\":\"m-1\"}' || printf '%s\\n' '{\"GroupId\":\"g-1\"}'\n"
        "    ;;\n"
        "  *) printf '%s\\n' 'unexpected aws call' >&2; exit 3 ;;\n"
        "esac\n",
    )
    return aws, log


def _run_resolver(
    tmp_path: Path,
    record: dict[str, object],
    *,
    mode: str = "ok",
    profile: str | None = "verified",
    account: str | None = "111111111111",
    region: str | None = "eu-west-1",
) -> tuple[subprocess.CompletedProcess[str], Path]:
    aws, log = _make_aws_mock(tmp_path, mode=mode)
    env = os.environ.copy()
    env["PATH"] = f"{aws.parent}{os.pathsep}{env['PATH']}"
    for key, value in {"AWS_PROFILE": profile, "EXPECTED_AWS_ACCOUNT_ID": account, "IDENTITY_CENTER_REGION": region}.items():
        if value is None:
            env.pop(key, None)
        else:
            env[key] = value
    result = subprocess.run([str(RESOLVER)], cwd=REPO_ROOT, env=env, input=json.dumps(record) + "\n", text=True, capture_output=True)
    return result, log


def _last_json(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    return json.loads(result.stdout.strip().splitlines()[-1])


def test_group_resolution_verifies_identity_and_uses_current_cli_namespaces(tmp_path: Path) -> None:
    result, log = _run_resolver(tmp_path, {"scope": "identity", "address": "aws_identitystore_group.groups[\"platform\"]", "resource_kind": "identitystore_group", "lookup": {"display_name": "Platform"}})
    assert result.returncode == 0
    assert _last_json(result) == {"canonical_id": "d-1/g-1", "import_id": "d-1/g-1", "identity_store_id": "d-1", "resource_kind": "identitystore_group"}
    calls = log.read_text(encoding="utf-8").splitlines()
    assert any("sts get-caller-identity" in call for call in calls)
    assert any("sso-admin list-instances" in call for call in calls)
    group_call = next(call for call in calls if "get-group-id" in call)
    assert '"AttributePath":"DisplayName"' in group_call
    assert '"AttributeValue":"Platform"' in group_call
    assert all("ssoadmin" not in call for call in calls)


def test_membership_resolution_uses_user_id_tagged_union(tmp_path: Path) -> None:
    result, log = _run_resolver(tmp_path, {"scope": "identity", "address": "aws_identitystore_group_membership.members[\"platform\"]", "resource_kind": "identitystore_group_membership", "lookup": {"display_name": "Platform", "user_name": "dana"}})
    assert result.returncode == 0
    assert _last_json(result)["canonical_id"] == "d-1/m-1"
    calls = log.read_text(encoding="utf-8").splitlines()
    assert any("identitystore get-user-id" in call and "UserName" in call for call in calls)
    membership_call = next(call for call in calls if "get-group-membership-id" in call)
    assert "--member-id UserId=u-1" in membership_call
    assert all("list-group-memberships" not in call for call in calls)


@pytest.mark.parametrize(
    ("mode", "expected_status"),
    [("wrong-account", "aws_error"), ("zero", "not_found"), ("multiple", "ambiguous"), ("group-failure", "aws_error"), ("incomplete", "aws_error")],
)
def test_lookup_failures_are_typed_and_never_emit_an_import_id(tmp_path: Path, mode: str, expected_status: str) -> None:
    resource_kind = "identitystore_group_membership" if mode == "incomplete" else "identitystore_group"
    result, _ = _run_resolver(tmp_path, {"scope": "identity", "address": "aws_identitystore_group.groups[\"platform\"]", "resource_kind": resource_kind, "lookup": {"display_name": "Platform", "user_name": "dana"}}, mode=mode)
    assert result.returncode != 0
    payload = _last_json(result)
    assert payload["status"] == expected_status
    assert "import_id" not in payload
    assert "canonical_id" not in payload


@pytest.mark.parametrize("missing", ["AWS_PROFILE", "IDENTITY_CENTER_REGION"])
def test_profile_and_identity_center_region_are_required_before_aws_calls(tmp_path: Path, missing: str) -> None:
    values = {"profile": "verified", "account": "111111111111", "region": "eu-west-1"}
    values["profile" if missing == "AWS_PROFILE" else "region"] = None
    result, log = _run_resolver(tmp_path, {"scope": "identity", "address": "aws_identitystore_group.groups[\"platform\"]", "resource_kind": "identitystore_group", "lookup": {"display_name": "Platform"}}, profile=values["profile"], account=values["account"], region=values["region"])
    assert result.returncode != 0
    assert not log.exists() or log.read_text(encoding="utf-8") == ""


def test_unsupported_resource_kind_fails_closed(tmp_path: Path) -> None:
    result, log = _run_resolver(tmp_path, {"scope": "identity", "address": "aws_unknown.value", "resource_kind": "unknown", "lookup": {}})
    assert result.returncode != 0
    assert _last_json(result)["status"] == "terraform_error"
    assert not log.exists() or log.read_text(encoding="utf-8") == ""


def test_resolver_source_has_no_deprecated_or_unsafe_fallbacks() -> None:
    text = RESOLVER.read_text(encoding="utf-8")
    assert "ssoadmin" not in text
    assert "GROUPS=" not in text
    assert "list-group-memberships" not in text
    assert ".Memberships" not in text
    assert ".GroupMemberships" not in text
