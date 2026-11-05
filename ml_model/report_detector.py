def detect_report_type(text):

    text = text.lower()

    report_types = []

    # CBC
    if (
        "hemoglobin" in text
        or "platelet" in text
        or "wbc" in text
        or "rbc" in text
    ):
        report_types.append("cbc")

    # Diabetes
    if (
        "hba1c" in text
        or "glucose" in text
        or "fasting glucose" in text
    ):
        report_types.append("diabetes")

    # Lipid Profile
    if (
        "cholesterol" in text
        or "hdl" in text
        or "ldl" in text
        or "triglycerides" in text
    ):
        report_types.append("lipid")

    # Liver Function
    if (
        "bilirubin" in text
        or "sgot" in text
        or "sgpt" in text
        or "alp" in text
    ):
        report_types.append("lft")

    # Kidney Function
    if (
        "creatinine" in text
        or "urea" in text
        or "egfr" in text
    ):
        report_types.append("kft")

    # Thyroid
    if (
        "tsh" in text
        or "t3" in text
        or "t4" in text
    ):
        report_types.append("thyroid")

    return report_types