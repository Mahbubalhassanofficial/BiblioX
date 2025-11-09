"""
analysis.py — CBIS Bibliometric Analysis Utilities
---------------------------------------------------
Performs quantitative and descriptive bibliometric analytics on 
harmonized datasets (Scopus / WoS / Combined).

Author: Mahbub Hassan
Affiliation: Department of Civil Engineering, Chulalongkorn University
Lab: B'Deshi Emerging Research Lab
"""

import pandas as pd
from collections import Counter
import numpy as np

# ============================================================
# 1. BASIC TEMPORAL ANALYSIS
# ============================================================
def annual_counts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return annual publication and citation trends.
    Output columns: Year | Publications | Citations | AvgCitations
    """
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    grp = df.groupby("year", dropna=True)
    annual = grp.agg({
        "title": "count",
        "cited_by": lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()
    }).rename(columns={"title": "Publications", "cited_by": "Citations"})
    annual["AvgCitations"] = (annual["Citations"] / annual["Publications"]).round(2)
    return annual.reset_index().sort_values("year")


# ============================================================
# 2. TOP ENTITIES
# ============================================================
def _split_and_flatten(series: pd.Series) -> list[str]:
    """Split semicolon-separated or comma-separated entries."""
    vals = []
    for row in series.fillna(""):
        parts = [a.strip() for a in str(row).replace(",", ";").split(";") if a.strip()]
        vals.extend(parts)
    return vals


def top_sources(df: pd.DataFrame, k: int = 15) -> pd.Series:
    """Top publishing sources (journals / proceedings)."""
    return df["source"].fillna("").value_counts().head(k)


def top_authors(df: pd.DataFrame, k: int = 15) -> pd.Series:
    """Top contributing authors across dataset."""
    vals = _split_and_flatten(df["authors"])
    return pd.Series(Counter(vals)).sort_values(ascending=False).head(k)


def top_affiliations(df: pd.DataFrame, k: int = 15) -> pd.Series:
    """Top author affiliations."""
    vals = _split_and_flatten(df["affiliations"])
    return pd.Series(Counter(vals)).sort_values(ascending=False).head(k)


def top_countries(df: pd.DataFrame, k: int = 15) -> pd.Series:
    """
    Top publishing countries; if 'countries' missing,
    fallback to parsing affiliations.
    """
    src = "countries" if "countries" in df.columns else "affiliations"
    vals = _split_and_flatten(df[src])
    vals = [relabel_country(v) for v in vals]
    return pd.Series(Counter(vals)).sort_values(ascending=False).head(k)


# ============================================================
# 3. KEYWORD ANALYTICS
# ============================================================
def keyword_series(df: pd.DataFrame, field="author_keywords", k: int = 30) -> pd.Series:
    """Return top keywords from given field."""
    allk = []
    if field in df.columns:
        for row in df[field]:
            if isinstance(row, list):
                allk.extend(row)
            elif isinstance(row, str) and row.strip():
                allk.extend([r.strip().lower() for r in row.split(";") if r.strip()])
    return pd.Series(Counter(allk)).sort_values(ascending=False).head(k)


def keyword_evolution(df: pd.DataFrame, min_year=None, max_year=None, top_k=10) -> pd.DataFrame:
    """
    Year-wise keyword frequency table (for thematic evolution mapping).
    Returns a pivot table: Year × Keyword → Count
    """
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"])
    if min_year: df = df[df["year"] >= min_year]
    if max_year: df = df[df["year"] <= max_year]
    records = []
    for _, row in df.iterrows():
        if isinstance(row.get("author_keywords"), list):
            for kw in row["author_keywords"]:
                records.append((row["year"], kw))
    if not records:
        return pd.DataFrame(columns=["year", "keyword", "count"])
    temp = pd.DataFrame(records, columns=["year", "keyword"])
    freq = temp.groupby(["year", "keyword"]).size().reset_index(name="count")
    top_keywords = freq.groupby("keyword")["count"].sum().nlargest(top_k).index
    return freq[freq["keyword"].isin(top_keywords)].pivot(index="year", columns="keyword", values="count").fillna(0)


# ============================================================
# 4. IMPACT METRICS
# ============================================================
def compute_metrics(df: pd.DataFrame) -> dict:
    """
    Compute key bibliometric indicators:
    - total_publications
    - total_citations
    - mean_citations
    - median_citations
    - h_index (approximation)
    - unique_authors
    """
    citations = pd.to_numeric(df["cited_by"], errors="coerce").fillna(0).astype(int)
    citations_sorted = np.sort(citations)[::-1]
    h = int(sum(citations_sorted >= np.arange(1, len(citations_sorted) + 1)))
    return {
        "Total Publications": len(df),
        "Total Citations": int(citations.sum()),
        "Mean Citations": round(float(citations.mean()), 2),
        "Median Citations": round(float(np.median(citations)), 2),
        "h-index (approx.)": h,
        "Unique Authors": df["authors"].nunique(),
    }


# ============================================================
# 5. COUNTRY RELABELING (for consistency)
# ============================================================
def relabel_country(name: str) -> str:
    """Basic normalization of country names."""
    if not name:
        return ""
    name = str(name).strip()
    name = name.replace("United States of America", "USA")
    name = name.replace("United Kingdom", "UK")
    name = name.replace("Peoples R China", "China")
    name = name.replace("Korea South", "South Korea")
    name = name.replace("Iran Islamic Republic", "Iran")
    return name


# ============================================================
# 6. DIAGNOSTIC SUMMARY
# ============================================================
def summary_overview(df: pd.DataFrame) -> pd.DataFrame:
    """Compact overview for Streamlit dashboard."""
    metrics = compute_metrics(df)
    annual = annual_counts(df)
    overview = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"])
    overview.loc[len(overview)] = ["First Year", int(annual["year"].min()) if not annual.empty else None]
    overview.loc[len(overview)] = ["Latest Year", int(annual["year"].max()) if not annual.empty else None]
    return overview
