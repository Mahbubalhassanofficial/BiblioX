import pandas as pd
import re

SCOPUS_MAP = {
    "Authors":"authors","Author(s) ID":"author_ids","Title":"title","Year":"year",
    "Source title":"source","Cited by":"cited_by","Author Keywords":"author_keywords",
    "Index Keywords":"index_keywords","Affiliations":"affiliations","DOI":"doi",
    "Abstract":"abstract","References":"references","Document Type":"document_type",
    "Country/Territory":"countries"
}
WOS_MAP = {
    "AU":"authors","AF":"authors_full","TI":"title","PY":"year","SO":"source","TC":"cited_by",
    "DE":"author_keywords","ID":"index_keywords","C1":"affiliations","DI":"doi",
    "AB":"abstract","CR":"references","DT":"document_type","CU":"countries"
}
CANONICAL = ["title","authors","year","source","document_type","doi","cited_by",
             "author_keywords","index_keywords","abstract","references",
             "affiliations","countries","source_db"]

def _norm_authors(txt):
    if pd.isna(txt): return ""
    parts = [p.strip() for p in str(txt).replace("|",";").split(";") if p.strip()]
    return "; ".join(parts)

def _norm_keywords(txt):
    if pd.isna(txt) or not str(txt).strip(): return []
    parts = re.split(r"[;,]", str(txt))
    return [p.strip().lower() for p in parts if p.strip()]

def harmonize_scopus(df: pd.DataFrame):
    df = df.rename(columns=SCOPUS_MAP).copy()
    df["source_db"] = "Scopus"
    if "authors" in df: df["authors"] = df["authors"].map(_norm_authors)
    for k in ["author_keywords","index_keywords"]:
        if k in df: df[k] = df[k].map(_norm_keywords)
    return df.reindex(columns=CANONICAL, fill_value="")

def harmonize_wos(df: pd.DataFrame):
    df = df.rename(columns=WOS_MAP).copy()
    df["source_db"] = "WoS"
    if "authors" in df: df["authors"] = df["authors"].map(_norm_authors)
    if "authors" not in df and "authors_full" in df:
        df["authors"] = df["authors_full"].map(_norm_authors)
    for k in ["author_keywords","index_keywords"]:
        if k in df: df[k] = df[k].map(_norm_keywords)
    return df.reindex(columns=CANONICAL, fill_value="")

def merge_and_dedupe(dfs):
    df = pd.concat(dfs, ignore_index=True)
    if "doi" in df and df["doi"].astype(str).str.len().gt(0).any():
        with_doi = df[df["doi"].astype(str).str.len()>0]
        no_doi   = df[~df.index.isin(with_doi.index)]
        df = pd.concat([
            with_doi.drop_duplicates(subset=["doi"], keep="first"),
            no_doi.drop_duplicates(subset=["title","year"], keep="first")
        ], ignore_index=True)
    else:
        df = df.drop_duplicates(subset=["title","year"], keep="first")
    return df
