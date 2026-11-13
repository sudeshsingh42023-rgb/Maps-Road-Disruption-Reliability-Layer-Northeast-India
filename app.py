"""Streamlit prototype: 'Can I travel today?' road reliability layer. Run: streamlit run app.py
Data is SYNTHETIC. Requires: python generate_data.py && python train_model.py first.
"""
import json, joblib, numpy as np, pandas as pd, streamlit as st
from gemini_extract import extract_event, SAMPLES

st.set_page_config(page_title="Maps NE Road Reliability", layout="wide")
st.title("Maps Road-Disruption Reliability Layer - Northeast India (prototype)")
st.caption("Synthetic data. Demonstrates crowdsourced report credibility scoring + multilingual event extraction.")

bundle = joblib.load("model.joblib"); model, cols = bundle["model"], bundle["columns"]
df = pd.read_csv("reports_synthetic.csv")
metrics = json.load(open("metrics.json"))

HALF_LIFE_MIN = st.sidebar.slider("Report half-life (minutes)", 60, 480, 180, 30)
OPEN_T = st.sidebar.slider("'Likely closed' threshold", 0.3, 0.9, 0.6, 0.05)
corridor = st.sidebar.selectbox("Corridor", sorted(df.corridor.unique()))

X = pd.get_dummies(df.drop(columns=["report_id", "segment_id", "corridor", "is_true_closure"]),
                   columns=["report_type"]).reindex(columns=cols, fill_value=0)
df["p_true"] = model.predict_proba(X)[:, 1]
df["decay"] = 0.5 ** (df.minutes_since_report / HALF_LIFE_MIN)
df["w"] = df.p_true * df.decay

# Latest 8 reports per segment; recency-weighted average shrunk toward a low prior (no data -> likely open)
PRIOR, K = 0.15, 1.0
latest = df.sort_values("minutes_since_report").groupby("segment_id").head(8)
latest = latest.assign(wp=latest.decay * latest.p_true)
seg = (latest.groupby(["corridor", "segment_id"])
       .agg(reports=("report_id", "count"), sw=("decay", "sum"), swp=("wp", "sum"),
            top_cause=("report_type", lambda s: s.mode().iat[0])).reset_index())
seg["p_closed"] = (seg.swp + K * PRIOR) / (seg.sw + K)
seg["status"] = np.where(seg.p_closed >= OPEN_T, "Likely closed",
                 np.where(seg.p_closed >= 0.35, "Uncertain", "Likely open"))

tab1, tab2, tab3 = st.tabs(["Can I travel today?", "Extract from news (Gemini)", "Alert trade-off"])
with tab1:
    sub = seg[seg.corridor == corridor]
    for _, r in sub.iterrows():
        c1, c2, c3 = st.columns([2, 2, 3])
        c1.metric(r.segment_id, r.status)
        c2.metric("Closure confidence", f"{r.p_closed:.0%}")
        c3.write(f"{r.reports} recent reports - main cause: {r.top_cause}")
    st.info("Product rule: below 35% show nothing; 35-60% show 'Uncertain' with a confirm prompt; "
            "above the threshold show a reroute suggestion.")
with tab2:
    text = st.text_area("Paste news/social text (English / Hindi / Assamese / Bengali)", SAMPLES[0], height=120)
    if st.button("Extract event"):
        st.json(extract_event(text))
with tab3:
    st.write(f"Model AUC **{metrics['auc_model']}** vs naive confirmations>denials rule **{metrics['auc_baseline_rule']}** (synthetic).")
    st.dataframe(pd.DataFrame(metrics["threshold_table"]))
    st.write("Higher threshold = fewer false closure alerts (protects trust) but misses more real closures (hurts safety). "
             "The PRD picks the operating point per cause: stricter for protest/accident, looser for landslide/flood.")
