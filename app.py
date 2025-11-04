import os, json, requests
import streamlit as st
import pandas as pd
from utils.e2k_parser import parse_e2k_tables
from utils.relevance import relevant_tables, ground_rules

st.set_page_config(page_title="ETABS GPT (Online)", page_icon="📐", layout="wide")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY is required. Set it in Streamlit Secrets or environment.")
    st.stop()

APP_PASSWORD = os.getenv("APP_PASSWORD") or st.secrets.get("APP_PASSWORD", "")
if APP_PASSWORD:
    pw = st.sidebar.text_input("Password", type="password")
    if pw != APP_PASSWORD:
        st.stop()

st.title("📐 ETABS GPT — Online")
st.caption("Upload an **ETABS .e2k** export, ask engineering questions, and get grounded GPT answers.")

@st.cache_data(show_spinner=False)
def parse_uploaded(file_bytes: bytes):
    lines = file_bytes.decode("utf-8", "ignore").splitlines()
    return parse_e2k_tables(lines)

uploaded = st.file_uploader("Upload .e2k", type=["e2k","txt"])
if not uploaded:
    st.info("Export your model to **.e2k** in ETABS and upload it here to start.", icon="💡")
    st.stop()

tables = parse_uploaded(uploaded.getvalue())
if not tables:
    st.error("No TABLE blocks detected in this file. Ensure it's a valid .e2k export.")
    st.stop()

with st.expander("📚 Tables (preview)", expanded=False):
    shown = 0
    for name, df in tables.items():
        st.write(f"**{name}** ({len(df)} rows)")
        st.dataframe(df.head(12), use_container_width=True, height=220)
        shown += 1
        if shown >= 8:
            st.caption(f"...and {len(tables)-shown} more tables")
            break

st.subheader("Ask ETABS GPT")
question = st.text_area("Question", value="Summarize the grid spacing and list the 5 longest frames with their lengths.")
strict = st.checkbox("Strict grounding (only use numbers from tables_preview)", value=True)
rows = st.slider("Rows per relevant table to share", 20, 200, 60, 10)

if st.button("Ask"):
    chosen = relevant_tables(question, tables, limit_rows=rows)
    payload = {
        "model": "gpt-4o-mini",
        "temperature": 0 if strict else 0.2,
        "max_tokens": 900,
        "messages": [
            {"role":"system","content": ground_rules(strict)},
            {"role":"user","content": json.dumps({
                "question": question,
                "tables_preview": {k: v.to_dict(orient="list") for k, v in chosen.items()}
            })}
        ]
    }
    try:
        r = requests.post("https://api.openai.com/v1/chat/completions",
                          headers={"Authorization": f"Bearer {OPENAI_API_KEY}",
                                   "Content-Type":"application/json"},
                          data=json.dumps(payload), timeout=90)
        r.raise_for_status()
        st.success(r.json()["choices"][0]["message"]["content"])
    except Exception as e:
        st.error(f"OpenAI request failed: {e}")
