# MediScan AI — Final-Year Project Edition

## Title
**Explainable AI-Based Multilingual Medical Report Understanding and Longitudinal Health Monitoring System**

## UI upgrade
The Streamlit dashboard (`ui/app.py`) was redesigned with a modern glass-card layout,
KPI tiles, tabbed results (Parameters / AI Insights / Translate & Voice / Report & Share),
color-coded status badges, an interactive Plotly confidence gauge, a deviation bar chart,
a status donut chart, an animated multi-step analysis progress indicator, and richer
Patient History / Model Evaluation pages (trend line chart, grouped metric comparison,
confusion-matrix heatmap). No backend logic, data formats, or file layouts were changed —
only the presentation layer.

## What was added
- Native-text + OCR PDF pipeline
- Medical parameter normalization and reference-range analysis
- ML ensemble: Logistic Regression, SVM, Random Forest
- Model confidence and evidence-based explanation
- Synthetic academic benchmark + reproducible evaluation page
- SQLite patient history
- Longitudinal trend graphs
- Translation to English, Kannada, Hindi, Tamil, Telugu and Malayalam
- Language-specific TTS
- Downloadable PDF report
- Existing optional WhatsApp desktop workflow
- Streamlit dashboard and safety notices

## Important academic note
The included ML training set is **synthetically generated** so the project runs without private patient data. Its metrics are demonstrations of the software pipeline, not clinical validation. Do not claim the model diagnoses disease.

## Windows setup
1. Install Python 3.10 or 3.11.
2. Install Tesseract OCR. The application uses `pytesseract`; if Tesseract is not on PATH, configure `pytesseract.pytesseract.tesseract_cmd` in `ocr/engine.py`.
3. Run `run_app.bat`, or manually:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run ui\app.py
```

## Demo flow
1. Open **Upload & Analyze**.
2. Enter any patient name.
3. Upload a medical PDF.
4. Click **Analyze Report**.
5. Inspect extracted values, AI pattern, confidence and evidence.
6. Generate translations/audio/PDF as required.
7. Open **Patient History** and select a parameter to show longitudinal trends.
8. Open **Model Evaluation** to demonstrate model comparison and confusion matrices.

## Project defense points
The core engineering contribution is the integration of OCR/NLP, normalized laboratory features, ensemble ML, explainability, longitudinal analytics and multilingual accessibility into one reproducible application.

## Real-report parser fix

The parser now supports native laboratory PDFs whose table columns are returned by PyMuPDF on separate lines. The OCR layer reconstructs table rows from PDF coordinates before NLP parsing. This prevents false "No supported parameters" messages for text-based reports and preserves the report's own numeric reference intervals when available.

A local regression test can be run with:

```bash
python test_real_report.py "path\\to\\report.pdf"
```

## WhatsApp test scripts
`test_whatsapp.py` and `test_whatsapp_attachment.py` read the recipient from the `TEST_PHONE`
environment variable. If WhatsApp Desktop is not installed in the default location, set `WHATSAPP_PATH`.

## Disclaimer
This is an academic project. It is not a medical device and must not be used for diagnosis or treatment decisions.
