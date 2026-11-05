from reportlab.platypus import SimpleDocTemplate,Spacer,Paragraph,Table,TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from pathlib import Path
from datetime import datetime

def generate_pdf_report(patient_name,extracted_data,report_summary,model_label="N/A",confidence=0,report_types=None):
    root=Path(__file__).resolve().parents[1]; out=root/"outputs"/"reports"; out.mkdir(parents=True,exist_ok=True)
    path=out/f"MediScan_AI_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc=SimpleDocTemplate(str(path),rightMargin=36,leftMargin=36,topMargin=36,bottomMargin=36); styles=getSampleStyleSheet(); story=[]
    story += [Paragraph("MediScan AI — AI-Assisted Medical Report",styles["Title"]),Spacer(1,10),Paragraph(f"<b>Patient:</b> {patient_name}<br/><b>Date:</b> {datetime.now():%d-%m-%Y %H:%M}<br/><b>Report type:</b> {', '.join(report_types or ['Unknown'])}<br/><b>AI pattern:</b> {model_label}<br/><b>Model confidence:</b> {confidence:.0%}",styles["BodyText"]),Spacer(1,14)]
    data=[["Parameter","Value","Unit","Range","Status","Severity"]]+[[x["Parameter"],str(x["Value"]),x["Unit"],f"{x['Min']}–{x['Max']}",x["Status"],x["Severity"]] for x in extracted_data]
    t=Table(data,repeatRows=1); t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.lightblue),("GRID",(0,0),(-1,-1),.5,colors.grey),("VALIGN",(0,0),(-1,-1),"TOP")])); story += [Paragraph("Extracted Parameters",styles["Heading2"]),t,Spacer(1,14),Paragraph("AI Explanation",styles["Heading2"]),Paragraph(report_summary.replace("\n","<br/>"),styles["BodyText"]),Spacer(1,14),Paragraph("<b>Safety notice:</b> This educational report is not a diagnosis or treatment recommendation. The included ML benchmark uses synthetic data and is not clinically validated. Review results with a qualified healthcare professional.",styles["Italic"])]
    doc.build(story); return str(path)
