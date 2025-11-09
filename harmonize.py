"""
harmonize.py — CBIS Bibliometric Harmonization Module
------------------------------------------------------
Unifies metadata formats from Scopus and Web of Science exports
into a single canonical DataFrame for further analysis.

Author: Mahbub Hassan
Affiliation: Department of Civil Engineering, Chulalongkorn University
Lab: B'Deshi Emerging Research Lab
"""

import pandas as pd
import re

# ============================================================
# 1. COLUMN MAPPINGS
# ============================================================
SCOPUS_MAP = {
    "Authors": "authors",
    "Author(s) ID": "author_ids",
    "Title": "title",
    "Year": "year",
    "Source title": "source",
    "Cited by": "cited_by",
    "Author Keywords": "author_keywords",
    "Index Keywords": "index_keywords",
    "Affiliations": "affiliations",
    "DOI": "doi",
    "Abstract": "abstract",
    "References": "references",
    "Document Type": "document_type",
    "Country/Territory": "countries",
}

WOS_MAP = {
    "AU": "authors",
    "AF": "authors_full",
    "TI": "title",
    "PY": "year",
    "SO": "source",
    "TC": "cited_by",
    "DE": "author_keywords",
    "ID": "index_keywords",
    "C1": "affiliations",
    "DI": "doi",
    "AB": "abstract",
    "CR": "references",
    "DT": "document_type",
    "CU": "countries",
}

CANONICAL = [
    "title", "authors", "year", "source", "document_type", "doi", "cited_by",
    "author_keywords", "index_keywords", "abstract", "references",
    "affiliations", "countries", "source_db"
]

# ============================================================
# 2. NORMALIZATION UTILITIES
# ============================================================
def _norm_authors(txt: str) -> str:
    """Normalize author string; unify delimiters, strip noise."""
    if pd.isna(txt):
        return ""
    txt = str(txt).replace("|", ";").replace(",", ";")
    txt = re.sub(r"\s*et al\.?\s*", "", txt, flags=re.I)
    parts = [p.strip() for p in re.split(r"[;;&]", txt) if p.strip()]
    return "; ".join(dict.fromkeys(parts))  # preserve order, remove duplicates


def _norm_keywords(txt: str) -> list[str]:
    """Normalize keywords → lowercase unique list."""
    if pd.isna(txt) or not str(txt).strip():
        return []
    txt = re.sub(r"[\[\]']", "", str(txt))
    parts = re.split(r"[;,/]", txt)
    cleaned = [p.strip().lower() for p in parts if p.strip()]
    return list(dict.fromkeys(cleaned))


def _norm_doi(txt: str) -> str:
    """Normalize DOI to lowercase and remove URL wrappers."""
    if pd.isna(txt):
        return ""
    s = str(txt).strip().lower()
    s = re.sub(r"(https?://(dx\.)?doi\.org/)", "", s)
    return s


def _detect_source(df: pd.DataFrame) -> str:
    """Detect whether a DataFrame looks like Scopus or WoS."""
    cols = set(df.columns)
    if {"Source title", "Cited by"} & cols:
        return "Scopus"
    elif {"SO", "PY", "AU"} & cols:
        return "WoS"
    return "Unknown"


# ============================================================
# 3. HARMONIZATION PIPELINES
# ============================================================
def harmonize_scopus(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize Scopus export to canonical schema."""
    df = df.rename(columns=SCOPUS_MAP).copy()
    df["source_db"] = "Scopus"

    # Normalize textual fields
    if "authors" in df:
        df["authors"] = df["authors"].map(_norm_authors)
    if "doi" in df:
        df["doi"] = df["doi"].map(_norm_doi)
    for k in ["author_keywords", "index_keywords"]:
        if k in df:
            df[k] = df[k].map(_norm_keywords)

    return df.reindex(columns=CANONICAL, fill_value="")


def harmonize_wos(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize Web of Science export to canonical schema."""
    df = df.rename(columns=WOS_MAP).copy()
    df["source_db"] = "WoS"

    # Author field fallback
    if "authors" not in df and "authors_full" in df:
        df["authors"] = df["authors_full"]
    if "authors" in df:
        df["authors"] = df["authors"].map(_norm_authors)

    if "doi" in df:
        df["doi"] = df["doi"].map(_norm_doi)
    for k in ["author_keywords", "index_keywords"]:
        if k in df:
            df[k] = df[k].map(_norm_keywords)

    return df.reindex(columns=CANONICAL, fill_value="")


# ============================================================
# 4. MERGE + DEDUPLICATE
# ============================================================
def merge_and_dedupe(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    """Merge multiple harmonized DataFrames, removing duplicates."""
    if not dfs:
        return pd.DataFrame(columns=CANONICAL)

    df = pd.concat(dfs, ignore_index=True)
    df = df.dropna(subset=["title"], how="all")

    # Primary deduplication by DOI
    has_doi = df["doi"].astype(str).str.len() > 0
    with_doi = df[has_doi]
    no_doi = df[~has_doi]

    # Unique by DOI, then by title+year+first author (for non-DOI)
    df_doi = with_doi.drop_duplicates(subset=["doi"], keep="first")
    if not no_doi.empty:
        no_doi["first_author"] = no_doi["authors"].map(lambda x: x.split(";")[0] if isinstance(x, str) else "")
        df_no_doi = no_doi.drop_duplicates(subset=["title", "year", "first_author"], keep="first")
    else:
        df_no_doi = pd.DataFrame(columns=df.columns)

    df_final = pd.concat([df_doi, df_no_doi], ignore_index=True)
    df_final.reset_index(drop=True, inplace=True)
    return df_final


# ============================================================
# 5. DIAGNOSTIC SUMMARY
# ============================================================
def summarize_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Return a small diagnostic summary (for logging in Streamlit)."""
    summary = {
        "records_total": len(df),
        "records_with_doi": int(df["doi"].astype(str).str.len().gt(0).sum()),
        "unique_titles": df["title"].nunique(),
        "unique_authors": df["authors"].nunique(),
        "source_breakdown": df["source_db"].value_counts().to_dict(),
        "missing_year": int(df["year"].isna().sum()),
    }
    return pd.DataFrame(list(summary.items()), columns=["Metric", "Value"])
