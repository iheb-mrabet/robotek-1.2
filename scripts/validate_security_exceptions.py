#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
POLICY_FILE = ROOT / "security" / "exceptions.yaml"
MAX_LIFETIME_DAYS = 90
ALLOWED_TOOLS = {"cppcheck", "gitleaks", "semgrep", "trivy-fs", "trivy-image"}
REQUIRED_FIELDS = {
    "id",
    "tool",
    "rule",
    "path",
    "reason",
    "owner",
    "approved_by",
    "created_on",
    "expires_on",
    "ticket",
}
ID_PATTERN = re.compile(r"^SEC-EXC-\d{4}-\d{3}$")


def parse_date(value: Any, label: str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"{label} must use YYYY-MM-DD") from exc
    raise ValueError(f"{label} must be a date")


def main() -> int:
    try:
        document = yaml.safe_load(POLICY_FILE.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"Security exception policy failed: {exc}", file=sys.stderr)
        return 1

    if not isinstance(document, dict) or not isinstance(document.get("exceptions"), list):
        print("Security exception policy failed: exceptions must be a YAML list", file=sys.stderr)
        return 1

    errors: list[str] = []
    seen_ids: set[str] = set()
    today = date.today()

    for index, exception in enumerate(document["exceptions"], start=1):
        label = f"exception #{index}"
        if not isinstance(exception, dict):
            errors.append(f"{label} must be a mapping")
            continue

        missing = sorted(REQUIRED_FIELDS - exception.keys())
        if missing:
            errors.append(f"{label} is missing: {', '.join(missing)}")
            continue

        exception_id = exception["id"]
        label = str(exception_id)
        if not isinstance(exception_id, str) or not ID_PATTERN.fullmatch(exception_id):
            errors.append(f"{label}: id must match SEC-EXC-YYYY-NNN")
        elif exception_id in seen_ids:
            errors.append(f"{label}: duplicate id")
        else:
            seen_ids.add(exception_id)

        if exception["tool"] not in ALLOWED_TOOLS:
            errors.append(f"{label}: unsupported tool {exception['tool']!r}")
        if not isinstance(exception["rule"], str) or not exception["rule"].strip():
            errors.append(f"{label}: rule must be non-empty")
        if not isinstance(exception["path"], str) or not exception["path"].strip():
            errors.append(f"{label}: path must be non-empty")
        if not isinstance(exception["reason"], str) or len(exception["reason"].strip()) < 20:
            errors.append(f"{label}: reason must contain at least 20 characters")
        owner = exception["owner"]
        approver = exception["approved_by"]
        if not isinstance(owner, str) or not owner.strip():
            errors.append(f"{label}: owner must be non-empty")
        if not isinstance(approver, str) or not approver.strip():
            errors.append(f"{label}: approved_by must be non-empty")
        if isinstance(owner, str) and isinstance(approver, str) and owner == approver:
            errors.append(f"{label}: owner cannot approve their own exception")
        path = exception["path"]
        if isinstance(path, str) and (path.startswith("/") or ".." in Path(path).parts):
            errors.append(f"{label}: path must be repository-relative")
        if not isinstance(exception["ticket"], str) or not exception["ticket"].startswith(
            "https://"
        ):
            errors.append(f"{label}: ticket must be an HTTPS URL")

        try:
            created = parse_date(exception["created_on"], f"{label}.created_on")
            expires = parse_date(exception["expires_on"], f"{label}.expires_on")
        except ValueError as exc:
            errors.append(str(exc))
            continue

        if created > today:
            errors.append(f"{label}: created_on cannot be in the future")
        if expires <= created:
            errors.append(f"{label}: expires_on must be after created_on")
        if (expires - created).days > MAX_LIFETIME_DAYS:
            errors.append(f"{label}: lifetime cannot exceed {MAX_LIFETIME_DAYS} days")
        if expires < today:
            errors.append(f"{label}: expired on {expires.isoformat()}")

    if errors:
        print("Security exception policy failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"Security exception policy passed: {len(document['exceptions'])} active exception(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
