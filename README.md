# BiblioX — Chulalongkorn Bibliometric Intelligence Suite (CBIS)

Publication-grade bibliometric analysis with Scopus/WoS harmonization, 600 DPI figures (Times New Roman), Seaborn/SciencePlots styling, interactive previews (Altair/Plotly), networks (PyVis), maps (Plotly choropleth), Biblioshiny export/launcher, and a persistent Citation Vault (BibTeX/RIS).

## Features
- Scopus-only / WoS-only / Combined modes (auto-detect + de-dup)
- Descriptives: annual counts, top sources/affiliations/countries
- Keywords: frequency bars, co-occurrence network (PyVis HTML)
- Networks: co-authorship (PyVis HTML)
- Maps: choropleth (Plotly) from (Country, Freq) CSV
- Theme Manager + palette extractor from any uploaded image
- Biblioshiny bridge: export CSV + optional rpy2 launcher
- Citation Vault: add/update and export BibTeX/RIS

## Quickstart
```bash
pip install -r requirements.txt
streamlit run app.py
