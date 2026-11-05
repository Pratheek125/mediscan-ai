import os, sys, json, tempfile
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

from ocr.engine import extract_text_from_pdf
from ml_engine.analysis import analyze
from ml_engine.ai_engine import evaluation_table
from patient_data.database import init_db, save_report, history
from patient_data.trends import trend_frame
from translator.translate_report import translate_text
from tts.generate_audio import generate_audio_for_language
from utils.generate_pdf_report import generate_pdf_report

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
init_db()

st.set_page_config(page_title="MediScan AI", page_icon="🩺", layout="wide", initial_sidebar_state="expanded")

# ----------------------------------------------------------------------------------
# THEME / DESIGN SYSTEM
# ----------------------------------------------------------------------------------
COLORS = {
    "NORMAL": "#22c55e",
    "HIGH": "#f43f5e",
    "LOW": "#f59e0b",
}
SEVERITY_COLORS = {
    "Normal": "#22c55e",
    "Mild": "#f59e0b",
    "Moderate": "#fb7185",
    "Critical": "#ef4444",
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');

:root{
  --bg-0:#070c17; --bg-1:#0b1424; --bg-2:#0f1b30;
  --card:rgba(255,255,255,.045); --card-hi:rgba(255,255,255,.075);
  --border:rgba(255,255,255,.09); --border-hi:rgba(99,179,255,.35);
  --text:#eaf3ff; --muted:#8ea3c0; --muted2:#6b7f9c;
  --accent:#3fa9ff; --accent2:#8b5cf6; --teal:#2dd4bf;
  --good:#22c55e; --warn:#f59e0b; --bad:#f43f5e;
}
html, body, [class*="css"]{font-family:'Manrope',-apple-system,sans-serif;}
h1,h2,h3,h4{font-family:'Sora',sans-serif !important; letter-spacing:-.01em;}

.stApp{
  background:
    radial-gradient(1100px 600px at 85% -8%, rgba(63,169,255,.12), transparent 60%),
    radial-gradient(900px 500px at -10% 10%, rgba(139,92,246,.10), transparent 55%),
    linear-gradient(180deg, var(--bg-0), var(--bg-1) 45%, var(--bg-2));
  color:var(--text);
}
.block-container{padding-top:1.6rem; padding-bottom:3rem; max-width:1300px;}
#MainMenu, footer {visibility:hidden;}

/* ---------- Hero ---------- */
.hero{
  position:relative; overflow:hidden;
  background:linear-gradient(135deg, rgba(63,169,255,.14), rgba(139,92,246,.10) 60%, rgba(45,212,191,.08));
  border:1px solid var(--border-hi); border-radius:22px;
  padding:2.1rem 2.4rem; margin-bottom:1.4rem;
  box-shadow:0 20px 60px -25px rgba(63,169,255,.35);
}
.hero::after{
  content:""; position:absolute; inset:0; border-radius:22px;
  background:radial-gradient(400px 200px at 90% 0%, rgba(255,255,255,.08), transparent 70%);
  pointer-events:none;
}
.hero .eyebrow{
  display:inline-flex; align-items:center; gap:.4rem; font-size:.72rem; font-weight:700;
  letter-spacing:.08em; text-transform:uppercase; color:var(--accent);
  background:rgba(63,169,255,.12); border:1px solid rgba(63,169,255,.3);
  padding:.25rem .7rem; border-radius:99px; margin-bottom:.7rem;
}
.hero h1{margin:0; font-size:2.1rem; color:var(--text);}
.hero p{margin:.4rem 0 0; color:var(--muted); font-size:1rem; max-width:60ch;}

/* ---------- Cards ---------- */
.card{
  background:var(--card); border:1px solid var(--border); border-radius:18px;
  padding:1.35rem 1.5rem; margin-bottom:1rem;
  backdrop-filter:blur(6px);
  transition:border-color .2s ease, transform .2s ease;
}
.card:hover{border-color:var(--border-hi);}
.section-title{
  display:flex; align-items:center; gap:.55rem; font-size:1.05rem; font-weight:700;
  color:var(--text); margin:1.4rem 0 .7rem;
}
.section-title .bar{width:4px; height:1.05rem; border-radius:4px; background:linear-gradient(180deg,var(--accent),var(--accent2));}

/* ---------- KPI tiles ---------- */
.kpi-row{display:grid; grid-template-columns:repeat(4,1fr); gap:.85rem; margin-bottom:.4rem;}
.kpi{
  background:var(--card); border:1px solid var(--border); border-radius:16px; padding:1rem 1.1rem;
  position:relative; overflow:hidden;
}
.kpi .lbl{font-size:.74rem; color:var(--muted2); text-transform:uppercase; letter-spacing:.06em; font-weight:700;}
.kpi .val{font-size:1.65rem; font-weight:800; margin-top:.15rem; font-family:'Sora',sans-serif;}
.kpi .sub{font-size:.78rem; color:var(--muted); margin-top:.1rem;}
.kpi.good .val{color:var(--good);} .kpi.bad .val{color:var(--bad);} .kpi.warn .val{color:var(--warn);} .kpi.acc .val{color:var(--accent);}

/* ---------- Status pills ---------- */
.pill{display:inline-flex; align-items:center; gap:.35rem; font-size:.72rem; font-weight:700;
  padding:.18rem .6rem; border-radius:99px; letter-spacing:.03em;}
.pill-normal{background:rgba(34,197,94,.14); color:#4ade80; border:1px solid rgba(34,197,94,.3);}
.pill-high{background:rgba(244,63,94,.14); color:#fb7185; border:1px solid rgba(244,63,94,.3);}
.pill-low{background:rgba(245,158,11,.14); color:#fbbf24; border:1px solid rgba(245,158,11,.3);}

/* ---------- Evidence rows ---------- */
.evi{
  display:flex; align-items:flex-start; gap:.6rem; padding:.55rem .7rem; border-radius:12px;
  background:rgba(255,255,255,.03); border:1px solid var(--border); margin-bottom:.45rem; font-size:.88rem;
}
.evi .dot{width:8px;height:8px;border-radius:50%; margin-top:.35rem; flex-shrink:0;}

/* ---------- Buttons ---------- */
.stButton>button, .stDownloadButton>button{
  border-radius:12px !important; font-weight:700 !important; border:1px solid var(--border) !important;
  transition:.15s ease !important;
}
.stButton>button[kind="primary"], .stDownloadButton>button{
  background:linear-gradient(135deg, var(--accent), var(--accent2)) !important; color:#fff !important; border:none !important;
  box-shadow:0 10px 26px -12px rgba(63,169,255,.55) !important;
}
.stButton>button[kind="primary"]:hover, .stDownloadButton>button:hover{filter:brightness(1.08); transform:translateY(-1px);}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"]{
  background:linear-gradient(180deg, var(--bg-1), var(--bg-0)); border-right:1px solid var(--border);
}
.brand{text-align:center; padding:.6rem 0 1rem;}
.brand .logo{font-size:2.4rem; filter:drop-shadow(0 0 14px rgba(63,169,255,.5));}
.brand h3{margin:.2rem 0 0; color:var(--text);}
.brand p{margin:0; color:var(--muted2); font-size:.78rem; letter-spacing:.04em; text-transform:uppercase;}

.safety{
  background:rgba(245,158,11,.08); border:1px solid rgba(245,158,11,.28); border-radius:12px;
  padding:.7rem .85rem; color:#fcd34d; font-size:.8rem; margin-top:.6rem;
}

hr{border-color:var(--border) !important;}
.stTabs [data-baseweb="tab-list"]{gap:4px;}
.stTabs [data-baseweb="tab"]{
  background:var(--card); border-radius:10px 10px 0 0; border:1px solid var(--border); border-bottom:none;
  padding:.55rem 1.1rem; color:var(--muted);
}
.stTabs [aria-selected="true"]{color:var(--text) !important; background:var(--card-hi) !important;}

[data-testid="stMetricValue"]{font-family:'Sora',sans-serif;}
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------------------
def pill(status):
    cls = {"NORMAL": "pill-normal", "HIGH": "pill-high", "LOW": "pill-low"}.get(status, "pill-normal")
    icon = {"NORMAL": "●", "HIGH": "▲", "LOW": "▼"}.get(status, "●")
    return f"<span class='pill {cls}'>{icon} {status}</span>"


def kpi_card(label, value, sub="", tone=""):
    return f"""<div class='kpi {tone}'><div class='lbl'>{label}</div><div class='val'>{value}</div><div class='sub'>{sub}</div></div>"""


def section_title(icon, text):
    st.markdown(f"<div class='section-title'><span class='bar'></span>{icon} {text}</div>", unsafe_allow_html=True)


def style_param_table(df: pd.DataFrame):
    def row_style(row):
        color = COLORS.get(row["Status"], "#8ea3c0")
        return [f"box-shadow: inset 3px 0 0 0 {color};"] * len(row)

    def status_col(val):
        color = COLORS.get(val, "#8ea3c0")
        return f"color:{color}; font-weight:700;"

    styler = df.style.apply(row_style, axis=1)
    map_fn = styler.map if hasattr(styler, "map") else styler.applymap
    if "Status" in df.columns:
        styler = map_fn(status_col, subset=["Status"])
    if "Severity" in df.columns:
        map_fn = styler.map if hasattr(styler, "map") else styler.applymap
        styler = map_fn(
            lambda v: f"color:{SEVERITY_COLORS.get(v,'#8ea3c0')}; font-weight:600;", subset=["Severity"]
        )
    return styler


def confidence_gauge(conf, label):
    color = "#3fa9ff"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(conf * 100, 1),
        number={"suffix": "%", "font": {"size": 34, "family": "Sora"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#5b7291", "tickfont": {"color": "#8ea3c0", "size": 10}},
            "bar": {"color": color, "thickness": .32},
            "bgcolor": "rgba(255,255,255,.04)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 50], "color": "rgba(244,63,94,.15)"},
                {"range": [50, 75], "color": "rgba(245,158,11,.15)"},
                {"range": [75, 100], "color": "rgba(34,197,94,.15)"},
            ],
        },
    ))
    fig.update_layout(
        height=210, margin=dict(l=20, r=20, t=25, b=5),
        paper_bgcolor="rgba(0,0,0,0)", font={"color": "#eaf3ff"},
        title={"text": f"Model confidence — {label}", "font": {"size": 13, "color": "#8ea3c0"}, "x": .5},
    )
    return fig


def deviation_chart(data):
    df = pd.DataFrame(data).copy()
    if df.empty:
        return None
    df = df.sort_values("Deviation %", key=lambda s: s.abs(), ascending=True)
    colors = [COLORS.get(s, "#3fa9ff") for s in df["Status"]]
    fig = go.Figure(go.Bar(
        x=df["Deviation %"], y=df["Parameter"], orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:+.1f}%" for v in df["Deviation %"]], textposition="outside",
        hovertext=[f"{p}: {v} {u}" for p, v, u in zip(df["Parameter"], df["Value"], df["Unit"])],
        hoverinfo="text",
    ))
    fig.update_layout(
        height=max(280, 34 * len(df)), margin=dict(l=10, r=30, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#cfe1f7", "size": 12},
        xaxis=dict(title="Deviation from reference range (%)", gridcolor="rgba(255,255,255,.06)", zeroline=True, zerolinecolor="rgba(255,255,255,.18)"),
        yaxis=dict(gridcolor="rgba(255,255,255,.03)"),
        showlegend=False,
    )
    return fig


def donut_status(data):
    df = pd.DataFrame(data)
    counts = df["Status"].value_counts().reindex(["NORMAL", "HIGH", "LOW"]).fillna(0)
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values, hole=.68,
        marker=dict(colors=[COLORS["NORMAL"], COLORS["HIGH"], COLORS["LOW"]]),
        textinfo="value", textfont=dict(color="#0a0f1e", size=13, family="Sora"),
    ))
    fig.update_layout(
        height=220, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", showlegend=True,
        legend=dict(orientation="h", y=-.12, font=dict(color="#8ea3c0", size=11)),
        annotations=[dict(text=f"{len(df)}<br><span style='font-size:11px;color:#8ea3c0'>params</span>",
                           x=.5, y=.5, font=dict(size=22, color="#eaf3ff", family="Sora"), showarrow=False)],
    )
    return fig


