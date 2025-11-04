import pandas as pd
from io import StringIO
from typing import Dict

def parse_e2k(text: str) -> Dict[str, pd.DataFrame]:
    tables: Dict[str, pd.DataFrame] = {}
    current_name = None
    rows = []

    def flush():
        nonlocal current_name, rows
        if current_name and rows:
            csv_text = "\n".join(rows).strip()
            if csv_text:
                try:
                    df = pd.read_csv(StringIO(csv_text))
                    tables[current_name] = df
                except Exception:
                    pass
        current_name, rows = None, []

    for raw in text.splitlines():
        line = raw.rstrip("\n")
        if line.strip().upper().startswith("TABLE:"):
            flush()
            current_name = line.split("TABLE:", 1)[1].strip()
            continue
        if current_name:
            s = line.strip()
            if not s or s.startswith("!") or s.startswith("$"):
                continue
            rows.append(s)

    flush()
    return tables
