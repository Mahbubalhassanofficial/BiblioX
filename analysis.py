import pandas as pd
from collections import Counter

def annual_counts(df: pd.DataFrame) -> pd.Series:
    s = pd.to_numeric(df["year"], errors="coerce").dropna().astype(int)
    return s.value_counts().sort_index()

def top_sources(df: pd.DataFrame, k=15) -> pd.Series:
    return df["source"].fillna("").value_counts().head(k)

def top_affiliations(df: pd.DataFrame, k=15) -> pd.Series:
    vals = []
    for row in df["affiliations"].fillna(""):
        vals.extend([a.strip() for a in str(row).split(";") if a.strip()])
    return pd.Series(Counter(vals)).sort_values(ascending=False).head(k)

def top_countries(df: pd.DataFrame, k=15) -> pd.Series:
    src = "countries" if "countries" in df.columns else "affiliations"
    vals = []
    for row in df[src].fillna(""):
        vals.extend([a.strip() for a in str(row).split(";") if a.strip()])
    return pd.Series(Counter(vals)).sort_values(ascending=False).head(k)

def keyword_series(df: pd.DataFrame, field="author_keywords", k=30) -> pd.Series:
    allk = []
    if field in df.columns:
        for row in df[field]:
            if isinstance(row, list):
                allk.extend(row)
    return pd.Series(Counter(allk)).sort_values(ascending=False).head(k)
