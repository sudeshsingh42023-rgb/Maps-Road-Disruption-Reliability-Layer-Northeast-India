# Maps Road-Disruption Reliability Layer (Northeast India) - prototype

Product + ML prototype for Google APM application. **All data is synthetic.**

```bash
pip install -r requirements.txt
python generate_data.py      # synthetic crowdsourced reports
python train_model.py        # credibility model -> model.joblib, metrics.json
python gemini_extract.py     # multilingual event extraction (set GEMINI_API_KEY for Gemini; fallback otherwise)
streamlit run app.py         # demo
```
See `PRD.md` for the product thinking. Edit the discovery section with your real interviews before using numbers on a resume.

## Resume bullets (fill [ ] with measured numbers only)
- Authored a PRD for a crowdsourced road-closure reliability layer in Google Maps for Northeast India, grounded in [N] user interviews, with a North Star metric, guardrails and a phased pilot plan.
- Built a report-credibility model (AUC [X] vs [Y] for a naive rule, on synthetic data) and a Streamlit prototype with Gemini API extraction of closure events from multilingual text.


