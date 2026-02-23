#!/usr/bin/env python3
"""Revert screenshots that haven't meaningfully changed.

Compares newly captured screenshots against their git HEAD versions.
If the pixel difference is below the configured threshold (default 1%),
the new file is reverted to HEAD — preventing noise commits from minor
rendering variations (anti-aliasing, sub-pixel shifts, etc.).

Uses Pillow for image comparison, matching the stack in CLAUDE.md.
"""
import io
import json
import subprocess
from pathlib import Path

from PIL import Image


def load_threshold():
    """Read visual_diff_threshold from config/test-config.json."""
    config_path = Path("config/test-config.json")
    if config_path.exists():
        config = json.loads(config_path.read_text())
        return config.get("screenshots", {}).get("visual_diff_threshold", 0.01)
    return 0.01


def get_changed_screenshots():
    """Return list of screenshot PNGs that git considers modified."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "--", "screenshots/"],
        capture_output=True, text=True,
    )
    return [p for p in result.stdout.strip().splitlines() if p.endswith(".png")]


def git_show_head(path):
    """Return the bytes of a file at HEAD, or None if it doesn't exist."""
    result = subprocess.run(
        ["git", "show", f"HEAD:{path}"],
        capture_output=True,
    )
    if result.returncode == 0:
        return result.stdout
    return None


def pixel_diff_ratio(img_a, img_b):
    """Return fraction of pixels that differ between two same-size images."""
    if img_a.size != img_b.size:
        return 1.0  # different dimensions = fully changed

    pixels_a = list(img_a.getdata())
    pixels_b = list(img_b.getdata())
    total    = len(pixels_a)

    if total == 0:
        return 0.0

    diff_count = sum(1 for a, b in zip(pixels_a, pixels_b) if a != b)
    return diff_count / total


def revert_file(path):
    """Restore a file to its HEAD version."""
    subprocess.run(["git", "checkout", "HEAD", "--", path], check=True)


def main():
    threshold = load_threshold()
    changed   = get_changed_screenshots()

    if not changed:
        print("  No modified screenshots detected.")
        return

    print(f"  Checking {len(changed)} modified screenshot(s) (threshold={threshold:.1%})")

    reverted = 0
    kept     = 0

    for path in changed:
        head_bytes = git_show_head(path)
        if head_bytes is None:
            # New file — no previous version to compare
            print(f"    NEW  {path}")
            kept += 1
            continue

        try:
            img_old = Image.open(io.BytesIO(head_bytes))
            img_new = Image.open(path)
        except Exception as e:
            print(f"    SKIP {path} (cannot open: {e})")
            kept += 1
            continue

        ratio = pixel_diff_ratio(img_old, img_new)

        if ratio <= threshold:
            revert_file(path)
            print(f"    REVERT {path} (diff={ratio:.4%} <= {threshold:.1%})")
            reverted += 1
        else:
            print(f"    KEEP   {path} (diff={ratio:.4%} > {threshold:.1%})")
            kept += 1

    print(f"  Done: {reverted} reverted, {kept} kept")


if __name__ == "__main__":
    main()
