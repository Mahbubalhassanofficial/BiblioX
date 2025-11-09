import matplotlib as mpl
from matplotlib import font_manager

CHULA_PALETTE = ["#E4007C", "#4B2E83", "#A7C947", "#707070", "#008CBA"]

def register_times(ttf_path=None):
    if ttf_path:
        try:
            font_manager.fontManager.addfont(ttf_path)
        except Exception:
            pass

def apply_pub_style(palette=CHULA_PALETTE):
    mpl.rcParams.update({
        "font.family": "Times New Roman",
        "font.size": 9, "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
        "legend.fontsize": 8, "axes.linewidth": 0.8,
        "xtick.major.size": 2, "ytick.major.size": 2,
        "savefig.dpi": 600, "savefig.bbox": "tight", "savefig.pad_inches": 0.01
    })
    mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=palette)

def mm_to_inches(mm): return mm/25.4

FIG_SIZES_MM = {
    "single": (85, 60),
    "one_half": (120, 80),
    "double": (175, 110),
}
