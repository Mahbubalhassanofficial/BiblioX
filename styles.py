import matplotlib as mpl
import seaborn as sns
from matplotlib import font_manager

CHULA_PALETTE = ["#E4007C", "#4B2E83", "#A7C947", "#707070", "#008CBA"]

def register_times(ttf_path=None):
    if ttf_path:
        try:
            font_manager.fontManager.addfont(ttf_path)
        except Exception:
            pass

def apply_pub_style(palette=CHULA_PALETTE, theme="science"):
    # SciencePlots theme (for Nature/IEEE style)
    try:
        mpl.style.use([theme, "no-latex"])
    except Exception:
        pass
    sns.set_theme(style="whitegrid", palette=palette)
    mpl.rcParams.update({
        "font.family": "Times New Roman",
        "font.size": 9,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "axes.linewidth": 0.8,
        "xtick.major.size": 2,
        "ytick.major.size": 2,
        "savefig.dpi": 600,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.01,
    })
