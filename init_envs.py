#!/usr/bin/env python3
"""Sync GitHub Actions environment secrets from secrets.json."""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync GitHub env secrets from JSON")
    parser.add_argument(
        "--repo",
        default="6037-Title/admin-backend",
        help="Repository (owner/repo)",
    )
    parser.add_argument(
        "--env",
        default="prod",
        dest="environment",
        help="Environment name",
    )
    parser.add_argument(
        "--secrets-file",
        default="secrets.json",
        help="Path to secrets JSON file",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Delete all existing env secrets before adding new ones",
    )
    args = parser.parse_args()

    if not shutil.which("gh"):
        print("gh CLI is required", file=sys.stderr)
        sys.exit(1)

    secrets_path = Path(args.secrets_file)
    if not secrets_path.is_file():
        print(f"Secrets file not found: {secrets_path}", file=sys.stderr)
        sys.exit(1)

    with open(secrets_path, encoding="utf-8") as f:
        secrets = json.load(f)

    if not isinstance(secrets, list):
        print("secrets.json must be a list of {name, value} objects", file=sys.stderr)
        sys.exit(1)

    repo, env = args.repo, args.environment
    print(f"Repo: {repo}")
    print(f"Environment: {env}")
    print()

    if args.clear:
        print("Clearing all existing secrets...")
        result = run(
            ["gh", "secret", "list", "--repo", repo, "--env", env, "--json", "name"],
            capture_output=True,
        )
        data = json.loads(result.stdout)
        for item in data:
            name = item.get("name")
            if not name:
                continue
            print(f"→ Deleting secret: {name}")
            run(["gh", "secret", "delete", name, "--repo", repo, "--env", env])
        print()

    print(f"Adding new secrets from {secrets_path}:")
    for entry in secrets:
        name = entry.get("name")
        value = entry.get("value")
        if name is None or value is None:
            print(f"  Skipping invalid entry: {entry}", file=sys.stderr)
            continue
        print(f"→ Setting secret: {name}")
        run(
            ["gh", "secret", "set", name, "--repo", repo, "--env", env, "-b", value],
            capture_output=True,
        )

    print()
    print("Done.")


if __name__ == "__main__":
    main()
