"""
themes.py — BiblioX / CBIS Visualization Style Manager
------------------------------------------------------
Defines Chulalongkorn–B'Deshi color identity, typography, 
and unified Matplotlib + Seaborn + SciencePlots configuration 
for publication-grade bibliometric visualizations.

Author: Mahbub Hassan
Affiliation: Department of Civil Engineering, Chulalongkorn University
Lab: B'Deshi Emerging Research Lab
"""

import matplotlib as mpl
import seaborn as sns
from matplotlib import font_manager
import colorsys

# ============================================================
# 1. OFFICIAL BRAND COLOR SETS
# ============================================================
CHULA_BDESHI = ["#E4007C", "#4B2E83", "#A7C947", "#707070", "#008CBA"]

PALETTES = {
    "Chula–B'Deshi": CHULA_BDESHI,
    "IEEE Gray-Blue": ["#0050A0", "#7EAED6", "#EAEAEA", "#333333", "#007ACC"],
    "Elsevier Blue": ["#003366", "#005B96", "#B3CDE0", "#F2F2F2", "#808080"],
    "Nature Soft": ["#264653", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51"],
    "Monochrome": ["#111111", "#444444", "#777777", "#AAAAAA", "#DDDDDD"],
    "Minimal Pastel": ["#A8DADC", "#457B9D", "#1D3557", "#F1FAEE", "#E63946"],
}


# ============================================================
# 2. FONT REGISTRATION
# ============================================================
def register_times(ttf_path: str | None = None):
    """
    Register Times New Roman font if not natively available.
    Pass a .ttf path (optional, for deployment environments lacking Times).
    """
    if ttf_path:
        try:
            font_manager.fontManager.addfont(ttf_path)
        except Exception as e:
            print(f"[WARN] Could not register font from {ttf_path}: {e}")


# ============================================================
# 3. COLOR VALIDATION & CONTRAST CHECK
# ============================================================
def validate_palette(palette: list[str]) -> list[str]:
    """
    Ensure all colors are valid HEX codes; correct or remove invalid entries.
    """
    valid = []
    for c in palette:
        if isinstance(c, str) and c.startswith("#") and len(c) in {4, 7}:
            valid.append(c)
        else:
            print(f"[WARN] Invalid color skipped: {c}")
    if not valid:
        valid = ["#000000"]
    return valid


def luminance(hex_color: str) -> float:
    """Compute relative luminance (0=dark, 1=light) for theme adaptation."""
    rgb = [int(hex_color[i:i+2], 16) / 255.0 for i in (1, 3, 5)]
    return colorsys.rgb_to_hls(*rgb)[1]


# ============================================================
# 4. PUBLICATION STYLE APPLICATOR
# ============================================================
def apply_pub_style(
    palette: list[str] = CHULA_BDESHI,
    science_theme: str = "science",
    dark_mode: bool = False,
):
    """
    Apply unified Seaborn + SciencePlots theme.

    Args:
        palette: list of HEX colors (max 10)
        science_theme: one of ['science', 'nature', 'ieee', 'grid']
        dark_mode: switch for dark background presentation mode
    """
    palette = validate_palette(palette)
    bg_color = "#FFFFFF" if not dark_mode else "#111111"
    text_color = "#000000" if not dark_mode else "#F2F2F2"

    # SciencePlots (if installed)
    try:
        mpl.style.use([science_theme, "no-latex"])
    except Exception:
        mpl.style.use("default")

    # Seaborn + Matplotlib coherence
    sns.set_theme(style="whitegrid", palette=palette)
    mpl.rcParams.update({
        # Font and text
        "font.family": "Times New Roman",
        "font.size": 9,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        # Layout / Figure
        "axes.linewidth": 0.8,
        "axes.edgecolor": text_color,
        "axes.facecolor": bg_color,
        "figure.facecolor": bg_color,
        "figure.dpi": 120,
        "savefig.dpi": 600,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.01,
        "grid.color": "#DDDDDD" if not dark_mode else "#444444",
        # Ticks
        "xtick.color": text_color,
        "ytick.color": text_color,
        "xtick.major.size": 2,
        "ytick.major.size": 2,
        # Legend and labels
        "text.color": text_color,
        "axes.labelcolor": text_color,
        "axes.titlecolor": text_color,
    })
    mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=palette)


# ============================================================
# 5. SIZE CONVERSION UTILS
# ============================================================
def mm_to_inches(mm: float) -> float:
    """Convert millimeters to inches for figure sizing."""
    return mm / 25.4


FIG_SIZES_MM = {
    "single": (85, 60),
    "one_half": (120, 80),
    "double": (175, 110),
    "poster": (210, 148),
}
