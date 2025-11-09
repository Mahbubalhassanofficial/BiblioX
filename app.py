import streamlit as st
import pandas as pd

from themes import register_times, apply_pub_style, PALETTES
from harmonize import harmonize_scopus, harmonize_wos, merge_and_dedupe
from analysis import annual_counts, top_sources, top_affiliations, top_countries, keyword_series
from plots import barh_series, line_trend, altair_bar, plotly_choropleth
from network import coauthorship_graph, keyword_cooccurrence_graph, export_pyvis_html
from citations import upsert, export_bib, export_ris, load_vault
from palette_from_image import extract_palette
from utils_io import read_any_table

st.set_page_config(page_title="BiblioX — CBIS", page_icon="📚", layout="wide")

# ---- Branding (bibliometric suite only) ----
BRAND = """
### Bibliometric Intelligence Suite  
Developed by **Mahbub Hassan**  
Department of Civil Engineering, Chulalongkorn University  
Founder, [B'Deshi Emerging Research Lab](https://www.bdeshi-lab.org)

⚠️ *Disclaimer:* For educational and research training purposes only.
"""

st.title("📚 BiblioX — Chulalongkorn Bibliometric Intelligence Suite (CBIS)")
st.markdown(BRAND)

# ---- Sidebar: Theme & Mode ----
st.sidebar.header("Settings")
palette_name = st.sidebar.selectbox("Color theme", list(PALETTES.keys()), index=0)
analysis_mode = st.sidebar.radio("Analysis Mode", ["Scopus Only", "Web of Science Only", "Combined (Scopus + WoS)"], index=2)
size_key = st.sidebar.selectbox("Figure Size", ["single","one_half","double"], index=0)

with st.sidebar.expander("Theme from image (palette extractor)"):
    img = st.file_uploader("Upload figure/image", type=["png","jpg","jpeg"], key="palimg")
    k = st.slider("Palette size (k)", 3, 8, 6)
    if img and st.button("Extract palette"):
        pal = extract_palette(img, k=k)
        st.write("Extracted:", pal)
        PALETTES["Extracted"] = pal
        palette_name = "Extracted"

register_times(ttf_path=None)
apply_pub_style(palette=PALETTES[palette_name])

# ---- Upload & Harmonize ----
st.header("1) Upload & Harmonize")
files = st.file_uploader("Upload Scopus and/or WoS CSV/XLSX", type=["csv","xlsx"], accept_multiple_files=True)
dfs = []
if files:
    for f in files:
        df_raw = read_any_table(f)
        cols = set(df_raw.columns)
        if ("Source title" in cols) or ("Cited by" in cols):
            st.success(f"Detected **Scopus**: {f.name} ({len(df_raw)} rows)")
            if analysis_mode in ["Scopus Only","Combined (Scopus + WoS)"]:
                dfs.append(harmonize_scopus(df_raw))
        elif ("SO" in cols) or ("PY" in cols) or ("AU" in cols):
            st.success(f"Detected **WoS**: {f.name} ({len(df_raw)} rows)")
            if analysis_mode in ["Web of Science Only","Combined (Scopus + WoS)"]:
                dfs.append(harmonize_wos(df_raw))
        else:
            st.warning(f"Unknown format: {f.name}")
            st.dataframe(df_raw.head())

if not dfs:
    st.stop()

if analysis_mode.startswith("Combined"):
    merged = merge_and_dedupe(dfs)
else:
    merged = dfs[0] if len(dfs)==1 else pd.concat(dfs, ignore_index=True)

st.info(f"Active dataset: **{merged.shape[0]}** records | Mode: **{analysis_mode}**")
st.dataframe(merged.head(10), use_container_width=True)
st.session_state["merged"] = merged

# ---- Tabs ----
tab_desc, tab_keywords, tab_networks, tab_maps, tab_biblio, tab_refs, tab_theme, tab_about = st.tabs(
    ["Descriptives", "Keywords", "Networks", "Maps", "Biblioshiny", "Citation Vault", "Theme Manager", "About"]
)

