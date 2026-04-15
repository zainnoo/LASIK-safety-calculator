import streamlit as st
import math

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LASIK Pre-op Safety Calculator",
    page_icon="👁️",
    layout="wide",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main palette */
    :root {
        --navy: #1a3460;
        --teal: #0a6e78;
        --teal-light: #e6f4f5;
        --red-bg: #fff0f0;
        --red-border: #e53935;
        --green-bg: #f0faf2;
        --green-border: #2e7d32;
        --amber-bg: #fffbe6;
        --amber-border: #f9a825;
    }

    .main-header {
        background: linear-gradient(135deg, #1a3460 0%, #0a6e78 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { color: white; margin: 0; font-size: 1.6rem; }
    .main-header p  { color: rgba(255,255,255,0.82); margin: 0.3rem 0 0; font-size: 0.9rem; }

    .eye-header {
        background: #1a3460;
        color: white;
        padding: 0.6rem 1rem;
        border-radius: 8px 8px 0 0;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 0.03em;
    }
    .eye-block {
        border: 1.5px solid #c5cfe0;
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 1rem 1.2rem 1.2rem;
        background: #fafbfd;
        margin-bottom: 1.2rem;
    }

    /* Result rows */
    .result-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.45rem 0.75rem;
        border-radius: 6px;
        margin-bottom: 0.4rem;
        font-size: 0.92rem;
    }
    .result-label { font-weight: 600; color: #2c3e50; }
    .result-value { font-weight: 700; font-size: 1rem; }

    .result-safe    { background: #f0faf2; border-left: 4px solid #2e7d32; }
    .result-unsafe  { background: #fff0f0; border-left: 4px solid #e53935; }
    .result-neutral { background: #f4f6fb; border-left: 4px solid #1a3460; }
    .result-warn    { background: #fffbe6; border-left: 4px solid #f9a825; }

    .safe-text   { color: #2e7d32; }
    .unsafe-text { color: #e53935; }
    .warn-text   { color: #e65100; }
    .neutral-text{ color: #1a3460; }

    .verdict-safe   { background:#e8f5e9; color:#1b5e20; border:1.5px solid #2e7d32;
                      padding:0.6rem 1rem; border-radius:8px; font-weight:700;
                      font-size:1rem; text-align:center; margin-top:0.8rem; }
    .verdict-unsafe { background:#ffebee; color:#b71c1c; border:1.5px solid #e53935;
                      padding:0.6rem 1rem; border-radius:8px; font-weight:700;
                      font-size:1rem; text-align:center; margin-top:0.8rem; }
    .verdict-warn   { background:#fff8e1; color:#e65100; border:1.5px solid #f9a825;
                      padding:0.6rem 1rem; border-radius:8px; font-weight:700;
                      font-size:1rem; text-align:center; margin-top:0.8rem; }

    .warning-box {
        background: #fff3e0;
        border-left: 4px solid #f57c00;
        border-radius: 6px;
        padding: 0.5rem 0.85rem;
        margin-top: 0.4rem;
        font-size: 0.88rem;
        color: #e65100;
        font-weight: 500;
    }

    .section-divider {
        border: none;
        border-top: 1.5px solid #e0e7ef;
        margin: 0.8rem 0;
    }
    .ref-note {
        font-size:0.8rem; color:#607080; background:#f0f4f8;
        padding:0.5rem 0.8rem; border-radius:6px; margin-top:0.8rem;
    }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>👁️ LASIK Pre-op Safety Calculator</h1>
  <p>Residual stromal bed · Percent tissue altered · Corneal curvature checks · Pupil warning<br>
  By Dr. Zain Khatib &nbsp;|&nbsp; YOSI Clinical Tools</p>
</div>
""", unsafe_allow_html=True)

# ─── Helper: ablation depth formula (from Excel: (|Sph|+|Cyl|)/3 × OZ²) ─────
def ablation_depth(sphere, cyl, oz):
    """Munnerlyn approximation: depth = (|Sph| + |Cyl|) / 3 × OZ²"""
    return (abs(sphere) + abs(cyl)) / 3.0 * (oz ** 2)

# ─── Helper: render a single eye ─────────────────────────────────────────────
def render_eye(eye_label, key_prefix):
    st.markdown(f'<div class="eye-header">{"🔵" if eye_label=="Right Eye (RE)" else "🟡"} {eye_label}</div>', unsafe_allow_html=True)
    st.markdown('<div class="eye-block">', unsafe_allow_html=True)

    # ── Inputs ────────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        sph = st.number_input("Sphere (D)", min_value=-20.0, max_value=8.0, value=0.0,
                              step=0.25, format="%.2f", key=f"{key_prefix}_sph",
                              help="Manifest refraction sphere, e.g. −5.00")
    with c2:
        cyl = st.number_input("Cylinder (D, negative)", min_value=-8.0, max_value=0.0,
                              value=0.0, step=0.25, format="%.2f", key=f"{key_prefix}_cyl",
                              help="Enter as a negative value, e.g. −1.50")
    with c3:
        axis = st.number_input("Axis (°)", min_value=0, max_value=180, value=90,
                               step=1, key=f"{key_prefix}_axis")

    c4, c5, c6 = st.columns(3)
    with c4:
        pachy = st.number_input("Pachymetry (µm)", min_value=300, max_value=700,
                                value=540, step=1, key=f"{key_prefix}_pachy",
                                help="Central corneal thickness in µm")
    with c5:
        flap = st.number_input("Flap thickness (µm)", min_value=60, max_value=200,
                               value=110, step=5, key=f"{key_prefix}_flap",
                               help="Planned / achieved flap thickness in µm")
    with c6:
        oz = st.number_input("Optic zone (mm)", min_value=5.0, max_value=8.5,
                             value=6.5, step=0.1, format="%.1f", key=f"{key_prefix}_oz",
                             help="Treatment optic zone diameter in mm")

    c7, c8, c9 = st.columns(3)
    with c7:
        kf = st.number_input("Flat K (D)", min_value=30.0, max_value=52.0,
                             value=43.0, step=0.1, format="%.2f", key=f"{key_prefix}_kf",
                             help="Flattest meridian keratometry reading")
    with c8:
        ks = st.number_input("Steep K (D)", min_value=30.0, max_value=58.0,
                             value=44.0, step=0.1, format="%.2f", key=f"{key_prefix}_ks",
                             help="Steepest meridian keratometry reading")
    with c9:
        pupil = st.number_input("Mesopic pupil (mm)", min_value=2.0, max_value=10.0,
                                value=5.5, step=0.1, format="%.1f", key=f"{key_prefix}_pupil",
                                help="Mesopic pupil diameter measured in dim light")

    # ── Calculations ──────────────────────────────────────────────────────────
    abd = ablation_depth(sph, cyl, oz)                        # µm
    rsb = pachy - flap - abd                                  # µm residual stromal bed
    pta = (flap + abd) / pachy * 100                          # % tissue altered
    post_k_flat = kf - abs(sph + cyl / 2)                    # approximate post-op flat K
    post_k_steep = ks - abs(sph + cyl / 2)                   # approximate post-op steep K

    # Safety flags
    rsb_safe   = rsb >= 300
    pta_safe   = pta <= 40
    flat_safe  = post_k_flat >= 32                            # Excel: < 32 D = too flat
    steep_safe = (ks - abs(sph)) <= 50                        # Excel: post-op steep K > 50 D = too steep
    pupil_ok   = pupil <= oz + 0.5

    overall_safe = rsb_safe and pta_safe and flat_safe and steep_safe

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Results ───────────────────────────────────────────────────────────────
    r1, r2 = st.columns(2)

    with r1:
        # Ablation depth
        st.markdown(
            f'<div class="result-row result-neutral">'
            f'<span class="result-label">Ablation Depth</span>'
            f'<span class="result-value neutral-text">{abd:.0f} µm</span>'
            f'</div>', unsafe_allow_html=True)

        # RSB
        rsb_cls  = "result-safe"  if rsb_safe  else "result-unsafe"
        rsb_tcls = "safe-text"    if rsb_safe  else "unsafe-text"
        rsb_note = "✓ Safe (≥300 µm)" if rsb_safe else "✗ UNSAFE — < 300 µm"
        st.markdown(
            f'<div class="result-row {rsb_cls}">'
            f'<span class="result-label">Residual Stromal Bed (RSB)</span>'
            f'<span class="result-value {rsb_tcls}">{rsb:.0f} µm &nbsp; <small>{rsb_note}</small></span>'
            f'</div>', unsafe_allow_html=True)

        # PTA
        pta_cls  = "result-safe"  if pta_safe  else "result-unsafe"
        pta_tcls = "safe-text"    if pta_safe  else "unsafe-text"
        pta_note = "✓ Safe (≤40%)" if pta_safe else "✗ UNSAFE — > 40%"
        st.markdown(
            f'<div class="result-row {pta_cls}">'
            f'<span class="result-label">Percent Tissue Altered (PTA)</span>'
            f'<span class="result-value {pta_tcls}">{pta:.1f}% &nbsp; <small>{pta_note}</small></span>'
            f'</div>', unsafe_allow_html=True)

    with r2:
        # Post-op flat K
        flat_cls  = "result-safe"  if flat_safe  else "result-unsafe"
        flat_tcls = "safe-text"    if flat_safe  else "unsafe-text"
        flat_note = "✓ Not excessively flat" if flat_safe else "✗ UNSAFE — cornea too flat (<32 D)"
        st.markdown(
            f'<div class="result-row {flat_cls}">'
            f'<span class="result-label">Est. Post-op Flat K</span>'
            f'<span class="result-value {flat_tcls}">{post_k_flat:.2f} D &nbsp; <small>{flat_note}</small></span>'
            f'</div>', unsafe_allow_html=True)

        # Post-op steep K (overshoot check)
        steep_val = ks - abs(sph)
        steep_cls  = "result-safe"  if steep_safe  else "result-unsafe"
        steep_tcls = "safe-text"    if steep_safe  else "unsafe-text"
        steep_note = "✓ Not excessively steep" if steep_safe else "✗ UNSAFE — cornea too steep (>50 D)"
        st.markdown(
            f'<div class="result-row {steep_cls}">'
            f'<span class="result-label">Est. Post-op Steep K</span>'
            f'<span class="result-value {steep_tcls}">{steep_val:.2f} D &nbsp; <small>{steep_note}</small></span>'
            f'</div>', unsafe_allow_html=True)

        # Pupil vs optic zone
        pupil_cls  = "result-safe" if pupil_ok else "result-warn"
        pupil_tcls = "safe-text"   if pupil_ok else "warn-text"
        pupil_note = "✓ Within range" if pupil_ok else "⚠ Pupil large — consider increasing optic zone"
        st.markdown(
            f'<div class="result-row {pupil_cls}">'
            f'<span class="result-label">Pupil vs Optic Zone</span>'
            f'<span class="result-value {pupil_tcls}">{pupil:.1f} mm vs {oz:.1f} mm OZ &nbsp; <small>{pupil_note}</small></span>'
            f'</div>', unsafe_allow_html=True)

    # ── Overall verdict ───────────────────────────────────────────────────────
    if overall_safe:
        verdict_cls = "verdict-safe"
        verdict_txt = "✅ RSB and PTA are safe for LASIK"
    else:
        msgs = []
        if not rsb_safe:
            msgs.append("Reduce optic zone or correction to increase RSB")
        if not pta_safe:
            msgs.append("PTA >40% — reduce ablation depth")
        if not flat_safe:
            msgs.append("Post-op cornea will be excessively flat — reduce correction")
        if not steep_safe:
            msgs.append("Post-op cornea will be excessively steep — reduce correction")
        verdict_cls = "verdict-unsafe"
        verdict_txt = "❌ LASIK UNSAFE — " + " | ".join(msgs)

    st.markdown(f'<div class="{verdict_cls}">{verdict_txt}</div>', unsafe_allow_html=True)

    if not pupil_ok:
        st.markdown(
            f'<div class="warning-box">⚠️ Warning: Mesopic pupil ({pupil:.1f} mm) is larger than optic zone + 0.5 mm ({oz+0.5:.1f} mm). '
            f'Consider increasing the optic zone to reduce dysphotopsia risk.</div>',
            unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    return {
        "abd": abd, "rsb": rsb, "pta": pta,
        "rsb_safe": rsb_safe, "pta_safe": pta_safe,
        "flat_safe": flat_safe, "steep_safe": steep_safe,
        "overall_safe": overall_safe,
    }

# ─── Layout: two eyes side by side ────────────────────────────────────────────
col_re, col_le = st.columns(2)

with col_re:
    re = render_eye("Right Eye (RE)", "re")

with col_le:
    le = render_eye("Left Eye (LE)", "le")

# ─── Reference thresholds ─────────────────────────────────────────────────────
st.markdown("""
<div class="ref-note">
<strong>Safety thresholds used:</strong>
&nbsp; RSB ≥ 300 µm &nbsp;|&nbsp; PTA ≤ 40% &nbsp;|&nbsp; Post-op flat K ≥ 32 D &nbsp;|&nbsp;
Post-op steep K ≤ 50 D &nbsp;|&nbsp; Ablation depth = (|Sph| + |Cyl|) / 3 × OZ² (Munnerlyn approximation).
<br>These thresholds match the Excel pre-op safety calculator by Dr. Zain Khatib. Nomogram and microkeratome
selection are handled separately. Clinical judgment always takes precedence.
</div>
""", unsafe_allow_html=True)
