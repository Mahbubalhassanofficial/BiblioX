import matplotlib.pyplot as plt
import matplotlib as mpl
from styles import mm_to_inches, FIG_SIZES_MM

def _figure(size_key="single"):
    wmm,hmm = FIG_SIZES_MM[size_key]
    return plt.subplots(figsize=(mm_to_inches(wmm), mm_to_inches(hmm)))

def stamp_credit(fig):
    txt = ("Bibliometric Intelligence Suite · Developed by Mahbub Hassan · "
           "Department of Civil Engineering, Chulalongkorn University · "
           "Founder, B'Deshi Emerging Research Lab · Educational & training use")
    fig.text(0.99, 0.005, txt, ha="right", va="bottom", fontsize=6, color="#777777")

def barh_series(series, xlabel="Count", ylabel="", size_key="single"):
    fig, ax = _figure(size_key)
    s = series.sort_values(ascending=True)
    ax.barh(s.index, s.values, edgecolor="black", linewidth=0.6)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.tick_params(length=2, width=0.6)
    for spine in ["top","right"]: ax.spines[spine].set_visible(False)
    for i, v in enumerate(s.values):
        ax.text(v + max(s.values)*0.01, i, f"{int(v)}", va="center", fontsize=8)
    stamp_credit(fig)
    return fig

def line_with_markers(x, y, xlabel="", ylabel="", size_key="single"):
    fig, ax = _figure(size_key)
    ax.plot(x, y, marker="o", linewidth=1.2, markersize=3.8)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.tick_params(length=2, width=0.6)
    for spine in ["top","right"]: ax.spines[spine].set_visible(False)
    stamp_credit(fig)
    return fig
import seaborn as sns
import matplotlib.pyplot as plt
from styles import mm_to_inches, FIG_SIZES_MM

def line_trend(df, x, y, hue=None, size_key="single"):
    wmm,hmm = FIG_SIZES_MM[size_key]
    fig, ax = plt.subplots(figsize=(mm_to_inches(wmm), mm_to_inches(hmm)))
    sns.lineplot(data=df, x=x, y=y, hue=hue, marker="o", ax=ax, linewidth=1.5)
    for spine in ["top","right"]: ax.spines[spine].set_visible(False)
    ax.set_xlabel(x); ax.set_ylabel(y)
    ax.tick_params(length=2, width=0.6)
    stamp_credit(fig)
    return fig

def bar_rank(df, x, y, size_key="single", orient="h"):
    wmm,hmm = FIG_SIZES_MM[size_key]
    fig, ax = plt.subplots(figsize=(mm_to_inches(wmm), mm_to_inches(hmm)))
    sns.barplot(data=df, x=x, y=y, ax=ax, orient=orient, edgecolor="black")
    for spine in ["top","right"]: ax.spines[spine].set_visible(False)
    stamp_credit(fig)
    return fig
