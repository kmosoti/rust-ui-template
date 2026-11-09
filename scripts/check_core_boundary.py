"""Check the actual Cargo metadata graph, not an architectural drawing.

The initial core deliberately has no dependencies of any kind. Widen this
contract only through a reviewed decision and a corresponding target matrix.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


def violations(metadata: dict[str, Any]) -> list[str]:
    """Fail closed on absent, duplicate, or externally resolved core packages."""
    candidates = [p for p in metadata.get("packages", []) if p.get("name") == "app-core"]
    if len(candidates) != 1:
        return ["expected exactly one app-core package"]
    core = candidates[0]
    problems: list[str] = []
    if core.get("id") not in metadata.get("workspace_members", []):
        problems.append("app-core must be a workspace member")
    if core.get("source") is not None:
        problems.append("app-core must resolve to local workspace source")
    dependencies = core.get("dependencies")
    if not isinstance(dependencies, list):
        problems.append("missing declared dependency metadata")
    elif dependencies:
        problems.append("app-core must have zero declared dependencies, including target/dev/build")
    resolve = metadata.get("resolve")
    nodes = resolve.get("nodes", []) if isinstance(resolve, dict) else []
    matches = [n for n in nodes if n.get("id") == core.get("id")]
    if len(matches) != 1:
        problems.append("missing resolved core node; do not use cargo metadata --no-deps")
    else:
        edges = matches[0].get("dependencies")
        if not isinstance(edges, list) or edges:
            problems.append("app-core must have zero resolved dependency edges")
    return problems


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python3 scripts/check_core_boundary.py <cargo-metadata.json>", file=sys.stderr)
        return 2
    try:
        metadata = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        if not isinstance(metadata, dict):
            raise ValueError("metadata must be an object")
        problems = violations(metadata)
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"invalid Cargo metadata: {error}", file=sys.stderr)
        return 2
    if problems:
        print("\n".join(f"FAIL: {message}" for message in problems), file=sys.stderr)
        return 1
    print("PASS: actual Cargo graph has a local dependency-free app-core")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
