import math
import pandas as pd
from core.table_store import TableStore

def _find(ts: TableStore, *keywords):
    for name in ts.sorted_names():
        low = name.lower()
        if any(k in low for k in keywords):
            return name, ts[name]
    return None, None

def _get_story_df(ts: TableStore):
    return _find(ts, "story data", "story")

def _get_points_df(ts: TableStore):
    return _find(ts, "point coordinates")

def _get_frames_conn_df(ts: TableStore):
    return _find(ts, "frame assignments - connectivity")

def compute_quick_metrics(ts: TableStore) -> dict:
    out = {}
    s_name, s_df = _get_story_df(ts)
    if s_df is not None:
        # attempt to compute total height
        elev_col = None
        for c in s_df.columns:
            if "elev" in c.lower():
                elev_col = c; break
        if elev_col is not None:
            try:
                vals = pd.to_numeric(s_df[elev_col], errors="coerce").dropna()
                if len(vals):
                    out["Approx. total elevation"] = f"{vals.max():.3f}"
            except Exception:
                pass
        out["Stories detected"] = len(s_df)

    # longest frame (via points + connectivity)
    p_name, P = _get_points_df(ts)
    f_name, F = _get_frames_conn_df(ts)
    if P is not None and F is not None:
        try:
            Pn = P.set_index(next(c for c in P.columns if "point" in c.lower()))[
                [next(c for c in P.columns if c.lower()=='x' or ' x' in c.lower()),
                 next(c for c in P.columns if c.lower()=='y' or ' y' in c.lower()),
                 next(c for c in P.columns if c.lower()=='z' or ' z' in c.lower())]
            ].astype(float)
            frames = []
            ci = next(c for c in F.columns if "pointi" in c.lower())
            cj = next(c for c in F.columns if "pointj" in c.lower())
            fn = next(c for c in F.columns if "frame" in c.lower() or "name" in c.lower())
            for r in F.itertuples(index=False):
                pi, pj = getattr(r, ci), getattr(r, cj)
                if pi in Pn.index and pj in Pn.index:
                    xi, yi, zi = Pn.loc[pi]
                    xj, yj, zj = Pn.loc[pj]
                    L = math.sqrt((xj-xi)**2 + (yj-yi)**2 + (zj-zi)**2)
                    frames.append((getattr(r, fn), L))
            if frames:
                frames.sort(key=lambda x: -x[1])
                name, L = frames[0]
                out["Longest frame (approx)"] = f"{name} ~ {L:.3f}"
        except Exception:
            pass

    return out
