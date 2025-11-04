import pandas as pd
from io import TextIOWrapper
from typing import Dict
import zipfile

LIKELY_ENCODINGS = ["utf-8", "utf-16", "latin-1"]

def parse_et_bundle(file_like) -> Dict[str, pd.DataFrame]:
    """
    $et is a zip-like bundle with many .TXT tables (each CSV-style).
    We read every .txt inside and map: <basename> -> DataFrame
    """
    out: Dict[str, pd.DataFrame] = {}
    with zipfile.ZipFile(file_like) as z:
        for info in z.infolist():
            if info.is_dir(): 
                continue
            name = info.filename
            if not name.lower().endswith((".txt", ".csv")):
                continue
            with z.open(info) as f:
                data = None
                for enc in LIKELY_ENCODINGS:
                    try:
                        text = TextIOWrapper(f, encoding=enc, errors="ignore").read()
                        data = pd.read_csv(pd.compat.StringIO(text))
                        break
                    except Exception:
                        f.seek(0)
                        continue
                if data is not None:
                    key = name.rsplit("/", 1)[-1].rsplit(".", 1)[0].strip()
                    out[key] = data
    return out
