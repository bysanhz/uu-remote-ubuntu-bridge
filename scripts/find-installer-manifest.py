#!/usr/bin/env python3
"""Find an approved UU release manifest by installer SHA-256."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("installer", type=Path)
    parser.add_argument(
        "--patches",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "patches",
    )
    args = parser.parse_args()

    installer = args.installer.expanduser().resolve()
    actual = sha256_file(installer)
    matches: list[tuple[str, Path]] = []

    for manifest_path in sorted(args.patches.glob("uu-remote-*.json")):
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            print(f"warning: cannot read {manifest_path}: {error}", file=sys.stderr)
            continue
        if data.get("review_status") != "approved":
            continue
        installer_data = data.get("installer")
        if not isinstance(installer_data, dict):
            continue
        if installer_data.get("sha256") == actual:
            matches.append((str(data.get("version", "unknown")), manifest_path.resolve()))

    if len(matches) == 1:
        version, manifest_path = matches[0]
        print(f"{version}\t{manifest_path}")
        return 0
    if len(matches) > 1:
        print(
            f"error: installer hash {actual} matches multiple approved manifests",
            file=sys.stderr,
        )
        return 2

    print(actual)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
