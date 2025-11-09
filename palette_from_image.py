"""
palette_from_image.py — CBIS / BiblioX Color Palette Extractor
--------------------------------------------------------------
Extracts dominant color palettes from uploaded images using K-Means,
then harmonizes and exports them for use in figures or dashboards.

Author: Mahbub Hassan
Affiliation: Department of Civil Engineering, Chulalongkorn University
Lab: B'Deshi Emerging Research Lab
"""

from __future__ import annotations
from pathlib import Path
from typing import List
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import colorsys
import json
import matplotlib.pyplot as plt

# ============================================================
# 1. CORE EXTRACTION
# ============================================================
def extract_palette(image_file: str | Path, k: int = 6, random_state: int = 42) -> List[str]:
    """
    Extract a color palette from an image using K-Means clustering.
    Returns a list of HEX colors sorted by luminance (dark → light).
    """
    im = Image.open(image_file).convert("RGB")
    arr = np.array(im).reshape(-1, 3)
    n = min(25000, arr.shape[0])
    idx = np.random.default_rng(random_state).choice(arr.shape[0], size=n, replace=False)
    sample = arr[idx]

    km = KMeans(n_clusters=k, n_init=8, random_state=random_state)
    km.fit(sample)
    centers = km.cluster_centers_.astype(int)

    # Sort by luminance (perceptual brightness)
    lum = 0.2126 * centers[:, 0] + 0.7152 * centers[:, 1] + 0.0722 * centers[:, 2]
    centers = centers[np.argsort(lum)]
    return [f"#{r:02X}{g:02X}{b:02X}" for r, g, b in centers]

# ============================================================
# 2. HARMONIZATION
# ============================================================
def complementary_palette(hex_colors: List[str]) -> List[str]:
    """Generate complementary colors for given HEX palette."""
    comps = []
    for hex_code in hex_colors:
        rgb = [int(hex_code[i : i + 2], 16) / 255 for i in (1, 3, 5)]
        h, l, s = colorsys.rgb_to_hls(*rgb)
        h = (h + 0.5) % 1.0
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        comps.append(f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}")
    return comps

def merge_palettes(p1: List[str], p2: List[str]) -> List[str]:
    """Interleave two palettes for balanced diversity."""
    return [c for pair in zip(p1, p2) for c in pair]

# ============================================================
# 3. PREVIEW UTILITIES
# ============================================================
def preview_palette(palette: List[str], figsize=(6, 1), savepath: str | None = None):
    """Display or save palette as color swatch bar."""
    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow([[(int(c[1:3], 16)/255, int(c[3:5], 16)/255, int(c[5:7], 16)/255) for c in palette]])
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("Extracted Palette", fontsize=10, fontfamily="Times New Roman")
    if savepath:
        plt.savefig(savepath, bbox_inches="tight", dpi=600)
    plt.show()

# ============================================================
# 4. EXPORT FUNCTIONS
# ============================================================
def export_palette_json(palette: List[str], path: str = "vault/palette.json") -> Path:
    """Export palette to JSON."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(palette, indent=2), encoding="utf-8")
    return Path(path)

def export_palette_mplstyle(palette: List[str], path: str = "vault/palette.mplstyle") -> Path:
    """Export palette as Matplotlib style file."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    lines = [f"axes.prop_cycle: cycler('color', {palette})"]
    Path(path).write_text("\n".join(lines), encoding="utf-8")
    return Path(path)

# ============================================================
# 5. DEMO
# ============================================================
def _demo():
    """Demonstrate palette extraction and visualization."""
    img = "sample_image.jpg"  # Replace with your file
    palette = extract_palette(img, k=6)
    comp = complementary_palette(palette)
    merged = merge_palettes(palette, comp)
    preview_palette(merged)
    export_palette_json(merged)
    export_palette_mplstyle(merged)
    print("✅ Palette extracted and exported.")

if __name__ == "__main__":
    _demo()
