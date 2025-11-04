from typing import Dict
import pandas as pd
from core.table_store import TableStore

KEYS = {
    "grid": ["grid", "grid lines", "grid system"],
    "story": ["story data", "story heights", "story names"],
    "points": ["point coordinates"],
    "frames": ["frame assignments - connectivity", "frame assignments - property"],
    "sections": ["frame section properties", "shell section properties", "material properties"],
    "loads": ["load case", "load pattern", "load combo", "static load", "response spectrum"],
    "drift": ["story drift"],
    "modal": ["modal", "periods", "eigenvalues", "mass participation"],
    "forces": ["frame forces", "shell forces"],
    "design": ["design", "p-m-m", "interaction", "pmm", "utilization", "punch"],
}

def choose_tables_for_question(question: str, ts: TableStore, limit_rows=100, max_tables=8):
    q = question.lower()
    picks: Dict[str, Dict] = {}
    # keyword match
    for tag, candidates in KEYS.items():
        if tag in q or any(c in q for c in candidates):
            for name in ts.sorted_names():
                if any(c in name.lower() for c in candidates):
                    if len(picks) >= max_tables: break
                    picks[name] = {"rows": limit_rows}
    # fallback: first few tables
    if not picks:
        for name in ts.sorted_names()[:max_tables]:
            picks[name] = {"rows": limit_rows}
    return picks

def system_rules(strict=True) -> str:
    base = "You are a structural engineering assistant for ETABS exports (.e2k or .$et)."
    if strict:
        base += " Use ONLY numbers shown in the provided tables_preview. If data is missing, say so. Cite table names in answers. Prefer concise bullets or small tables."
    else:
        base += " Be concise and cite table names."
    return base
