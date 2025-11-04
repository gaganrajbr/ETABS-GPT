import pandas as pd
from typing import Dict, List, Iterable

def _is_table_header(line: str) -> bool:
    return line.strip().upper().startswith("TABLE:")

def parse_e2k_tables(lines: Iterable[str]) -> Dict[str, pd.DataFrame]:
    tables: Dict[str, pd.DataFrame] = {}
    current_name = None
    current_rows: List[str] = []

    def flush():
        nonlocal current_name, current_rows
        if current_name and current_rows:
            csv_text = "\n".join(current_rows).strip()
            if csv_text:
                try:
                    from io import StringIO
                    df = pd.read_csv(StringIO(csv_text))
                    tables[current_name] = df
                except Exception:
                    pass
        current_name, current_rows = None, []

    for raw in lines:
        line = raw.rstrip("\n")
        if _is_table_header(line):
            flush()
            current_name = line.split("TABLE:",1)[1].strip()
            continue
        if current_name:
            s = line.strip()
            if not s or s.startswith("!") or s.startswith("$"):
                continue
            current_rows.append(s)

    flush()
    return tables

