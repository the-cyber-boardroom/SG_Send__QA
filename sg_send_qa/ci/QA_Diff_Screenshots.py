"""Type_Safe class for screenshot diffing and revert logic.

Compares newly captured screenshots against their git HEAD versions.
If the pixel difference is below the configured threshold (default 1%),
the new file is reverted to HEAD — preventing noise commits from minor
rendering variations (anti-aliasing, sub-pixel shifts, etc.).
"""
import io
import json
import subprocess
from pathlib import Path

from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self as Type_Safe

from PIL import Image


class QA_Diff_Screenshots(Type_Safe):
    threshold     : float = 0.01
    screenshots_dir: str  = "sg_send_qa__site/"
    config_path   : str   = "tests/config/test-config.json"

    # ------------------------------------------------------------------ config

    def load_threshold(self) -> float:
        """Read visual_diff_threshold from config/test-config.json."""
        path = Path(self.config_path)
        if path.exists():
            config = json.loads(path.read_text())
            return config.get("screenshots", {}).get("visual_diff_threshold", 0.01)
        return 0.01

    # -------------------------------------------------------------------- git

    def get_changed_screenshots(self) -> list:
        """Return list of screenshot PNGs that git considers modified."""
        result = subprocess.run(
            ["git", "diff", "--name-only", "--", self.screenshots_dir],
            capture_output=True, text=True,
        )
        return [p for p in result.stdout.strip().splitlines() if p.endswith(".png")]

    def git_show_head(self, path: str):
        """Return the bytes of a file at HEAD, or None if it doesn't exist."""
        result = subprocess.run(
            ["git", "show", f"HEAD:{path}"],
            capture_output=True,
        )
        if result.returncode == 0:
            return result.stdout
        return None

    def revert_file(self, path: str) -> None:
        """Restore a file to its HEAD version."""
        subprocess.run(["git", "checkout", "HEAD", "--", path], check=True)

    # --------------------------------------------------------------- diffing

    def pixel_diff_ratio(self, img_a: Image.Image, img_b: Image.Image) -> float:
        """Return fraction of pixels that differ between two same-size images."""
        if img_a.size != img_b.size:
            return 1.0  # different dimensions = fully changed

        pixels_a = list(img_a.get_flattened_data())
        pixels_b = list(img_b.get_flattened_data())
        total    = len(pixels_a)

        if total == 0:
            return 0.0

        diff_count = sum(1 for a, b in zip(pixels_a, pixels_b) if a != b)
        return diff_count / total

    # --------------------------------------------------------------- main run

    def run(self) -> dict:
        """Check all modified screenshots and revert those below threshold.

        Returns a summary dict with keys: threshold, checked, reverted, kept.
        """
        threshold = self.load_threshold()
        changed   = self.get_changed_screenshots()
        reverted  = 0
        kept      = 0

        if not changed:
            print("  No modified screenshots detected.")
            return {"threshold": threshold, "checked": 0, "reverted": 0, "kept": 0}

        print(f"  Checking {len(changed)} modified screenshot(s) (threshold={threshold:.1%})")

        for path in changed:
            head_bytes = self.git_show_head(path)
            if head_bytes is None:
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

            ratio = self.pixel_diff_ratio(img_old, img_new)

            if ratio <= threshold:
                self.revert_file(path)
                print(f"    REVERT {path} (diff={ratio:.4%} <= {threshold:.1%})")
                reverted += 1
            else:
                print(f"    KEEP   {path} (diff={ratio:.4%} > {threshold:.1%})")
                kept += 1

        print(f"  Done: {reverted} reverted, {kept} kept")
        return {"threshold": threshold, "checked": len(changed), "reverted": reverted, "kept": kept}
