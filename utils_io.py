"""
utils_io.py — CBIS / BiblioX File Loader
----------------------------------------
Robust input handler for bibliometric datasets from Scopus and Web of Science.
Handles CSV/XLSX/TSV formats, detects encoding, harmonizes structure,
and returns ready-to-analyze DataFrames.

Author: Mahbub Hassan
Affiliation: Department of Civil Engineering, Chulalongkorn University
Lab: B'Deshi Emerging Research Lab
"""

from __future__ import annotations
import io, zipfile
import pandas as pd
import chardet
from pathlib import Path
from typing import Dict, Any
from harmonize import harmonize_scopus, harmonize_wos

# ============================================================
# 1. FILE READING WITH ENCODING DETECTION
# ============================================================
def _read_csv_safe(file_obj, nrows: int = None) -> pd.DataFrame:
    """Read CSV with automatic encoding detection and fallback."""
    raw = file_obj.read()
    enc = chardet.detect(raw[:50000]).get("encoding", "utf-8")
    try:
        return pd.read_csv(io.BytesIO(raw), encoding=enc, nrows=nrows, low_memory=False)
    except Exception:
        return pd.read_csv(io.BytesIO(raw), encoding="latin-1", nrows=nrows, low_memory=False)

# ============================================================
# 2. SOURCE DETECTION
# ============================================================
def detect_source(df: pd.DataFrame) -> str:
    """Identify whether dataset originates from Scopus or Web of Science."""
    scopus_keys = {"Authors", "Source title", "Author(s) ID", "Affiliations"}
    wos_keys = {"AU", "TI", "SO", "C1", "DI"}
    cols = set(df.columns)
    if cols & scopus_keys:
        return "Scopus"
    elif cols & wos_keys:
        return "Web of Science"
    return "Unknown"

# ============================================================
# 3. MAIN LOADER
# ============================================================
def read_any_table(uploaded_file) -> Dict[str, Any]:
    """
    Read and harmonize bibliometric data.
    Supports CSV/XLSX/TSV/ZIP (Scopus or Web of Science exports).

    Returns dict:
        {
          'df': <pandas.DataFrame>,
          'source': 'Scopus'|'WoS'|'Unknown',
          'records': int,
          'columns': list[str]
        }
    """
    name = uploaded_file.name.lower()
    df = None

    # --- Handle compressed ZIP archives (common from WoS) ---
    if name.endswith(".zip"):
        with zipfile.ZipFile(uploaded_file) as zf:
            for member in zf.namelist():
                if member.lower().endswith((".csv", ".txt")):
                    with zf.open(member) as f:
                        df = _read_csv_safe(f)
                        break
    elif name.endswith(".csv") or name.endswith(".txt"):
        df = _read_csv_safe(uploaded_file)
    elif name.endswith(".xlsx") or name.endswith(".xls"):
        df = pd.read_excel(uploaded_file)
    elif name.endswith(".tsv"):
        df = pd.read_csv(uploaded_file, sep="\t", low_memory=False)
    else:
        raise ValueError(f"Unsupported file type: {name}")

    # --- Detect and harmonize source ---
    src = detect_source(df)
    if src == "Scopus":
        df_h = harmonize_scopus(df)
    elif src == "Web of Science":
        df_h = harmonize_wos(df)
    else:
        df_h = df.copy()

    info = {
        "df": df_h,
        "source": src,
        "records": len(df_h),
        "columns": list(df_h.columns),
    }
    return info

# ============================================================
# 4. SUMMARY UTILITIES
# ============================================================
def summarize_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate summary statistics for the loaded dataset."""
    years = pd.to_numeric(df.get("year"), errors="coerce").dropna()
    countries = df.get("countries", pd.Series(dtype=str)).dropna()
    return {
        "records": len(df),
        "year_range": f"{int(years.min())}–{int(years.max())}" if not years.empty else "N/A",
        "countries": countries.nunique() if not countries.empty else 0,
        "sources": df["source"].nunique() if "source" in df else "N/A",
    }

# ============================================================
# 5. DEMO (LOCAL TEST)
# ============================================================
def _demo():
    path = Path("sample_scopus.csv")
    with open(path, "rb") as f:
        info = read_any_table(f)
    print(f"✅ Source: {info['source']} ({info['records']} records)")
    print(f"Columns: {len(info['columns'])}")
    print("Summary:", summarize_dataset(info["df"]))

if __name__ == "__main__":
    _demo()
