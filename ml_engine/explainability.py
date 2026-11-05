from .ai_engine import explain

def explanation_lines(extracted,label):
    top=explain(extracted,label)
    if not top: return ["No strongly deviating parameters were detected in the ML feature representation."]
    lines=[]
    for p,mag,signed in top:
        direction="below" if signed<0 else "above"
        lines.append(f"{p}: {direction} its configured reference interval (relative deviation {mag:.2f}).")
    return lines
