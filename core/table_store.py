import pandas as pd
from typing import Dict, Iterable

class TableStore:
    def __init__(self):
        self._tables: Dict[str, pd.DataFrame] = {}

    def ingest(self, mapping: Dict[str, pd.DataFrame]):
        for k, df in mapping.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                self._tables[k] = df

    def __getitem__(self, name: str) -> pd.DataFrame:
        return self._tables[name]

    def table_count(self) -> int:
        return len(self._tables)

    def total_rows(self) -> int:
        return sum(len(df) for df in self._tables.values())

    def names(self) -> Iterable[str]:
        return self._tables.keys()

    def sorted_names(self):
        return sorted(self._tables.keys(), key=str.lower)
