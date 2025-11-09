"""
citations.py — CBIS / BiblioX Citation Vault
--------------------------------------------
Lightweight citation manager for bibliometric workflows.
Handles YAML-based storage, BibTeX/RIS export, and preview formatting.

Author: Mahbub Hassan
Affiliation: Department of Civil Engineering, Chulalongkorn University
Lab: B'Deshi Emerging Research Lab
"""

from __future__ import annotations
import yaml, json, re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from pybtex.database import BibliographyData, Entry

# ============================================================
# 1. VAULT PATHS
# ============================================================
VAULT_DIR = Path("vault")
YAML_PATH = VAULT_DIR / "citations.yaml"
JSON_PATH = VAULT_DIR / "citations.json"

# ============================================================
# 2. CORE LOAD/SAVE
# ============================================================
def load_vault() -> Dict:
    """Load YAML citation vault."""
    if YAML_PATH.exists():
        data = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8")) or {}
        return data
    return {}

def save_vault(db: Dict):
    """Save YAML + JSON vault with timestamped backup."""
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    YAML_PATH.write_text(yaml.safe_dump(db, sort_keys=False, allow_unicode=True), encoding="utf-8")
    JSON_PATH.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")

def backup_vault():
    """Create timestamped backup copy."""
    if YAML_PATH.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = VAULT_DIR / f"citations_backup_{ts}.yaml"
        backup.write_text(YAML_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"[INFO] Backup saved → {backup}")

# ============================================================
# 3. UPSERT / DELETE / SEARCH
# ============================================================
def upsert(key: str, entry_type: str, fields: Dict, persons: Optional[Dict] = None):
    """Insert or update a citation entry."""
    db = load_vault()
    if key in db:
        print(f"[WARN] Updating existing key: {key}")
    db[key] = {
        "type": entry_type,
        "fields": fields,
        "persons": persons or {},
        "updated": datetime.now().isoformat(timespec="seconds"),
    }
    save_vault(db)

def delete_entry(key: str):
    """Remove a citation entry by key."""
    db = load_vault()
    if key in db:
        del db[key]
        save_vault(db)
        print(f"[INFO] Deleted entry: {key}")
    else:
        print(f"[WARN] No entry found for key: {key}")

def search_vault(query: str) -> Dict[str, Dict]:
    """Search vault by keyword, author, or year."""
    db = load_vault()
    results = {}
    q = query.lower()
    for k, v in db.items():
        fields = " ".join(str(x) for x in v.get("fields", {}).values()).lower()
        persons = " ".join(";".join(v.get("persons", {}).get("author", []))).lower()
        if q in fields or q in persons or q in k.lower():
            results[k] = v
    return results

# ============================================================
# 4. EXPORT FUNCTIONS
# ============================================================
def export_bib(path: str = "vault/citations.bib"):
    """Export to BibTeX file."""
    db = load_vault()
    entries = {}
    for k, v in db.items():
        e = Entry(v["type"], fields=v.get("fields", {}))
        if v.get("persons"):
            for role, names in v["persons"].items():
                e.add_persons(role, names)
        entries[k] = e
    BibliographyData(entries).to_file(path)
    print(f"[INFO] BibTeX exported → {path}")

def export_ris(path: str = "vault/citations.ris"):
    """Export to RIS format."""
    db = load_vault()
    lines = []
    typemap = {"article": "JOUR", "inproceedings": "CPAPER", "book": "BOOK", "misc": "GEN"}
    for k, v in db.items():
        lines.append(f"TY  - {typemap.get(v['type'].lower(), 'GEN')}")
        f = v.get("fields", {}); persons = v.get("persons", {})
        for a in persons.get("author", []): lines.append(f"AU  - {a}")
        if f.get("title"): lines.append(f"TI  - {f['title']}")
        if f.get("journal"): lines.append(f"T2  - {f['journal']}")
        if f.get("year"): lines.append(f"PY  - {f['year']}")
        if f.get("doi"): lines.append(f"DO  - {f['doi']}")
        if f.get("volume"): lines.append(f"VL  - {f['volume']}")
        if f.get("number"): lines.append(f"IS  - {f['number']}")
        if f.get("pages"): lines.append(f"SP  - {f['pages']}")
        lines.append("ER  - ")
    Path(path).write_text("\n".join(lines), encoding="utf-8")
    print(f"[INFO] RIS exported → {path}")

# ============================================================
# 5. FORMATTING UTILITIES
# ============================================================
def format_apa(entry: Dict) -> str:
    """Format a single citation as APA-style string (basic)."""
    f = entry.get("fields", {})
    persons = entry.get("persons", {}).get("author", [])
    authors = ", ".join(persons)
    title = f.get("title", "")
    year = f.get("year", "n.d.")
    journal = f.get("journal", "")
    doi = f" https://doi.org/{f['doi']}" if f.get("doi") else ""
    return f"{authors} ({year}). {title}. *{journal}*.{doi}"

def preview_vault(n: int = 5):
    """Print formatted preview of first n entries."""
    db = load_vault()
    for i, (k, v) in enumerate(db.items()):
        print(f"▶ {k}: {format_apa(v)}")
        if i + 1 >= n: break

# ============================================================
# 6. DOI FETCH (OPTIONAL LIVE ENRICHMENT)
# ============================================================
def enrich_from_doi(doi: str) -> Optional[Dict]:
    """Attempt to fetch metadata from DOI.org (if online)."""
    import requests
    url = f"https://api.crossref.org/works/{doi}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()["message"]
            fields = {
                "title": data.get("title", [""])[0],
                "journal": data.get("container-title", [""])[0],
                "year": data.get("issued", {}).get("date-parts", [[None]])[0][0],
                "doi": doi,
            }
            persons = {"author": [f"{a.get('family','')}, {a.get('given','')}" for a in data.get("author", [])]}
            return {"type": data.get("type", "article"), "fields": fields, "persons": persons}
    except Exception as e:
        print(f"[WARN] DOI fetch failed: {e}")
    return None

# ============================================================
# 7. DEMO
# ============================================================
def _demo():
    """Demonstrate adding entries and exporting."""
    upsert(
        key="Hassan2025_AVReview",
        entry_type="article",
        fields={
            "title": "Mapping the Machine Learning Landscape in Autonomous Vehicles",
            "journal": "IEEE Access",
            "year": "2025",
            "doi": "10.1109/ACCESS.2025.3620637",
        },
        persons={"author": ["Hassan, M.", "Kabir, M.E."]},
    )
    preview_vault()
    export_bib()
    export_ris()
    print("✅ Demo citation vault updated.")

if __name__ == "__main__":
    _demo()
