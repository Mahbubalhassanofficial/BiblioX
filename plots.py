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
    """Ensure non-empty numeric series; return empty placeholder instead of raising."""
    if not isinstance(series, pd.Series):
        return pd.Series(dtype=float)
    series = series.dropna()
    if series.empty:
        return pd.Series(dtype=float)
    return series


# ============================================================
# 2. MATPLOTLIB / SEABORN EXPORTABLE PLOTS
# ============================================================
def barh_series(series, xlabel="Count", ylabel="", size_key="single", color=None):
    """Safe horizontal bar plot that handles missing/empty data gracefully."""
    s = _safe_series(series)
    if s.empty:
        fig, ax = _fig(size_key)
        ax.text(
            0.5, 0.5, "⚠️ No valid data available for this chart",
            ha="center", va="center", fontsize=9
        )
        ax.axis("off")
        _stamp(fig)
        return fig

    s = s.sort_values(ascending=True)
    fig, ax = _fig(size_key)
    c = color or current_palette(1)[0]
    sns.barplot(x=s.values, y=s.index, ax=ax, color=c, edgecolor="black")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.tick_params(length=2, width=0.6)
    for i, v in enumerate(s.values):
        ax.text(v + max(s.values) * 0.01, i, f"{int(v)}", va="center", fontsize=8)
    _stamp(fig)
    return fig


def line_trend(x, y, xlabel="Year", ylabel="Publications", size_key="single", color=None):
    """Final robust publication trend line chart (safe for Streamlit Cloud)."""
    x = np.array(x).flatten()
    y = np.array(y).flatten()

    if len(x) == 0 or len(y) == 0:
        fig, ax = _fig(size_key)
        ax.text(0.5, 0.5, "⚠️ No valid data for line chart", ha="center", va="center", fontsize=9)
        ax.axis("off")
        return fig

    # Convert to numeric
    x = pd.to_numeric(x, errors="coerce")
    y = pd.to_numeric(y, errors="coerce")
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if len(x) == 0:
        fig, ax = _fig(size_key)
        ax.text(0.5, 0.5, "⚠️ No numeric values available", ha="center", va="center", fontsize=9)
        ax.axis("off")
        return fig

    try:
        order = np.argsort(x)
        x, y = x[order], y[order]
    except Exception:
        pass

    fig, ax = _fig(size_key)
    c = color or current_palette(1)[0]
    sns.lineplot(x=x, y=y, ax=ax, marker="o", linewidth=1.6, color=c)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.tick_params(length=2, width=0.6)
    _stamp(fig)
    return fig


def dual_axis_line(df, x_col, y1_col, y2_col, y1_label, y2_label, size_key="single"):
    """Dual-axis line plot (e.g., publications vs citations)."""
    fig, ax1 = _fig(size_key)
    color1, color2 = current_palette(2)
    ax1.plot(df[x_col], df[y1_col], marker="o", color=color1, label=y1_label)
    ax1.set_xlabel(x_col)
    ax1.set_ylabel(y1_label, color=color1)
    ax2 = ax1.twinx()
    ax2.plot(df[x_col], df[y2_col], marker="s", linestyle="--", color=color2, label=y2_label)
    ax2.set_ylabel(y2_label, color=color2)
    _stamp(fig)
    return fig


def save_figure(fig, filename: str | Path, formats=("png", "pdf"), dpi=600):
    """Save figure in specified formats."""
    for fmt in formats:
        path = Path(f"{filename}.{fmt}")
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
    print(f"[INFO] Figure saved → {filename}.[{', '.join(formats)}]")


# ============================================================
# 3. ALTAIR INTERACTIVE PREVIEWS
# ============================================================
def altair_bar(df, x, y, title="Top Sources (Interactive Preview)"):
    """Interactive Altair bar chart (Streamlit-safe, schema-compliant)."""
    import matplotlib.pyplot as plt

    if df is None or df.empty:
        fig, ax = plt.subplots(figsize=(5, 2))
        ax.text(0.5, 0.5, "⚠️ No data for Altair chart", ha="center", va="center", fontsize=10)
        ax.axis("off")
        return fig

    df = df.copy()
    df.columns = [str(c) for c in df.columns]

    if x not in df.columns or y not in df.columns:
        fig, ax = plt.subplots(figsize=(5, 2))
        ax.text(0.5, 0.5, f"⚠️ Columns '{x}' or '{y}' missing", ha="center", va="center", fontsize=9)
        ax.axis("off")
        return fig

    df[x] = pd.to_numeric(df[x], errors="coerce")
    df[y] = df[y].astype(str)
    df = df.dropna(subset=[x])
    if df.empty:
        fig, ax = plt.subplots(figsize=(5, 2))
        ax.text(0.5, 0.5, "⚠️ No valid numeric data", ha="center", va="center", fontsize=9)
        ax.axis("off")
        return fig

    chart = (
        alt.Chart(df)
        .mark_bar(color=current_palette(1)[0])
        .encode(
            x=alt.X(x, type="quantitative", title=x),
            y=alt.Y(y, sort='-x', title=y),
            tooltip=[x, y]
        )
        .properties(width=480, height=340, title=(title or ""))
        .configure_title(font="Times New Roman", fontSize=12, anchor="start")
        .configure_axis(labelFont="Times New Roman", titleFont="Times New Roman")
    )
    return chart


def altair_line(df, x, y, title="Trend (Interactive Preview)"):
    """Safe Altair line plot (handles missing data gracefully)."""
    import matplotlib.pyplot as plt

    if df is None or df.empty:
        fig, ax = plt.subplots(figsize=(5, 2))
        ax.text(0.5, 0.5, "⚠️ No data for Altair line chart", ha="center", va="center", fontsize=10)
        ax.axis("off")
        return fig

    df = df.copy()
    df.columns = [str(c) for c in df.columns]
    if x not in df.columns or y not in df.columns:
        fig, ax = plt.subplots(figsize=(5, 2))
        ax.text(0.5, 0.5, f"⚠️ Missing '{x}' or '{y}'", ha="center", va="center", fontsize=9)
        ax.axis("off")
        return fig

    df[x] = pd.to_numeric(df[x], errors="coerce")
    df[y] = pd.to_numeric(df[y], errors="coerce")
    df = df.dropna(subset=[x, y])
    if df.empty:
        fig, ax = plt.subplots(figsize=(5, 2))
        ax.text(0.5, 0.5, "⚠️ No valid numeric data", ha="center", va="center", fontsize=9)
        ax.axis("off")
        return fig

    chart = (
        alt.Chart(df)
        .mark_line(point=True, color=current_palette(1)[0])
        .encode(
            x=alt.X(x, type="quantitative", title=x),
            y=alt.Y(y, type="quantitative", title=y),
            tooltip=[x, y]
        )
        .properties(width=480, height=340, title=(title or ""))
        .configure_title(font="Times New Roman", fontSize=12, anchor="start")
        .configure_axis(labelFont="Times New Roman", titleFont="Times New Roman")
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
        x=x,
        y=y,
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
