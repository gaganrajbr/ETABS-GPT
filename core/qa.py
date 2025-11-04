from core.table_store import TableStore

def offline_intents(q: str, ts: TableStore) -> str | None:
    ql = q.lower()

    if "what tables" in ql or ("list" in ql and "tables" in ql):
        names = "\n".join(f"- {n}" for n in ts.sorted_names()[:200])
        extra = "" if ts.table_count() <= 200 else f"\n… and {ts.table_count()-200} more."
        return f"Available tables:\n{names}{extra}"

    if "stories" in ql and "how many" in ql:
        # simple count from story data
        for name in ts.sorted_names():
            if "story" in name.lower():
                return f"**Stories detected:** {len(ts[name])}  \n(Table: *{name}*)"

    # add more deterministic mini-intents here if you want

    return None
