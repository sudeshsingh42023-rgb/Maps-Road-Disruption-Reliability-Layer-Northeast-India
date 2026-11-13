"""Generate a SYNTHETIC crowdsourced road-closure report dataset for Northeast India corridors.
All data is simulated for prototyping. Replace with real data / pilot logs when available.
Run: python generate_data.py
"""
import numpy as np, pandas as pd

rng = np.random.default_rng(42)
N = 6000

SEGMENTS = {  # segment_id: (corridor, landslide-prone weight)
    "GHY-SHL-01": ("Guwahati-Shillong", 0.5),
    "GHY-SHL-02": ("Guwahati-Shillong", 0.4),
    "DMP-KHM-01": ("Dimapur-Kohima", 0.7),
    "KHM-IMP-01": ("Kohima-Imphal", 0.9),
    "KHM-IMP-02": ("Kohima-Imphal", 0.8),
    "SLC-IMP-01": ("Silchar-Imphal", 0.9),
    "AGT-GHY-01": ("Agartala-Guwahati", 0.5),
    "AGT-GHY-02": ("Agartala-Guwahati", 0.6),
}
TYPES = ["landslide", "flooding", "protest_blockade", "accident", "construction"]

seg_ids = rng.choice(list(SEGMENTS), N)
prone = np.array([SEGMENTS[s][1] for s in seg_ids])
rtype = rng.choice(TYPES, N, p=[0.3, 0.2, 0.15, 0.2, 0.15])
rain = np.clip(rng.gamma(2.0, 25 * prone), 0, 300)
conf = rng.poisson(1 + 2 * prone)
den = rng.poisson(1.2, N)
trust = np.clip(rng.beta(4, 2.5, N), 0.05, 0.99)
photo = rng.random(N) < 0.35
mins = rng.exponential(120, N)
hour = rng.integers(0, 24, N)
prior = rng.exponential(30, N)

logit = (-1.2 + 0.9 * (conf - den) / 2 + 2.2 * (trust - 0.5) + 1.1 * photo
         + 0.012 * rain * (rtype == "landslide") + 0.008 * rain * (rtype == "flooding")
         - 0.004 * mins - 0.01 * prior + 0.5 * prone + rng.normal(0, 0.6, N))
p = 1 / (1 + np.exp(-logit))
y = (rng.random(N) < p).astype(int)

df = pd.DataFrame({
    "report_id": np.arange(N), "segment_id": seg_ids,
    "corridor": [SEGMENTS[s][0] for s in seg_ids], "report_type": rtype,
    "rain_mm_24h": rain.round(1), "n_confirmations": conf, "n_denials": den,
    "reporter_trust": trust.round(3), "has_photo": photo.astype(int),
    "minutes_since_report": mins.round(0), "hour_of_day": hour,
    "km_from_prior_closure": prior.round(1), "is_true_closure": y,
})
df.to_csv("reports_synthetic.csv", index=False)
print(f"Wrote reports_synthetic.csv rows={len(df)} base_rate={y.mean():.2f}")
