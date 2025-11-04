from typing import Dict
import pandas as pd

KEYWORDS = {
    "grid": ["grid"],
    "story": ["story data"],
    "length": ["point coordinates", "frame assignments - connectivity"],
    "section": ["frame section properties"],
    "property": ["frame assignments - property"],
    "load": ["static loads", "load case", "load pattern"],
    "pmm": ["design ratio", "p-m-m", "interaction"],
    "punch": ["punching"],
}

def relevant_tables(question: str, tables: Dict[str, pd.DataFrame], limit_rows: int = 60):
    q = question.lower()
    chosen = {}
    for tag, keys in KEYWORDS.items():
        if any(k in q for k in [tag] + keys):
            for key in tables:
                if any(k in key.lower() for k in keys):
                    chosen[key] = tables[key].head(limit_rows)
    if not chosen:
        for key in list(tables.keys())[:3]:
            chosen[key] = tables[key].head(limit_rows)
    return chosen

def ground_rules(strict: bool = True) -> str:
    base = "You are a structural engineering assistant for ETABS .e2k exports."
    if strict:
        base += (" Use ONLY numbers visible in the provided tables_preview. "
                 "If a number is missing, say you don't have it. Always cite table names used. "
                 "Prefer concise bullet lists or small tables.")
    else:
        base += " Be concise and cite table names where possible."
    return base
