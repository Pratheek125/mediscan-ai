import pandas as pd
import re

from ml_model.report_detector import (
    detect_report_type
)

# --------------------------
# MEDICAL KNOWLEDGE
# --------------------------

medical_knowledge = {

    "Hemoglobin": {
        "cause":
            "may indicate anemia or iron deficiency",

        "symptoms":
            "fatigue, weakness, pale skin",

        "doctor":
            "consult a physician if symptoms persist",

        "food":
            "iron-rich foods such as spinach, lentils and red meat"
    },

    "WBC": {
        "cause":
            "may indicate infection or inflammation",

        "symptoms":
            "fever, tiredness or body pain",

        "doctor":
            "consult a physician if symptoms continue",

        "food":
            "vitamin C rich foods and hydration"
    },

    "Platelets": {
        "cause":
            "may affect blood clotting",

        "symptoms":
            "easy bruising or bleeding",

        "doctor":
            "avoid injury and consult a physician",

        "food":
            "papaya leaf extract and leafy vegetables"
    },

    "HbA1c": {
        "cause":
            "may indicate poor blood sugar control",

        "symptoms":
            "fatigue, thirst or frequent urination",

        "doctor":
            "consult a doctor for diabetes management",

        "food":
            "low sugar and high fiber foods"
    },

    "Fasting Glucose": {
        "cause":
            "may indicate elevated diabetes risk",

        "symptoms":
            "excessive thirst or tiredness",

        "doctor":
            "monitor sugar levels regularly",

        "food":
            "fiber rich vegetables and healthy meals"
    },

    "Total Cholesterol": {
        "cause":
            "may increase cardiovascular risk",

        "symptoms":
            "often no visible symptoms",

        "doctor":
            "consider lifestyle modification",

        "food":
            "oats, nuts and healthy fats"
    },

    "HDL": {
        "cause":
            "may indicate lower protective cholesterol",

        "symptoms":
            "usually asymptomatic",

        "doctor":
            "increase physical activity",

        "food":
            "fish, olive oil and nuts"
    },

    "LDL": {
        "cause":
            "may indicate higher bad cholesterol",

        "symptoms":
            "usually asymptomatic",

        "doctor":
            "reduce processed foods",

        "food":
            "fiber-rich foods"
    },

    "Creatinine": {
        "cause":
            "may indicate kidney function changes",

        "symptoms":
            "swelling or fatigue",

        "doctor":
            "consult nephrologist if elevated",

        "food":
            "low sodium foods and hydration"
    },

    "TSH": {
        "cause":
            "may indicate thyroid imbalance",

        "symptoms":
            "weight change or tiredness",

        "doctor":
            "consult endocrinologist",

        "food":
            "iodine rich foods"
    }
}


# --------------------------
# SEVERITY
# --------------------------

def get_severity(
    value,
    min_val,
    max_val
):

    if min_val <= value <= max_val:
        return (
            "🟢 NORMAL",
            "normal"
        )

    if value < min_val:

        difference = (
            (min_val - value)
            / min_val
        ) * 100

        if difference > 40:
            return (
                "🔴 CRITICAL LOW",
                "critical"
            )

        elif difference > 20:
            return (
                "🟠 MODERATE LOW",
                "moderate"
            )

        return (
            "🟡 MILD LOW",
            "mild"
        )

    difference = (
        (value - max_val)
        / max_val
    ) * 100

    if difference > 40:
        return (
            "🔴 CRITICAL HIGH",
            "critical"
        )

    elif difference > 20:
        return (
            "🟠 MODERATE HIGH",
            "moderate"
        )

    return (
        "🟡 MILD HIGH",
        "mild"
    )


# --------------------------
# MAIN ANALYZER
# --------------------------

def analyze_report(text):

    report_types = (
        detect_report_type(text)
    )

    summary = ""

    extracted_data = []

    for report_type in report_types:

        csv_path = (
            f"dataset/normal_ranges/"
            f"{report_type}_ranges.csv"
        )

        ranges = pd.read_csv(
            csv_path
        )

        for _, row in (
            ranges.iterrows()
        ):

            parameter = (
                row["parameter"]
            )

            min_val = (
                row["min"]
            )

            max_val = (
                row["max"]
            )

            pattern = (
                rf"{parameter}"
                rf".*?(\d+\.?\d*)"
            )

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                value = float(
                    match.group(1)
                )

                severity, risk = (
                    get_severity(
                        value,
                        min_val,
                        max_val
                    )
                )

                extracted_data.append(
                    {
                        "Parameter":
                            parameter,
                        "Value":
                            value,
                        "Min":
                            min_val,
                        "Max":
                            max_val,
                        "Status":
                            severity
                    }
                )

                # --------------------------
                # HUMAN-LIKE SUMMARY
                # --------------------------

                if (
                    risk == "normal"
                ):

                    summary += (
                        f"Your "
                        f"{parameter} level "
                        f"appears normal "
                        f"({value}), which "
                        f"is within the "
                        f"healthy range.\n\n"
                    )

                else:

                    info = (
                        medical_knowledge
                        .get(
                            parameter,
                            {}
                        )
                    )

                    summary += (
                        f"Your "
                        f"{parameter} level "
                        f"is {severity.lower()} "
                        f"({value}), which "
                        f"{info.get('cause','may require attention')}.\n"
                    )

                    summary += (
                        f"You may experience "
                        f"{info.get('symptoms','some symptoms')}.\n"
                    )

                    summary += (
                        f"It is recommended "
                        f"to {info.get('doctor','consult a doctor')}.\n"
                    )

                    summary += (
                        f"Suggested diet: "
                        f"{info.get('food','healthy foods')}.\n\n"
                    )

    return (
        summary,
        extracted_data
    )