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
    # [LIB-2026-04-01-014] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
    def get_changed_screenshots(self) -> list:
        """Return list of screenshot PNGs that git considers modified."""
        result = subprocess.run(
            ["git", "diff", "--name-only", "--", self.screenshots_dir],
            capture_output=True, text=True,
        )
        return [p for p in result.stdout.strip().splitlines() if p.endswith(".png")]

    def real_path_for_deterministic(self, det_path: str) -> str:
        """Return the real PNG path that pairs with a __deterministic.png."""
        return det_path.replace("__deterministic.png", ".png")

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

    channel_tolerance : int   = 5    # per-channel max difference to ignore (0-255)
                                     # rendering noise (anti-aliasing, sub-pixel shifts)
                                     # typically differs by 1-3 per channel across many
                                     # pixels — a tolerance of 5 absorbs this without
                                     # hiding real visual changes.

    def pixel_diff_ratio(self, img_a: Image.Image, img_b: Image.Image) -> float:
        """Return fraction of pixels that differ significantly between two images.

        A pixel is counted as different only if at least one channel differs by
        more than channel_tolerance (default 5 out of 255).  This absorbs
        rendering noise (anti-aliasing, sub-pixel font shifts) without hiding
        genuine visual changes.
        """
        if img_a.size != img_b.size:
            return 1.0  # different dimensions = fully changed

        pixels_a = list(img_a.convert("RGB").get_flattened_data())
        pixels_b = list(img_b.convert("RGB").get_flattened_data())
        total    = len(pixels_a)

        if total == 0:
            return 0.0

        tol = self.channel_tolerance
        diff_count = sum(
            1 for a, b in zip(pixels_a, pixels_b)
            if max(abs(x - y) for x, y in zip(a, b)) > tol
        )
        return diff_count / total

    # --------------------------------------------------------------- main run

    def run(self) -> dict:
        """Check all modified screenshots and revert those below threshold.

        Strategy:
          - Deterministic files (*__deterministic.png) are the primary diff
            signal.  If the deterministic diff is below threshold, BOTH the
            deterministic file and its real counterpart are reverted.
          - Real files that have a deterministic companion are skipped
            (the deterministic file governs the decision for that pair).
          - Real files with no deterministic companion are diffed directly
            (legacy / backwards-compat behaviour).

        Returns a summary dict with keys: threshold, checked, reverted, kept.
        """
        threshold = self.load_threshold()
        changed   = self.get_changed_screenshots()
        reverted  = 0
        kept      = 0

        if not changed:
            print("  No modified screenshots detected.")
            return {"threshold": threshold, "checked": 0, "reverted": 0, "kept": 0}

        # Split into deterministic and real sets
        det_paths  = {p for p in changed if p.endswith("__deterministic.png")}
        real_paths = set(changed) - det_paths

        # Real files whose deterministic pair is also changed → skip (pair governs)
        governed   = {self.real_path_for_deterministic(d) for d in det_paths}
        standalone = real_paths - governed   # real files with no det companion

        candidates = list(det_paths) + list(standalone)
        print(f"  Checking {len(candidates)} screenshot(s) (threshold={threshold:.1%})")

        for path in sorted(candidates):
            is_det    = path.endswith("__deterministic.png")
            real_path = self.real_path_for_deterministic(path) if is_det else path

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
                reverted += 1
                if is_det and real_path in real_paths:
                    # Revert the paired real PNG too
                    self.revert_file(real_path)
                    print(f"    REVERT {path} + {real_path} (diff={ratio:.4%} <= {threshold:.1%})")
                else:
                    print(f"    REVERT {path} (diff={ratio:.4%} <= {threshold:.1%})")
            else:
                print(f"    KEEP   {path} (diff={ratio:.4%} > {threshold:.1%})")
                kept += 1

        print(f"  Done: {reverted} reverted, {kept} kept")
        return {"threshold": threshold, "checked": len(candidates), "reverted": reverted, "kept": kept}
