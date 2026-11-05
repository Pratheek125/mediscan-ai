from parser.medical_parser import parse
from ml_engine.ai_engine import predict
from ml_engine.explainability import explanation_lines
from ml_model.report_detector import detect_report_type

def analyze(text):
    data=parse(text)
    label,conf,per_model,results=predict(data)
    evidence=explanation_lines(data,label)
    abnormal=[d for d in data if d["Status"]!="NORMAL"]
    if abnormal:
        intro=f"The AI system identified {len(abnormal)} parameter(s) outside the reference intervals extracted/configured for this report."
    else: intro="All extracted parameters were within the reference intervals extracted/configured for this report."
    summary=intro+f"\n\nML ensemble pattern: {label} (model confidence {conf:.0%}).\n\n"+"\n".join("• "+e for e in evidence)
    summary += "\n\nThis is an informational AI-assisted interpretation, not a diagnosis. Results should be reviewed with a qualified healthcare professional."
    return summary,data,detect_report_type(text),label,conf,per_model,results
