import streamlit as st, pandas as pd
from styles import register_times, apply_pub_style, CHULA_PALETTE
from harmonize import harmonize_scopus, harmonize_wos, merge_and_dedupe
from plots import barh_series, line_with_markers
from biblioshiny_bridge import export_biblioshiny_ready, try_launch_biblioshiny

st.set_page_config(page_title="Bibliometric Intelligence Suite", page_icon="📚", layout="wide")

# --- Persistent branding (shown in About panel) ---
BRAND = """
### Bibliometric Intelligence Suite  
Developed by **Mahbub Hassan**  
Department of Civil Engineering, Chulalongkorn University  
Founder, [B'Deshi Emerging Research Lab](https://www.bdeshi-lab.org)

⚠️ *Disclaimer:* For educational and research training purposes only.
"""

# --- Style ---
register_times(ttf_path=None)         # add a local TimesNewRoman.ttf if needed
apply_pub_style(palette=CHULA_PALETTE)

# --- Sidebar controls ---
st.sidebar.header("Upload & Mode")
mode = st.sidebar.radio("Analysis Mode", ["Scopus Only", "Web of Science Only", "Combined (Scopus + WoS)"])
files = st.sidebar.file_uploader("Upload CSV/XLSX (Scopus and/or WoS)", type=["csv","xlsx"], accept_multiple_files=True)
size_key = st.sidebar.selectbox("Figure Size", ["single","one_half","double"], index=0)
st.sidebar.caption("All exports are 600 DPI, Times New Roman, tight layout.")

st.title("📚 Bibliometric Intelligence Suite (CBIS)")
st.markdown(BRAND)

# --- Data cache ---
dfs = []
if files:
    for f in files:
        name = f.name.lower()
        try: df = pd.read_csv(f, low_memory=False)
        except Exception: df = pd.read_excel(f)
        cols = set(df.columns)
        if ("Source title" in cols) or ("Cited by" in cols):
            st.success(f"Detected **Scopus**: {f.name} ({len(df)} rows)")
            if mode in ["Scopus Only","Combined (Scopus + WoS)"]:
                dfs.append(harmonize_scopus(df))
        elif ("SO" in cols) or ("PY" in cols) or ("AU" in cols):
            st.success(f"Detected **Web of Science**: {f.name} ({len(df)} rows)")
            if mode in ["Web of Science Only","Combined (Scopus + WoS)"]:
                dfs.append(harmonize_wos(df))
        else:
            st.warning(f"Unknown format: {f.name} — showing head.")
            st.dataframe(df.head())

if dfs:
    if mode.startswith("Combined"):
        merged = merge_and_dedupe(dfs)
    else:
        merged = dfs[0] if len(dfs)==1 else pd.concat(dfs, ignore_index=True)
    st.info(f"Active dataset: **{merged.shape[0]}** records | Mode: **{mode}**")
    st.session_state["merged"] = merged
else:
    st.stop()

# ===== Tabs =====
tab_desc, tab_keywords, tab_maps, tab_biblio, tab_about = st.tabs(
    ["Descriptive", "Keywords", "Maps", "Biblioshiny", "About"]
)

with tab_desc:
    df = st.session_state["merged"]
    col1, col2 = st.columns(2, gap="large")

    # Annual production
    with col1:
        years = pd.to_numeric(df["year"], errors="coerce").dropna().astype(int)
        s = years.value_counts().sort_index()
        fig = line_with_markers(s.index, s.values, xlabel="Year", ylabel="Publications", size_key=size_key)
        st.pyplot(fig)
        if st.button("💾 Save annual_production.png"): fig.savefig("annual_production.png")

    # Top sources
    with col2:
        sources = df["source"].fillna("").value_counts().head(15)
        fig = barh_series(sources, xlabel="N", ylabel="Source", size_key=size_key)
        st.pyplot(fig)
        if st.button("💾 Save top_sources.png"): fig.savefig("top_sources.png")

    col3, col4 = st.columns(2, gap="large")
    with col3:
        # Top affiliations (if available)
        aff = df["affiliations"].fillna("")
        aff_list = []
        for row in aff:
            if not row: continue
            aff_list.extend([a.strip() for a in str(row).split(";") if a.strip()])
        if aff_list:
            s = pd.Series(aff_list).value_counts().head(10)
            fig = barh_series(s, xlabel="N", ylabel="Affiliation", size_key=size_key)
            st.pyplot(fig)
            if st.button("💾 Save affiliations.png"): fig.savefig("affiliations.png")

    with col4:
        # Top countries (prefer countries col)
        base = df["countries"] if "countries" in df.columns else df["affiliations"]
        clist = []
        for row in base.fillna(""):
            clist.extend([c.strip() for c in str(row).split(";") if c.strip()])
        if clist:
            s = pd.Series(clist).value_counts().head(15)
            fig = barh_series(s, xlabel="N", ylabel="Country", size_key=size_key)
            st.pyplot(fig)
            if st.button("💾 Save countries.png"): fig.savefig("countries.png")

with tab_keywords:
    df = st.session_state["merged"]
    field = st.selectbox("Keyword field", ["author_keywords","index_keywords"])
    topk = st.slider("Top K", 10, 50, 30, step=5)
    kv = []
    if field in df.columns:
        for row in df[field]:
            if isinstance(row, list): kv.extend(row)
    s = pd.Series(kv).value_counts().head(topk)
    fig = barh_series(s, xlabel="Count", ylabel="Keyword", size_key=size_key)
    st.pyplot(fig)
    if st.button("💾 Save keywords.png"): fig.savefig("keywords.png")

with tab_maps:
    st.info("For full choropleth/bubble maps with GeoPandas/Cartopy, upload country frequencies as CSV (Country, Freq) in a later step; module included. (Kept light here for GitHub deploy.)")

with tab_biblio:
    df = st.session_state["merged"]
    st.subheader("Biblioshiny Integration")
    st.caption("Export a harmonized CSV for R's Biblioshiny. Optional one-click launcher requires rpy2 + R.")
    c1, c2 = st.columns(2)
    if c1.button("⬇️ Export biblioshiny_ready.csv"):
        export_biblioshiny_ready(df, "biblioshiny_ready.csv")
    if c2.button("▶️ Launch Biblioshiny (if R available)"):
        try_launch_biblioshiny()

with tab_about:
    st.markdown(BRAND)
