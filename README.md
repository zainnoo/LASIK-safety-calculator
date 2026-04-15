# LASIK Pre-op Safety Calculator

A Streamlit web app that calculates LASIK pre-operative safety parameters using the Munnerlyn ablation depth formula.

**By Dr. Zain Khatib | YOSI Clinical Tools**

---

## What it calculates (per eye, RE and LE)

| Parameter | Threshold |
|-----------|-----------|
| Ablation Depth (µm) | Informational |
| Residual Stromal Bed (RSB) | ≥ 300 µm = safe |
| Percent Tissue Altered (PTA) | ≤ 40% = safe |
| Estimated post-op Flat K | ≥ 32 D = safe |
| Estimated post-op Steep K | ≤ 50 D = safe |
| Mesopic pupil vs optic zone | Pupil ≤ OZ + 0.5 mm = no warning |

**Formula:** Ablation Depth = (|Sphere| + |Cylinder|) / 3 × Optic Zone²  
(Munnerlyn approximation — same logic as the Excel source file)

Nomogram corrections and microkeratome selection are **not** included — handled separately.

---

## Deploy on Streamlit Community Cloud (free)

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/lasik-safety-calculator.git
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
2. Click **New app**
3. Select your repository and branch (`main`)
4. Set **Main file path** to `app.py`
5. Click **Deploy**

Your app will be live at `https://YOUR_USERNAME-lasik-safety-calculator-app-XXXXX.streamlit.app`

---

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Files

```
lasik-safety-calculator/
├── app.py            # Main Streamlit application
├── requirements.txt  # Python dependencies
└── README.md         # This file
```
