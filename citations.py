import yaml
from pathlib import Path
from pybtex.database import BibliographyData, Entry

VAULT = Path("vault") / "citations.yaml"

def load_vault():
    if VAULT.exists():
        return yaml.safe_load(VAULT.read_text(encoding="utf-8")) or {}
    return {}

def save_vault(db: dict):
    VAULT.parent.mkdir(parents=True, exist_ok=True)
    VAULT.write_text(yaml.safe_dump(db, sort_keys=False, allow_unicode=True), encoding="utf-8")

def upsert(key: str, entry_type: str, fields: dict, persons: dict=None):
    db = load_vault()
    db[key] = {"type": entry_type, "fields": fields, "persons": persons or {}}
    save_vault(db)

def export_bib(path="vault/citations.bib"):
    db = load_vault(); entries = {}
    for k, v in db.items():
        e = Entry(v["type"], fields=v.get("fields", {}))
        if v.get("persons"):
            for role, names in v["persons"].items():
                e.add_persons(role, names)
        entries[k] = e
    BibliographyData(entries).to_file(path)

def export_ris(path="vault/citations.ris"):
    db = load_vault(); lines = []
    typemap = {"article":"JOUR", "inproceedings":"CPAPER", "book":"BOOK", "misc":"GEN"}
    for k, v in db.items():
        lines.append(f"TY  - {typemap.get(v['type'].lower(),'GEN')}")
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