# ----------------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        "<div class='brand'><div class='logo'>🩺</div><h3>MediScan AI</h3>"
        "<p>Final-Year Edition</p></div>", unsafe_allow_html=True,
    )
    selected = option_menu(
        None, ["Upload & Analyze", "Patient History", "Model Evaluation", "About"],
        icons=["file-earmark-medical", "clock-history", "graph-up-arrow", "info-circle"],
        default_index=0,
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "icon": {"color": "#3fa9ff", "font-size": "15px"},
            "nav-link": {"font-size": "14px", "text-align": "left", "margin": "3px 0", "border-radius": "10px",
                         "color": "#c7d6ea", "padding": "10px 12px"},
            "nav-link-selected": {"background": "linear-gradient(135deg, rgba(63,169,255,.22), rgba(139,92,246,.18))",
                                   "color": "#eaf3ff", "font-weight": "600",
                                   "border": "1px solid rgba(99,179,255,.35)"},
        },
    )
    st.markdown("---")
    with st.expander("📘 Quick guide", expanded=False):
        st.markdown(
            "1. Enter patient details & upload a PDF\n"
            "2. Click **Analyze Report**\n"
            "3. Review parameters, AI pattern & evidence\n"
            "4. Translate / generate voice / export PDF\n"
            "5. Track trends in **Patient History**"
        )
    st.markdown(
        "<div class='safety'>⚠️ Educational / decision-support prototype.<br>Not for diagnosis or treatment.</div>",
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------------------
# PAGE: UPLOAD & ANALYZE
# ----------------------------------------------------------------------------------
if selected == "Upload & Analyze":
    st.markdown(
        "<div class='hero'><span class='eyebrow'>🧬 AI-Assisted Diagnostics</span>"
        "<h1>MediScan AI</h1>"
        "<p>Explainable AI-assisted medical report understanding, longitudinal monitoring "
        "and multilingual accessibility — all in one reproducible pipeline.</p></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<div class='kpi-row'>"
        f"{kpi_card('AI layers', '4', 'OCR · NLP · ML · XAI', 'acc')}"
        f"{kpi_card('Report groups', '6+', 'CBC, lipid, renal…', 'acc')}"
        f"{kpi_card('Languages', '6', 'incl. regional TTS', 'acc')}"
        f"{kpi_card('History store', 'SQLite', 'longitudinal trends', 'acc')}"
        f"</div>", unsafe_allow_html=True,
    )

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    section_title("📤", "Patient & Report Details")
    left, right = st.columns([1, 1])
    with left:
        patient = st.text_input("Patient name", placeholder="e.g. Ravi Kumar")
        language = st.selectbox("Output language", ["English", "Kannada", "Hindi", "Tamil", "Telugu", "Malayalam"])
    with right:
        phone = st.text_input("WhatsApp number (optional)", placeholder="+91XXXXXXXXXX")
        uploaded = st.file_uploader("Upload medical PDF", type=["pdf"])
    analyze_btn = st.button("🔍  Analyze Report", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if analyze_btn:
        if not patient.strip() or not uploaded:
            st.error("Enter a patient name and upload a PDF.")
        else:
            work = ROOT / "outputs"
            work.mkdir(exist_ok=True)
            pdf_path = work / "uploaded_report.pdf"
            pdf_path.write_bytes(uploaded.getbuffer())
            with st.status("Running MediScan AI pipeline…", expanded=True) as status:
                st.write("📄 Extracting native PDF text / OCR…")
                text = extract_text_from_pdf(str(pdf_path))
                st.session_state["raw_text"] = text
                st.write("🧠 Parsing parameters, running ML ensemble & explainability…")
                summary, data, types, label, conf, per_model, results = analyze(text)
                st.session_state.update({
                    "summary": summary, "data": data, "types": types, "label": label,
                    "conf": conf, "per_model": per_model, "results": results,
                    "patient": patient, "language": language,
                })
                st.write("💾 Saving to patient history…")
                save_report(patient, ", ".join(types) if types else "Unknown", label, conf, summary, data)
                status.update(label="Analysis complete", state="complete", expanded=False)
            st.toast("Report analyzed successfully", icon="✅")

    if "data" in st.session_state:
        data = st.session_state["data"]
        summary = st.session_state["summary"]
        label = st.session_state["label"]
        conf = st.session_state["conf"]
        types = st.session_state.get("types", [])
        patient = st.session_state.get("patient", "")
        language = st.session_state.get("language", "English")
        phone = phone if "phone" in dir() else ""

        abnormal = [d for d in data if d["Status"] != "NORMAL"]
        normal_ct = len(data) - len(abnormal)

        st.markdown(
            f"<div class='kpi-row'>"
            f"{kpi_card('Parameters found', len(data), ', '.join(types) if types else 'Unknown report type', 'acc')}"
            f"{kpi_card('Within range', normal_ct, 'normal parameters', 'good')}"
            f"{kpi_card('Flagged', len(abnormal), 'outside reference range', 'bad' if abnormal else 'good')}"
            f"{kpi_card('AI confidence', f'{conf:.0%}', label, 'warn' if conf < .6 else 'acc')}"
            f"</div>", unsafe_allow_html=True,
        )

        tabs = st.tabs(["🧪 Parameters", "🤖 AI Insights", "🌍 Translate & Voice", "📄 Report & Share"])

        # ---- Parameters tab ----
        with tabs[0]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            section_title("🧪", "Extracted & Normalized Parameters")
            if data:
                cA, cB = st.columns([2, 1])
                with cA:
                    st.dataframe(style_param_table(pd.DataFrame(data)), use_container_width=True, hide_index=True)
                with cB:
                    st.plotly_chart(donut_status(data), use_container_width=True)
                dchart = deviation_chart(data)
                if dchart is not None:
                    st.plotly_chart(dchart, use_container_width=True)
            else:
                st.warning("No supported parameters were extracted. Try a clearer PDF or verify that Tesseract OCR is installed for scanned documents.")
            st.markdown("</div>", unsafe_allow_html=True)

        # ---- AI Insights tab ----
        with tabs[1]:
            a, b = st.columns([1, 1.2])
            with a:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                section_title("🤖", "AI Pattern Assessment")
                st.plotly_chart(confidence_gauge(conf, label), use_container_width=True)
                st.markdown("**Why was this result flagged?**")
                if abnormal:
                    for x in abnormal[:8]:
                        color = COLORS.get(x["Status"], "#8ea3c0")
                        st.markdown(
                            f"<div class='evi'><span class='dot' style='background:{color}'></span>"
                            f"<div><b>{x['Parameter']}</b> {pill(x['Status'])} &nbsp;"
                            f"<span style='color:var(--muted)'>{x['Deviation %']}% deviation · severity {x.get('Severity','—')}</span></div></div>",
                            unsafe_allow_html=True,
                        )
                else:
                    st.success("No abnormal parameters detected.")
                st.markdown("</div>", unsafe_allow_html=True)
            with b:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                section_title("🧠", "Patient-Friendly Explanation")
                st.write(summary)
                st.markdown("</div>", unsafe_allow_html=True)
            st.warning("Medical safety: model outputs are informational, trained on a synthetic academic benchmark, and are not clinically validated. They must not be used as a diagnosis or treatment recommendation.")

        # ---- Translate & Voice tab ----
        with tabs[2]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            section_title("🌍", "Translation & Voice")
            tr1, tr2 = st.columns([2, 1])
            with tr1:
                if st.button("🌐 Translate to all 6 languages", use_container_width=True):
                    with st.spinner("Translating…"):
                        translated = translate_text(summary)
                    st.session_state["translated"] = translated
                    st.success("Translations generated.")
            with tr2:
                if st.button(f"🔊 Generate {language} audio", use_container_width=True):
                    txt = st.session_state.get("translated", {}).get(language, summary)
                    path = generate_audio_for_language(txt, language)
                    st.session_state["audio_path"] = path
            if st.session_state.get("translated"):
                st.text_area(f"{language} translation", st.session_state["translated"].get(language, summary), height=170)
            if st.session_state.get("audio_path") and Path(st.session_state["audio_path"]).exists():
                st.audio(Path(st.session_state["audio_path"]).read_bytes(), format="audio/mp3")
            st.markdown("</div>", unsafe_allow_html=True)

        # ---- Report & Share tab ----
        with tabs[3]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            section_title("📄", "Final Report")
            if st.button("📑 Generate downloadable AI report", use_container_width=True):
                p = generate_pdf_report(patient, data, summary, label, conf, types)
                st.session_state["report_pdf"] = p
            if st.session_state.get("report_pdf"):
                p = st.session_state["report_pdf"]
                st.download_button("⬇️ Download AI Medical Report", Path(p).read_bytes(),
                                    file_name="MediScan_AI_Report.pdf", mime="application/pdf",
                                    use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            section_title("📲", "WhatsApp Delivery")
            if phone:
                if st.button("📤 Open WhatsApp delivery workflow", use_container_width=True):
                    try:
                        from ui.send_whatsapp_attachment import send_files_whatsapp
                        audio = st.session_state.get("audio_path")
                        pdf = st.session_state.get("report_pdf")
                        if not pdf:
                            pdf = generate_pdf_report(patient, data, summary, label, conf, types)
                        send_files_whatsapp(phone_number=phone, patient_name=patient, pdf_path=pdf, audio_path=audio, report_summary=summary)
                        st.success("WhatsApp workflow launched.")
                    except Exception as e:
                        st.error(f"WhatsApp workflow could not be launched: {e}")
            else:
                st.caption("Enter a WhatsApp number above if you want to use the existing desktop automation workflow.")
            st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------------
# PAGE: PATIENT HISTORY
# ----------------------------------------------------------------------------------
elif selected == "Patient History":
    st.markdown(
        "<div class='hero'><span class='eyebrow'>📋 Longitudinal Monitoring</span>"
        "<h1>Patient History &amp; Trend Analysis</h1>"
        "<p>Track how a patient's laboratory parameters evolve across saved reports over time.</p></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    name = st.text_input("🔍 Search patient", value=st.session_state.get("patient", ""))
    st.markdown("</div>", unsafe_allow_html=True)

    rows = history(name) if name.strip() else []
    if not rows:
        st.info("No saved reports for this patient yet. Analyze a report first.")
    else:
        latest = rows[-1]
        latest_conf_pct = f"{latest['confidence']:.0%}"
        latest_conf_tone = "warn" if latest["confidence"] < .6 else "good"
        st.markdown(
            f"<div class='kpi-row'>"
            f"{kpi_card('Reports stored', len(rows), name, 'acc')}"
            f"{kpi_card('Latest AI pattern', latest['model_label'], latest['report_date'][:10], 'acc')}"
            f"{kpi_card('Latest confidence', latest_conf_pct, 'model ensemble', latest_conf_tone)}"
            f"{kpi_card('Report type', latest['report_type'], 'most recent upload', 'acc')}"
            f"</div>", unsafe_allow_html=True,
        )

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        section_title("🗂️", "Report Timeline")
        hist = pd.DataFrame([{"Date": r["report_date"], "Report": r["report_type"],
                               "AI Pattern": r["model_label"], "Confidence": f"{r['confidence']:.0%}"} for r in rows])
        st.dataframe(hist, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        section_title("📈", "Parameter Trend")
        params = sorted({p["Parameter"] for r in rows for p in json.loads(r["parameters_json"])})
        parameter = st.selectbox("Choose a parameter", params)
        tf = trend_frame(rows, parameter)
        if not tf.empty:
            tf["Date"] = pd.to_datetime(tf["Date"])
            tf = tf.sort_values("Date")
            colors = [COLORS.get(s, "#3fa9ff") for s in tf["Status"]]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=tf["Date"], y=tf["Value"], mode="lines+markers",
                line=dict(color="#3fa9ff", width=2.5),
                marker=dict(size=10, color=colors, line=dict(width=1, color="#0b1424")),
                hovertext=tf["Status"], hoverinfo="x+y+text",
            ))
            fig.update_layout(
                height=340, margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font={"color": "#cfe1f7"},
                xaxis=dict(gridcolor="rgba(255,255,255,.06)"),
                yaxis=dict(title=parameter, gridcolor="rgba(255,255,255,.06)"),
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(tf.reset_index(drop=True), use_container_width=True, hide_index=True)
            if len(tf) >= 2:
                delta = float(tf["Value"].iloc[-1] - tf["Value"].iloc[-2])
                st.info(f"Latest change in {parameter}: {delta:+.3g} from the previous stored report.")
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------------
# PAGE: MODEL EVALUATION
# ----------------------------------------------------------------------------------
elif selected == "Model Evaluation":
    st.markdown(
        "<div class='hero'><span class='eyebrow'>📊 Reproducible Benchmark</span>"
        "<h1>Model Evaluation</h1>"
        "<p>Comparison of the bundled Logistic Regression, SVM and Random Forest ensemble on the academic benchmark.</p></div>",
        unsafe_allow_html=True,
    )

    from ml_engine.ai_engine import train_models
    with st.spinner("Training / loading models…"):
        models, results = train_models()
    df = evaluation_table(results)
    best = df.loc[df["Accuracy"].idxmax()]
    best_acc_str = f"{best['Accuracy']:.1%} accuracy"
    avg_f1_str = f"{df['F1'].mean():.1%}"
    avg_prec_str = f"{df['Precision'].mean():.1%}"
    avg_rec_str = f"{df['Recall'].mean():.1%}"

    st.markdown(
        f"<div class='kpi-row'>"
        f"{kpi_card('Best model', best['Model'], best_acc_str, 'good')}"
        f"{kpi_card('Avg. F1', avg_f1_str, 'across ensemble', 'acc')}"
        f"{kpi_card('Avg. precision', avg_prec_str, 'across ensemble', 'acc')}"
        f"{kpi_card('Avg. recall', avg_rec_str, 'across ensemble', 'acc')}"
        f"</div>", unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1.3, 1])
    with c1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        section_title("📈", "Metric Comparison")
        long_df = df.melt(id_vars="Model", value_vars=["Accuracy", "Precision", "Recall", "F1"],
                           var_name="Metric", value_name="Score")
        fig = px.bar(long_df, x="Model", y="Score", color="Metric", barmode="group",
                     color_discrete_sequence=["#3fa9ff", "#8b5cf6", "#2dd4bf", "#f59e0b"])
        fig.update_layout(
            height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#cfe1f7"}, yaxis=dict(tickformat=".0%", gridcolor="rgba(255,255,255,.06)"),
            xaxis=dict(gridcolor="rgba(255,255,255,.03)"), legend=dict(orientation="h", y=1.12),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        section_title("🗒️", "Metrics Table")
        st.dataframe(
            df.style.format({"Accuracy": "{:.1%}", "Precision": "{:.1%}", "Recall": "{:.1%}", "F1": "{:.1%}"})
              .background_gradient(cmap="Blues", subset=["Accuracy"]),
            use_container_width=True, hide_index=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    section_title("🧩", "Confusion Matrix")
    model_name = st.selectbox("Select model", list(results.keys()))
    cm = results[model_name]["confusion_matrix"]
    classes = results[model_name]["classes"]
    fig = px.imshow(cm, x=classes, y=classes, text_auto=True, color_continuous_scale="Blues",
                     labels=dict(x="Predicted", y="Actual", color="Count"))
    fig.update_layout(height=420, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       font={"color": "#cfe1f7"})
    st.plotly_chart(fig, use_container_width=True)
    st.info("Benchmark note: the bundled training data is synthetically generated to make the project runnable without distributing private patient data. These metrics are software-demo metrics, not clinical performance claims.")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------------
# PAGE: ABOUT
# ----------------------------------------------------------------------------------
elif selected == "About":
    st.markdown(
        "<div class='hero'><span class='eyebrow'>ℹ️ Project Architecture</span>"
        "<h1>About MediScan AI</h1>"
        "<p>Final-year engineering project — explainable, multilingual, longitudinal medical report AI.</p></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    section_title("🎓", "Proposed Contribution")
    st.markdown("**Explainable AI-Based Multilingual Medical Report Understanding and Longitudinal Health Monitoring System.**")
    st.markdown("</div>", unsafe_allow_html=True)

    stages = [
        ("📄", "PDF / Image", "Native text + OCR fallback"),
        ("🔤", "OCR", "PyMuPDF + Tesseract + OpenCV"),
        ("🧾", "NLP Extraction", "Entity & value extraction"),
        ("📏", "Normalization", "Unit / reference-range mapping"),
        ("🧮", "Rule-based Analysis", "Deviation scoring"),
        ("🤖", "ML Ensemble", "LogReg · SVM · Random Forest"),
        ("🔍", "Explainability", "Evidence ranking"),
        ("🗣️", "Summary", "Patient-friendly explanation"),
        ("🌍", "Translation", "6 languages"),
        ("🔊", "TTS", "Regional audio"),
        ("📑", "PDF / WhatsApp", "Export & delivery"),
        ("📈", "History", "Longitudinal trends"),
    ]
    cols = st.columns(4)
    for i, (icon, title, desc) in enumerate(stages):
        with cols[i % 4]:
            st.markdown(
                f"<div class='card' style='min-height:118px'>"
                f"<div style='font-size:1.5rem'>{icon}</div>"
                f"<div style='font-weight:700;margin-top:.3rem'>{title}</div>"
                f"<div style='color:var(--muted);font-size:.82rem;margin-top:.15rem'>{desc}</div></div>",
                unsafe_allow_html=True,
            )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        section_title("🧠", "AI Components")
        st.markdown(
            "- Logistic Regression, SVM and Random Forest ensemble\n"
            "- Feature / deviation representation relative to configured ranges\n"
            "- Model confidence and evidence display\n"
            "- Explainability through parameter contribution / evidence ranking\n"
            "- Longitudinal trend and change analysis"
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        section_title("⚙️", "Engineering Components")
        st.markdown(
            "- Streamlit interface with interactive Plotly visualizations\n"
            "- SQLite patient / report database\n"
            "- PyMuPDF + OpenCV + Tesseract OCR\n"
            "- ReportLab PDF generation\n"
            "- Translation and speech synthesis\n"
            "- Optional existing WhatsApp desktop automation"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.warning("This is an educational software prototype. It does not diagnose disease, prescribe treatment, or replace a qualified clinician. The ML benchmark uses synthetic data and is not clinically validated.")
