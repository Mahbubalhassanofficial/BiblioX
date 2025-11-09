"""
biblioshiny_utils.py — CBIS / BiblioX R–Python Bridge
-----------------------------------------------------
Handles Biblioshiny (bibliometrix) export and local launch
from within the Streamlit-based BiblioX interface.

Author: Mahbub Hassan
Affiliation: Department of Civil Engineering, Chulalongkorn University
Lab: B'Deshi Emerging Research Lab
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import subprocess
import sys

# ============================================================
# 1. EXPORT TO BIBLIOSHINY
# ============================================================
def export_biblioshiny_ready(df: pd.DataFrame, path: str = "vault/biblioshiny_ready.csv") -> None:
    """Save harmonized dataset in a clean CSV for R–Biblioshiny import."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    st.success(f"✅ Exported for Biblioshiny: `{path}`")

# ============================================================
# 2. LAUNCH BIBLIOSHINY (LOCAL ONLY)
# ============================================================
def try_launch_biblioshiny() -> None:
    """
    Attempt to launch R's Biblioshiny app.
    Works only on local environments with R ≥4.3, bibliometrix, and rpy2 or Rscript available.
    """
    st.info("Attempting to launch Biblioshiny...")

    try:
        # --- Preferred: via rpy2 bridge ---
        from rpy2.robjects import r
        r('suppressMessages(library(bibliometrix))')
        r('biblioshiny()')
        st.success("📊 Biblioshiny started — open your browser at http://127.0.0.1:3838")
        return
    except Exception as e1:
        st.warning("⚠️ rpy2 bridge not available — trying Rscript fallback.")
        try:
            subprocess.Popen(["Rscript", "-e", "library(bibliometrix); biblioshiny()"])
            st.success("📊 Biblioshiny started — open http://127.0.0.1:3838")
            return
        except Exception as e2:
            st.error("❌ Could not launch Biblioshiny.")
            st.markdown("""
            **Check the following:**
            1. R ≥ 4.3 installed  
            2. Packages `bibliometrix`, `shiny` installed (`install.packages('bibliometrix')`)  
            3. rpy2 installed in Python environment (`pip install rpy2`)  
            """)
            st.exception(e1)
            st.exception(e2)

# ============================================================
# 3. SAFE FALLBACK MESSAGE (for Streamlit Cloud)
# ============================================================
def biblioshiny_cloud_notice():
    """Display note for users running on Streamlit Cloud."""
    st.warning(
        "Biblioshiny cannot be launched directly from Streamlit Cloud. "
        "You can download `biblioshiny_ready.csv` and open it locally in R:\n\n"
        "```R\n"
        "library(bibliometrix)\n"
        "biblioshiny()\n"
        "```"
    )

# ============================================================
# 4. DEMO (for testing)
# ============================================================
if __name__ == "__main__":
    st.write("Run `try_launch_biblioshiny()` locally after exporting your dataset.")
