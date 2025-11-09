"""
plots.py — CBIS / BiblioX Visualization Utilities
-------------------------------------------------
High-quality publication-grade and interactive visualization module
for bibliometric analysis.

Author: Mahbub Hassan
Affiliation: Department of Civil Engineering, Chulalongkorn University
Lab: B'Deshi Emerging Research Lab
"""

import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import plotly.express as px
import pandas as pd
import numpy as np
from pathlib import Path
from themes import mm_to_inches, FIG_SIZES_MM, current_palette

# ============================================================
# 1. GLOBAL METADATA & UTILITIES
# ============================================================
CREDIT = (
    "Bibliometric Intelligence Suite · Developed by Mahbub Hassan · "
    "Department of Civil Engineering, Chulalongkorn University · "
    "Founder, B'Deshi Emerging Research Lab · Educational & training use"
)

def _fig(size_key="single"):
    """Initialize figure with correct size."""
    wmm, hmm = FIG_SIZES_MM[size_key]
    return plt.subplots(figsize=(mm_to_inches(wmm), mm_to_inches(hmm)))

def _stamp(fig):
    """Footer metadata for branding."""
    fig.text(0.99, 0.005, CREDIT, ha="right", va="bottom", fontsize=6, color="#777777")

def _safe_series(series):
    """Ensure non-empty numeric series."""
    if isinstance(series, pd.Series):
        series = series.dropna()
        if len(series) == 0:
            raise ValueError("Empty series — cannot plot.")
        return series
    raise TypeError("Input must be pandas Series.")

# ============================================================
# 2. MATPLOTLIB / SEABORN EXPORTABLE PLOTS
# ============================================================
def barh_series(series, xlabel="Count", ylabel="", size_key="single", color=None):
    """Publication-grade horizontal bar chart."""
    s = _safe_series(series).sort_values(ascending=True)
    fig, ax = _fig(size_key)
    c = color or current_palette(1)[0]
    sns.barplot(x=s.values, y=s.index, ax=ax, color=c, edgecolor="black")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    for spine in ["top", "right"]: ax.spines[spine].set_visible(False)
    ax.tick_params(length=2, width=0.6)
    for i, v in enumerate(s.values):
        ax.text(v + max(s.values)*0.01, i, f"{int(v)}", va="center", fontsize=8)
    _stamp(fig)
    return fig

def line_trend(x, y, xlabel="Year", ylabel="Publications", size_key="single", color=None):
    """Line plot for yearly trends."""
    fig, ax = _fig(size_key)
    c = color or current_palette(1)[0]
    sns.lineplot(x=x, y=y, ax=ax, marker="o", linewidth=1.5, color=c)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    for spine in ["top","right"]: ax.spines[spine].set_visible(False)
    ax.tick_params(length=2, width=0.6)
    _stamp(fig)
    return fig

def dual_axis_line(df, x_col, y1_col, y2_col, y1_label, y2_label, size_key="single"):
    """Dual-axis line plot (e.g., publications vs citations)."""
    fig, ax1 = _fig(size_key)
    color1, color2 = current_palette(2)
    ax1.plot(df[x_col], df[y1_col], marker="o", color=color1, label=y1_label)
    ax1.set_xlabel(x_col); ax1.set_ylabel(y1_label, color=color1)
    ax2 = ax1.twinx()
    ax2.plot(df[x_col], df[y2_col], marker="s", linestyle="--", color=color2, label=y2_label)
    ax2.set_ylabel(y2_label, color=color2)
    _stamp(fig)
    return fig

def save_figure(fig, filename: str | Path, formats=("png","pdf"), dpi=600):
    """Save figure in specified formats."""
    for fmt in formats:
        path = Path(f"{filename}.{fmt}")
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
    print(f"[INFO] Figure saved → {filename}.[{', '.join(formats)}]")

# ============================================================
# 3. ALTAIR INTERACTIVE PREVIEWS
# ============================================================
def altair_bar(df, x, y, title=None):
    """Interactive bar chart for quick preview."""
    chart = (
        alt.Chart(df)
        .mark_bar(color=current_palette(1)[0])
        .encode(
            x=alt.X(x, type="quantitative", title=x),
            y=alt.Y(y, sort='-x', title=y),
            tooltip=[x, y]
        )
        .properties(width=480, height=340, title=title)
        .configure_title(font="Times New Roman", fontSize=12, anchor="start")
        .configure_axis(labelFont="Times New Roman", titleFont="Times New Roman")
    )
    return chart

def altair_line(df, x, y, title=None):
    """Interactive line plot."""
    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X(x, type="quantitative"),
            y=alt.Y(y, type="quantitative"),
            tooltip=[x, y]
        )
        .properties(width=480, height=340, title=title)
    )
    return chart

# ============================================================
# 4. PLOTLY VISUALS (MAPS / CHOROPLETH / NETWORK PREVIEWS)
# ============================================================
def plotly_choropleth(df, country_col="Country", value_col="Freq", scope="world", title=None):
    """Global choropleth for geographical collaboration."""
    fig = px.choropleth(
        df,
        locations=country_col,
        locationmode="country names",
        color=value_col,
        color_continuous_scale="Viridis",
        scope=scope,
        title=title or "Geographical Distribution"
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        title_font=dict(family="Times New Roman", size=16),
        font=dict(family="Times New Roman", size=12),
    )
    return fig

def plotly_bubble(df, x, y, size_col, color_col=None, title=None):
    """Plotly bubble chart for author/year/keyword correlations."""
    fig = px.scatter(
        df,
        x=x, y=y,
        size=size_col,
        color=color_col or size_col,
        color_continuous_scale="Plasma",
        hover_name=color_col or x,
        size_max=40,
        title=title,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        font=dict(family="Times New Roman", size=12),
    )
    return fig

# ============================================================
# 5. QUICK DEMO GENERATOR (optional testing)
# ============================================================
def _demo():
    """Generate sample demonstration plots."""
    years = np.arange(2010, 2025)
    pubs = np.random.randint(10, 200, len(years))
    cits = pubs * np.random.uniform(1.0, 5.0, len(years))
    df = pd.DataFrame({"Year": years, "Publications": pubs, "Citations": cits})
    fig = dual_axis_line(df, "Year", "Publications", "Citations",
                         "Publications", "Citations")
    save_figure(fig, "demo_trend")
    print("✅ Demo figure generated.")

if __name__ == "__main__":
    _demo()