# 2) Descriptives
with tab_desc:
    df = st.session_state["merged"]
    c1, c2 = st.columns(2)
    with c1:
        s = annual_counts(df)
        fig = line_trend(s.index, s.values, xlabel="Year", ylabel="Publications", size_key=size_key)
        st.pyplot(fig)
        if st.button("💾 Save annual_publications.png"): fig.savefig("annual_publications.png")

    with c2:
        topS = top_sources(df, k=15)
        fig = barh_series(topS, xlabel="N", ylabel="Source (Journal/Proceedings)", size_key=size_key)
        st.pyplot(fig)
        if st.button("💾 Save top_sources.png"): fig.savefig("top_sources.png")

    c3, c4 = st.columns(2)
    with c3:
        ta = top_affiliations(df, k=15)
        fig = barh_series(ta, xlabel="N", ylabel="Affiliation", size_key=size_key)
        st.pyplot(fig)
        if st.button("💾 Save affiliations.png"): fig.savefig("affiliations.png")

    with c4:
        tc = top_countries(df, k=15)
        fig = barh_series(tc, xlabel="N", ylabel="Country", size_key=size_key)
        st.pyplot(fig)
        if st.button("💾 Save countries.png"): fig.savefig("countries.png")

    st.divider()
    st.caption("Interactive preview (Altair):")
    st.altair_chart(altair_bar(topS.reset_index().rename(columns={"index":"Source", "source":"Source", 0:"Count", "source":"Source", topS.name:"Count"}), "Count", "Source"), use_container_width=True)

# 3) Keywords
with tab_keywords:
    df = st.session_state["merged"]
    field = st.selectbox("Keyword field", ["author_keywords","index_keywords"])
    topk = st.slider("Top K", 10, 50, 30, step=5)
    ks = keyword_series(df, field=field, k=topk)
    fig = barh_series(ks, xlabel="Count", ylabel="Keyword", size_key=size_key)
    st.pyplot(fig)
    if st.button("💾 Save keywords.png"): fig.savefig(f"keywords_{field}.png")

# 4) Networks
with tab_networks:
    df = st.session_state["merged"]
    st.subheader("Co-authorship network")
    min_deg = st.slider("Min degree (prune)", 1, 6, 2)
    if st.button("Build & Export (PyVis HTML)"):
        G = coauthorship_graph(df, min_freq=min_deg)
        path = export_pyvis_html(G, path="coauthorship_network.html")
        st.success(f"Saved: {path}")

    st.subheader("Keyword co-occurrence")
    field = st.selectbox("Co-occurrence field", ["author_keywords","index_keywords"])
    minf = st.slider("Min keyword frequency", 2, 10, 3, key="kwmin")
    if st.button("Build & Export keyword network"):
        G, _ = keyword_cooccurrence_graph(df, field=field, min_freq=minf)
        path = export_pyvis_html(G, path="keyword_cooccurrence.html")
        st.success(f"Saved: {path}")

# 5) Maps (Plotly choropleth)
with tab_maps:
    st.caption("Upload a (Country, Freq) table to render a global choropleth (Plotly).")
    mapfile = st.file_uploader("Upload country-frequency CSV", type=["csv"], key="mapcsv")
    if mapfile:
        mdf = pd.read_csv(mapfile)
        if {"Country","Freq"}.issubset(mdf.columns):
            fig = plotly_choropleth(mdf, "Country", "Freq", scope="world")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("CSV must have columns: Country, Freq")

# 6) Biblioshiny
with tab_biblio:
    st.subheader("Biblioshiny Integration (R)")
    colx, coly = st.columns(2)
    if colx.button("⬇️ Export biblioshiny_ready.csv"):
        st.session_state["merged"].to_csv("biblioshiny_ready.csv", index=False)
        st.success("Saved biblioshiny_ready.csv")
    if coly.button("▶️ Launch Biblioshiny (requires R + rpy2)"):
        try:
            from rpy2.robjects import r
            r('library(bibliometrix)'); r('biblioshiny()')
            st.info("Biblioshiny started at http://127.0.0.1:3838")
        except Exception as e:
            st.warning("Could not launch Biblioshiny. Ensure R + bibliometrix + rpy2 are installed.")
            st.exception(e)

# 7) Citation Vault
with tab_refs:
    st.subheader("Citation Vault (BibTeX / RIS)")
    vault = load_vault()
    st.write(f"Stored entries: **{len(vault)}**")
    with st.form("addref"):
        key = st.text_input("Key (e.g., Zupic2015)")
        entry_type = st.selectbox("Type", ["article","inproceedings","book","misc"])
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

# 8) Theme Manager (preview)
with tab_theme:
    st.subheader("Theme Manager")
    st.write("Active palette:", palette_name, PALETTES[palette_name])
    st.caption("Tip: use the image extractor in the sidebar to clone colors from an existing figure.")

# 9) About
with tab_about:
    st.markdown(BRAND)
