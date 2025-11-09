"""
app.py — BiblioX / CBIS
--------------------------------------------------------------
Comprehensive bibliometric intelligence suite built in Streamlit,
integrating Scopus + WoS harmonization, analytics, visualization,
networks, and R–Biblioshiny interoperability.

Author: Mahbub Hassan
Affiliation: Department of Civil Engineering, Chulalongkorn University
Lab: B'Deshi Emerging Research Lab
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from io import BytesIO
import base64

# --- Local imports ---
from themes import register_times, apply_pub_style, PALETTES
from harmonize import harmonize_scopus, harmonize_wos, merge_and_dedupe
from analysis import annual_counts, top_sources, top_affiliations, top_countries, keyword_series
from plots import barh_series, line_trend, altair_bar, plotly_choropleth
from network import coauthorship_graph, keyword_cooccurrence_graph, export_pyvis_html
from citations import upsert, export_bib, export_ris, load_vault
from palette_from_image import extract_palette
from utils_io import read_any_table, summarize_dataset
from biblioshiny_utils import export_biblioshiny_ready, try_launch_biblioshiny, biblioshiny_cloud_notice

# ============================================================
# 1. PAGE CONFIG
# ============================================================
st.set_page_config(page_title="BiblioX — CBIS", page_icon="📚", layout="wide")

# Ensure folders exist
for folder in ["vault", "outputs"]:
    Path(folder).mkdir(exist_ok=True)

# Branding header
BRAND = """
### Bibliometric Intelligence Suite (BiblioX / CBIS)  
Developed by **Mahbub Hassan**  
Department of Civil Engineering, Chulalongkorn University  
Founder, [B'Deshi Emerging Research Lab](https://www.bdeshi-lab.org)

⚠️ *For educational and research training purposes only.*
"""
st.title("📚 BiblioX — Chulalongkorn Bibliometric Intelligence Suite (CBIS)")
st.markdown(BRAND)

# ============================================================
# 2. SIDEBAR SETTINGS
# ============================================================
st.sidebar.header("⚙️ Settings")

palette_name = st.sidebar.selectbox("🎨 Color Theme", list(PALETTES.keys()), index=0)
dark_mode = st.sidebar.checkbox("🌙 Dark mode preview", value=False)
analysis_mode = st.sidebar.radio("Analysis Mode", ["Scopus Only", "Web of Science Only", "Combined (Scopus + WoS)"], index=2)
size_key = st.sidebar.selectbox("Figure Size", ["single", "one_half", "double"], index=0)

with st.sidebar.expander("🖼️ Theme from Image (Palette Extractor)"):
    img = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"], key="palimg")
    k = st.slider("Palette size (k)", 3, 8, 6)
    if img and st.button("Extract palette"):
        pal = extract_palette(img, k=k)
        st.write("Extracted:", pal)
        PALETTES["Extracted"] = pal
        palette_name = "Extracted"

register_times()
apply_pub_style(palette=PALETTES[palette_name], dark_mode=dark_mode)

# ============================================================
# 3. FILE UPLOAD & HARMONIZATION
# ============================================================
st.header("1️⃣ Upload & Harmonize Datasets")

@st.cache_data
def cached_read(file):
    return read_any_table(file)

files = st.file_uploader("Upload Scopus and/or WoS CSV/XLSX", type=["csv", "xlsx"], accept_multiple_files=True)
dfs = []

if files:
    for f in files:
        df_raw = cached_read(f)["df"]
        cols = set(df_raw.columns)

        # --- Detect Scopus ---
        if ("Source title" in cols) or ("Cited by" in cols):
            st.success(f"Detected **Scopus**: {f.name} ({len(df_raw)} records)")
            if analysis_mode in ["Scopus Only", "Combined (Scopus + WoS)"]:
                dfs.append(harmonize_scopus(df_raw))

        # --- Detect Web of Science ---
        elif ("SO" in cols) or ("PY" in cols) or ("AU" in cols):
            st.success(f"Detected **Web of Science (WoS)**: {f.name} ({len(df_raw)} records)")
            if analysis_mode in ["Web of Science Only", "Combined (Scopus + WoS)"]:
                dfs.append(harmonize_wos(df_raw))

        # --- Detect Harmonized Bibliometric Data (your custom format) ---
        elif {"title", "year", "authors"}.issubset(cols):
            st.success(f"Detected **Harmonized Bibliometric File**: {f.name} ({len(df_raw)} records)")
            dfs.append(df_raw)

        # --- Unknown format fallback ---
        else:
            st.warning(f"⚠️ Unknown format: {f.name}")
            st.caption("Preview of columns for debugging:")
            st.dataframe(df_raw.head())

if not dfs:
    st.stop()


merged = merge_and_dedupe(dfs) if analysis_mode.startswith("Combined") else (dfs[0] if len(dfs) == 1 else pd.concat(dfs))
st.session_state["merged"] = merged

summary = summarize_dataset(merged)
st.info(
    f"Active dataset: **{summary['records']} records**, "
    f"Years: **{summary['year_range']}**, "
    f"Countries: **{summary['countries']}**, "
    f"Sources: **{summary['sources']}**"
)
st.dataframe(merged.head(10), use_container_width=True)

# ============================================================
# 4. HELPER FUNCTION — DOWNLOAD FIGURE
# ============================================================
def download_fig(fig, filename="figure.png"):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=600, bbox_inches="tight")
    b64 = base64.b64encode(buf.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{b64}" download="{filename}">📥 Download {filename}</a>'
    st.markdown(href, unsafe_allow_html=True)

# ============================================================
# 5. MAIN TABS
# ============================================================
tabs = st.tabs([
    "Descriptives", "Keywords", "Networks", "Maps",
    "Biblioshiny", "Citation Vault", "Theme Manager", "About"
])

# ------------------------------------------------------------
# TAB 1 — DESCRIPTIVES
# ------------------------------------------------------------
with tabs[0]:
    df = st.session_state["merged"]
    c1, c2 = st.columns(2)
    with c1:
        s = annual_counts(df)
        fig = line_trend(s.index, s.values, xlabel="Year", ylabel="Publications", size_key=size_key)
        st.pyplot(fig)
        download_fig(fig, "annual_publications.png")

    with c2:
        topS = top_sources(df, k=15)
        fig = barh_series(topS, xlabel="Count", ylabel="Source (Journal/Conference)", size_key=size_key)
        st.pyplot(fig)
        download_fig(fig, "top_sources.png")

    c3, c4 = st.columns(2)
    with c3:
        ta = top_affiliations(df, k=15)
        fig = barh_series(ta, xlabel="Count", ylabel="Affiliation", size_key=size_key)
        st.pyplot(fig)
        download_fig(fig, "top_affiliations.png")

    with c4:
        tc = top_countries(df, k=15)
        fig = barh_series(tc, xlabel="Count", ylabel="Country", size_key=size_key)
        st.pyplot(fig)
        download_fig(fig, "top_countries.png")

    st.divider()
    st.caption("Interactive (Altair):")

    # --- Safe preparation of top sources data ---
    df_topS = topS.reset_index()
    df_topS.columns = ["Source", "Count"]

    # --- Generate Altair chart safely ---
    chart = altair_bar(
        df_topS,
        x="Count",
        y="Source",
        title="Top Sources (Journals / Proceedings)"
    )

    # --- Display in Streamlit ---
    st.altair_chart(chart, use_container_width=True)

# ------------------------------------------------------------
# TAB 2 — KEYWORDS
# ------------------------------------------------------------
with tabs[1]:
    df = st.session_state["merged"]
    field = st.selectbox("Keyword Field", ["author_keywords", "index_keywords"])
    topk = st.slider("Top K", 10, 50, 30)
    ks = keyword_series(df, field=field, k=topk)
    fig = barh_series(ks, xlabel="Count", ylabel="Keyword", size_key=size_key)
    st.pyplot(fig)
    download_fig(fig, f"keywords_{field}.png")

# ------------------------------------------------------------
# TAB 3 — NETWORKS
# ------------------------------------------------------------
with tabs[2]:
    df = st.session_state["merged"]
    st.subheader("👥 Co-authorship Network")
    min_deg = st.slider("Min Degree (Prune)", 1, 6, 2)
    if st.button("Build & Export Co-authorship Network (PyVis)"):
        G = coauthorship_graph(df, min_freq=min_deg)
        path = export_pyvis_html(G, path="outputs/coauthorship_network.html")
        st.success(f"Saved → {path}")

    st.subheader("🔗 Keyword Co-occurrence Network")
    field = st.selectbox("Co-occurrence Field", ["author_keywords", "index_keywords"])
    minf = st.slider("Min Keyword Frequency", 2, 10, 3)
    if st.button("Build & Export Keyword Network"):
        G, _ = keyword_cooccurrence_graph(df, field=field, min_freq=minf)
        path = export_pyvis_html(G, path="outputs/keyword_cooccurrence.html")
        st.success(f"Saved → {path}")

# ------------------------------------------------------------
# TAB 4 — MAPS
# ------------------------------------------------------------
with tabs[3]:
    st.caption("Upload a (Country, Freq) CSV to render a global choropleth (Plotly).")
    mapfile = st.file_uploader("Upload country-frequency CSV", type=["csv"], key="mapcsv")
    if mapfile:
        mdf = pd.read_csv(mapfile)
        if {"Country", "Freq"}.issubset(mdf.columns):
            fig = plotly_choropleth(mdf, "Country", "Freq", scope="world")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("CSV must have columns: Country, Freq")

# ------------------------------------------------------------
# TAB 5 — BIBLIOSHINY
# ------------------------------------------------------------
with tabs[4]:
    st.subheader("📊 Biblioshiny Integration (R–Bibliometrix)")
    c1, c2 = st.columns(2)
    if c1.button("⬇️ Export biblioshiny_ready.csv"):
        export_biblioshiny_ready(st.session_state["merged"])
    if c2.button("▶️ Launch Biblioshiny (local only)"):
        if "streamlit" in st.runtime.scriptrunner.script_run_context.get_script_run_ctx().__dict__:
            biblioshiny_cloud_notice()
        else:
            try_launch_biblioshiny()

# ------------------------------------------------------------
# TAB 6 — CITATION VAULT
# ------------------------------------------------------------
with tabs[5]:
    st.subheader("Citation Vault (BibTeX / RIS)")
    vault = load_vault()
    st.write(f"Stored entries: **{len(vault)}**")

    with st.form("addref"):
        key = st.text_input("Key (e.g., Zupic2015)")
        entry_type = st.selectbox("Type", ["article", "inproceedings", "book", "misc"])
        title = st.text_input("Title")
        journal = st.text_input("Journal/Booktitle")
        year = st.text_input("Year")
        doi = st.text_input("DOI")
        authors = st.text_area("Authors (one per line: 'Last, First')")
        submitted = st.form_submit_button("Add / Update")
        if submitted and key:
            fields = {"title": title}
            if journal: fields["journal"] = journal
            if year: fields["year"] = year
            if doi: fields["doi"] = doi
            persons = {"author": [a.strip() for a in authors.strip().split("\n") if a.strip()]} if authors.strip() else {}
            upsert(key, entry_type, fields, persons)
            st.success(f"Saved/updated {key}")

    c1, c2 = st.columns(2)
    if c1.button("Export BibTeX"):
        export_bib("vault/citations.bib")
        st.success("Exported → vault/citations.bib")
    if c2.button("Export RIS"):
        export_ris("vault/citations.ris")
        st.success("Exported → vault/citations.ris")

# ------------------------------------------------------------
# TAB 7 — THEME MANAGER
# ------------------------------------------------------------
with tabs[6]:
    st.subheader("Theme Manager")
    st.write("Active Palette:", palette_name, PALETTES[palette_name])
    st.caption("Tip: Use the sidebar image extractor to generate a palette from an existing figure.")

# ------------------------------------------------------------
# TAB 8 — ABOUT
# ------------------------------------------------------------
with tabs[7]:
    st.markdown(BRAND)
    st.info("Version: 1.0 — Optimized for academic bibliometric research and visualization.")
