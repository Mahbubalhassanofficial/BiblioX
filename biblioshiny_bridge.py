import streamlit as st
import pandas as pd

def export_biblioshiny_ready(df: pd.DataFrame, path="biblioshiny_ready.csv"):
    df.to_csv(path, index=False)
    st.success(f"Exported for Biblioshiny: {path}")

def try_launch_biblioshiny():
    try:
        from rpy2.robjects import r
        r('library(bibliometrix)')
        r('biblioshiny()')
        st.info("Biblioshiny started (check your browser/tab at http://127.0.0.1:3838).")
    except Exception as e:
        st.warning(
            "Could not launch Biblioshiny from Python. "
            "Ensure R ≥4.3, bibliometrix installed, and rpy2 configured."
        )
        st.exception(e)
