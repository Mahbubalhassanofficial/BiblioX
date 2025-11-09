import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import plotly.express as px
from themes import mm_to_inches, FIG_SIZES_MM

CREDIT = ("Bibliometric Intelligence Suite · Developed by Mahbub Hassan · "
          "Department of Civil Engineering, Chulalongkorn University · "
          "Founder, B'Deshi Emerging Research Lab · Educational & training use")

def _fig(size_key="single"):
    wmm,hmm = FIG_SIZES_MM[size_key]
    return plt.subplots(figsize=(mm_to_inches(wmm), mm_to_inches(hmm)))

def _stamp(fig):
    fig.text(0.99, 0.005, CREDIT, ha="right", va="bottom", fontsize=6, color="#777777")

# ---------- Matplotlib / Seaborn (final exports) ----------

def barh_series(series, xlabel="Count", ylabel="", size_key="single"):
    fig, ax = _fig(size_key)
    s = series.sort_values(ascending=True)
    sns.barplot(x=s.values, y=s.index, ax=ax, edgecolor="black")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    for spine in ["top","right"]: ax.spines[spine].set_visible(False)
    ax.tick_params(length=2, width=0.6)
    for i, v in enumerate(s.values):
        ax.text(v + max(s.values)*0.01, i, f"{int(v)}", va="center", fontsize=8)
    _stamp(fig)
    return fig

def line_trend(x, y, xlabel="Year", ylabel="Publications", size_key="single"):
    fig, ax = _fig(size_key)
    sns.lineplot(x=x, y=y, ax=ax, marker="o", linewidth=1.5)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    for spine in ["top","right"]: ax.spines[spine].set_visible(False)
    ax.tick_params(length=2, width=0.6)
    _stamp(fig)
    return fig

# ---------- Altair preview (interactive, optional) ----------

def altair_bar(df, x, y):
    return (alt.Chart(df).mark_bar().encode(
        x=alt.X(x, type="quantitative"), y=alt.Y(y, sort='-x')
    ).properties(width=450, height=320))

# ---------- Plotly (maps & quick previews) ----------

def plotly_choropleth(df, country_col="Country", value_col="Freq", scope="world"):
    fig = px.choropleth(
        df, locations=country_col, locationmode="country names",
        color=value_col, color_continuous_scale="Viridis", scope=scope
    )
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0))
    return fig
