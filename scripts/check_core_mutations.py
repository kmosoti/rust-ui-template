"""Check two deliberate defects against the real Rust tests in disposable copies.

A compiler error is NOT a killed mutant. The selected named test must execute
and fail. The real checkout is never modified. This is test sensitivity evidence,
not formal verification or a general mutation-testing framework.
"""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MUTATIONS = (
    (
        "accept-stale-pending-result",
        "if self.active != Some(id) {",
        "if self.active.is_none() {",
        "tests::stale_completion_cannot_clear_a_pending_newer_request",
    ),
    (
        "wrap-request-identifiers",
        "let next = self.last_issued.checked_add(1).ok_or(IdExhausted)?;",
        "let next = self.last_issued.wrapping_add(1);",
        "tests::highest_id_is_usable_and_exhaustion_is_atomic",
    ),
)


def main() -> None:
    for name, original, replacement, test in MUTATIONS:
        with tempfile.TemporaryDirectory(prefix="rust-ui-mutation-") as temporary:
            checkout = Path(temporary)
            for filename in ("Cargo.toml", "Cargo.lock", "rust-toolchain.toml"):
                shutil.copy2(ROOT / filename, checkout / filename)
            shutil.copytree(ROOT / "crates", checkout / "crates")
            source = checkout / "crates/app-core/src/lib.rs"
            text = source.read_text(encoding="utf-8")
            if text.count(original) != 1:
                raise RuntimeError(f"{name}: expected exactly one mutation site; review the harness")
            source.write_text(text.replace(original, replacement, 1), encoding="utf-8")
            environment = dict(os.environ, CARGO_TERM_COLOR="never", CARGO_TARGET_DIR=str(checkout / "target"))
            result = subprocess.run(
                ["cargo", "test", "--locked", "--offline", "-p", "app-core", "--lib", test, "--", "--exact"],
                cwd=checkout,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=120,
                check=False,
            )
            if result.returncode == 0 or f"test {test} ... FAILED" not in result.stdout:
                print(result.stdout)
                raise RuntimeError(f"{name}: mutant survived or named test did not execute")
            print(f"PASS: {name} rejected by {test}")


if __name__ == "__main__":
    main()
