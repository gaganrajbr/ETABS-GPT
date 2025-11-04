import os, json, io, zipfile, requests
import streamlit as st
from core.table_store import TableStore
from parsers.e2k import parse_e2k
from parsers.et_bundle import parse_et_bundle
from core.relevance import choose_tables_for_question, system_rules
from core.qa import offline_intents
from core.tools import compute_quick_metrics

st.set_page_config(page_title="ETABS GPT", page_icon="📐", layout="wide")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("Missing OPENAI_API_KEY (add in Streamlit Secrets).")
    st.stop()

APP_PASSWORD = os.getenv("APP_PASSWORD") or st.secrets.get("APP_PASSWORD", "")
if APP_PASSWORD:
    if st.sidebar.text_input("Password", type="password") != APP_PASSWORD:
        st.stop()

st.title("📐 ETABS GPT")
st.caption("Upload ETABS exports (.e2k or .$et) and ask questions in natural language. GPT answers are grounded in your tables.")

uploaded = st.file_uploader("Upload .e2k or .$et (zip-like database export)", type=["e2k","et","zip","txt"])
if not uploaded:
    st.info("Tip: For richest answers, export .$et (Tables → Export → 'ETABS Database (*.ETB, *.$et)').", icon="💡")
    st.stop()

# ---- Parse upload into TableStore ----
ts = TableStore()

name = uploaded.name.lower()
raw_bytes = uploaded.read()

if name.endswith(".e2k") or name.endswith(".txt"):
    text = raw_bytes.decode("utf-8", "ignore")
    ts.ingest(parse_e2k(text))
else:
    # .$et is a zip-like bundle with many .txt tables inside
    ts.ingest(parse_et_bundle(io.BytesIO(raw_bytes)))

st.success(f"Loaded {ts.table_count()} tables, ~{ts.total_rows():,} rows")

with st.expander("Browse tables", expanded=False):
    for tname in ts.sorted_names()[:60]:
        df = ts[tname]
        st.write(f"**{tname}**  (rows: {len(df)})")
        st.dataframe(df.head(20), use_container_width=True, height=240)
    if ts.table_count() > 60:
        st.caption(f"... and {ts.table_count() - 60} more tables")

# ---- Quick computed metrics (deterministic, no GPT) ----
with st.expander("Quick metrics (deterministic)", expanded=False):
    metrics = compute_quick_metrics(ts)
    for label, value in metrics.items():
        st.write(f"- **{label}:** {value}")

st.divider()

# ---- Chat UI ----
strict = st.checkbox("Strict grounding (only use numbers from tables sent to GPT)", value=True)
question = st.chat_input("Ask about your model (e.g., 'Which story governs drift? Top 5 longest beams?')")

if "history" not in st.session_state: st.session_state.history = []
for role, content in st.session_state.history:
    with st.chat_message(role): st.markdown(content)

if question:
    st.session_state.history.append(("user", question))
    with st.chat_message("user"): st.markdown(question)

    # 1) Try offline intent handlers first (fast, no cost)
    offline = offline_intents(question, ts)
    if offline:
        with st.chat_message("assistant"): st.markdown(offline)
        st.session_state.history.append(("assistant", offline))
    else:
        # 2) Prepare grounded context for GPT
        chosen = choose_tables_for_question(question, ts, limit_rows=100, max_tables=8)
        preview = {k: ts[k].head(v["rows"]).to_dict(orient="list") for k, v in chosen.items()}
        sysmsg = system_rules(strict=strict)

        payload = {
            "model": "gpt-4o-mini",
            "temperature": 0 if strict else 0.2,
            "max_tokens": 900,
            "messages": [
                {"role":"system","content": sysmsg},
                {"role":"user","content": json.dumps({
                    "question": question,
                    "tables_preview": preview,
                    "notes": "Respond with concise bullets or a small table. Cite table names you used."
                })}
            ]
        }
        try:
            r = requests.post("https://api.openai.com/v1/chat/completions",
                              headers={"Authorization": f"Bearer {OPENAI_API_KEY}",
                                       "Content-Type":"application/json"},
                              data=json.dumps(payload), timeout=90)
            r.raise_for_status()
            answer = r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            answer = f"OpenAI request failed: {e}"

        with st.chat_message("assistant"): st.markdown(answer)
        st.session_state.history.append(("assistant", answer))
