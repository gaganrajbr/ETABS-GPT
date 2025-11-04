# ETABS GPT (Online-only)

Streamlit app that requires an OpenAI API key and answers questions about ETABS **.e2k** exports.
- No offline analytics; GPT is required.
- Strong grounding: model is told to only use numbers present in the provided table previews.
- Simple optional password via `APP_PASSWORD`.

## Local run
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."   # or set in Streamlit Secrets
streamlit run app.py

## Deploy on Streamlit Community Cloud
- Push this folder to GitHub
- Deploy app with `app.py` as main file
- In Settings → Secrets, set `OPENAI_API_KEY` (and optionally `APP_PASSWORD`)
