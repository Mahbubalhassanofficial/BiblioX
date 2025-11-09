"""
themes.py — BiblioX / CBIS Visualization Style Manager
------------------------------------------------------
Chulalongkorn–B'Deshi color identity, typography, and unified
Matplotlib + Seaborn + SciencePlots configuration for publication-grade
bibliometric visualizations (600 DPI, Times New Roman).

Author: Mahbub Hassan
Affiliation: Department of Civil Engineering, Chulalongkorn University
Lab: B'Deshi Emerging Research Lab
"""

from __future__ import annotations
import contextlib
import colorsys
import json
from pathlib import Path
from typing import Iterable, List

import matplotlib as mpl
import seaborn as sns
from matplotlib import font_manager

# ============================================================
# 1) OFFICIAL + SCIENTIFICALLY SAFE PALETTES
# ============================================================
CHULA_BDESHI = ["#E4007C", "#4B2E83", "#A7C947", "#707070", "#008CBA"]

# Okabe–Ito (color-blind safe)
OKABE_ITO = ["#000000", "#E69F00", "#56B4E9", "#009E73",
             "#F0E442", "#0072B2", "#D55E00", "#CC79A7"]

# Tableau 10 (widely used, balanced)
TABLEAU10 = ["#4E79A7", "#F28E2B", "#E15759", "#76B7B2",
             "#59A14F", "#EDC949", "#AF7AA1", "#FF9DA7",
             "#9C755F", "#BAB0AC"]

PALETTES = {
    "Chula–B'Deshi": CHULA_BDESHI,
    "IEEE Gray-Blue": ["#0050A0", "#7EAED6", "#EAEAEA", "#333333", "#007ACC"],
    "Elsevier Blue": ["#003366", "#005B96", "#B3CDE0", "#F2F2F2", "#808080"],
    "Nature Soft": ["#264653", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51"],
    "Monochrome": ["#111111", "#444444", "#777777", "#AAAAAA", "#DDDDDD"],
    "Minimal Pastel": ["#A8DADC", "#457B9D", "#1D3557", "#F1FAEE", "#E63946"],
    "Okabe–Ito (CB-safe)": OKABE_ITO,
    "Tableau 10": TABLEAU10,
}

# ============================================================
# 2) FONT REGISTRATION
# ============================================================
def register_times(ttf_path: str | None = None) -> None:
    """
    Register Times New Roman font if not natively available.
    Pass a .ttf path in deployments lacking Times.
    """
    if ttf_path:
        try:
            font_manager.fontManager.addfont(ttf_path)
        except Exception as e:
            print(f"[WARN] Could not register font from {ttf_path}: {e}")

# ============================================================
# 3) COLOR VALIDATION & LUMINANCE
# ============================================================
def _is_hex(c: str) -> bool:
    return isinstance(c, str) and c.startswith("#") and len(c) in {4, 7}

def validate_palette(palette: Iterable[str]) -> List[str]:
    """Ensure all entries are valid HEX; drop invalid; guarantee ≥1 color."""
    valid = [c for c in palette if _is_hex(c)]
    if not valid:
        valid = ["#000000"]
        print("[WARN] Palette invalid/empty. Falling back to #000000.")
    return valid

def luminance(hex_color: str) -> float:
    """Relative luminance (0=dark, 1=light) for theme adaptation."""
    r, g, b = (int(hex_color[i:i+2], 16)/255.0 for i in (1, 3, 5))
    # colorsys uses HLS; we only need L
    return colorsys.rgb_to_hls(r, g, b)[1]

# ============================================================
# 4) SIZE HELPERS
# ============================================================
def mm_to_inches(mm: float) -> float:
    return mm / 25.4

FIG_SIZES_MM = {
    "single": (85, 60),
    "one_half": (120, 80),
    "double": (175, 110),
    "poster": (210, 148),
}

def get_figsize_inches(size_key: str = "single") -> tuple[float, float]:
    wmm, hmm = FIG_SIZES_MM.get(size_key, FIG_SIZES_MM["single"])
    return mm_to_inches(wmm), mm_to_inches(hmm)

# ============================================================
# 5) STYLE APPLICATION (Seaborn + SciencePlots + MPL)
# ============================================================
def apply_pub_style(
    palette: Iterable[str] = CHULA_BDESHI,
    science_theme: str = "science",
    dark_mode: bool = False,
) -> None:
    """
    Apply unified Seaborn + SciencePlots theme.
    - Times New Roman
    - 600 DPI tight export
    - Thin axes/ticks, neutral grid
    - Optional dark_mode for presentations
    """
    palette = validate_palette(palette)
    bg = "#111111" if dark_mode else "#FFFFFF"
    fg = "#F2F2F2" if dark_mode else "#000000"
    gridc = "#444444" if dark_mode else "#DDDDDD"

    # SciencePlots theme (graceful fallback)
    try:
        mpl.style.use([science_theme, "no-latex"])
    except Exception:
        mpl.style.use("default")

    # Seaborn + Matplotlib coherence
    sns.set_theme(style="whitegrid", palette=palette)
    mpl.rcParams.update({
        # Font & text
        "font.family": "Times New Roman",
        "font.size": 9,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "text.color": fg,
        "axes.labelcolor": fg,
        "axes.titlecolor": fg,
        "xtick.color": fg,
        "ytick.color": fg,
        # Axes & figure
        "axes.linewidth": 0.8,
        "axes.edgecolor": fg,
        "axes.facecolor": bg,
        "figure.facecolor": bg,
        # Saving
        "figure.dpi": 120,
        "savefig.dpi": 600,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.01,
        # Grid
        "grid.color": gridc,
        # Tick geometry
        "xtick.major.size": 2,
        "ytick.major.size": 2,
    })
    mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=list(palette))

# ============================================================
# 6) CONTEXT MANAGER: TEMPORARY STYLE
# ============================================================
@contextlib.contextmanager
def temporary_style(
    palette: Iterable[str] = CHULA_BDESHI,
    science_theme: str = "science",
    dark_mode: bool = False,
):
    """
    Temporarily apply style inside a `with` block.
    Example:
        with temporary_style(PALETTES["Okabe–Ito (CB-safe)"]):
            fig, ax = plt.subplots(...)
            ...
    """
    old_rc = mpl.rcParams.copy()
    try:
        apply_pub_style(palette=palette, science_theme=science_theme, dark_mode=dark_mode)
        yield
    finally:
        mpl.rcParams.update(old_rc)

# ============================================================
# 7) UTILITIES: ACTIVE PALETTE & EXPORT
# ============================================================
def current_palette(n: int | None = None) -> list[str]:
    """
    Return the active Matplotlib color cycle (optionally first n colors).
    """
    cycle = mpl.rcParams.get("axes.prop_cycle")
    cols = [d["color"] for d in cycle]
    return cols[:n] if n else cols

def export_mplstyle(path: str | Path, palette: Iterable[str] | None = None) -> Path:
    """
    Export an .mplstyle file reflecting the current rcParams (and optional palette).
    Useful for sharing exact style with collaborators or journals.
    """
    path = Path(path)
    rc = mpl.rcParams.copy()
    if palette is not None:
        rc["axes.prop_cycle"] = mpl.cycler(color=list(validate_palette(palette)))
    lines = [f"{k}: {v}" for k, v in sorted(rc.items())]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path

def save_palette_json(path: str | Path, palette: Iterable[str]) -> Path:
    """Save a palette to JSON for app-level theme persistence."""
    path = Path(path)
    path.write_text(json.dumps(list(validate_palette(palette)), ensure_ascii=False, indent=2), encoding="utf-8")
    return path
