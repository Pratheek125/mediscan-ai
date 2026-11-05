import pandas as pd
import re

# Read OCR text
file_path = "outputs/extracted_text/report_text.txt"

with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()

lines = text.split("\n")

# Parameter detection
parameters = {
    "WBC": ["white blood cell", "wbc"],
    "RBC": ["red blood cell", "rbc"],
    "Hemoglobin": ["hemoglobin", "hb/hgb", "hgb"],
    "Hematocrit": ["hematocrit", "hct"],
    "MCV": ["mean cell volume", "mcv"],
    "MCH": ["mean cellhemoglobin", "mch"],
    "MCHC": ["mean cell hb conc", "mchc"],
    "RDW": ["red cell dist width", "rdw"],
    "Platelets": ["platelet count", "platelet"]
}

extracted_data = {}

for line in lines:

    line_lower = line.lower()

    for parameter, keywords in parameters.items():

        for keyword in keywords:

            if keyword in line_lower:

                numbers = re.findall(
                    r"\d+\.\d+|\d+",
                    line
                )

                if numbers:
                    extracted_data[parameter] = float(
                        numbers[0]
                    )

# Load normal ranges
ranges = pd.read_csv(
    "dataset/normal_ranges/cbc_ranges.csv"
)

# Explanations
medical_explanations = {
    "Hemoglobin":
        "Low hemoglobin may indicate anemia or iron deficiency.",

    "WBC":
        "Abnormal WBC may indicate infection or immune system issues.",

    "Platelets":
        "Low platelet count may affect blood clotting.",

    "RBC":
        "Abnormal RBC may indicate anemia or dehydration.",

    "RDW":
        "High RDW may indicate vitamin deficiency.",

    "MCV":
        "Abnormal MCV may indicate blood cell size issues.",

    "MCH":
        "Abnormal MCH may indicate anemia.",

    "MCHC":
        "Abnormal MCHC may indicate blood disorders.",

    "Hematocrit":
        "Abnormal hematocrit may indicate dehydration or anemia."
}

print("\n===== MEDICAL REPORT ANALYSIS =====\n")

for parameter, value in extracted_data.items():

    row = ranges[
        ranges["parameter"] == parameter
    ]

    if not row.empty:

        min_val = row["min"].values[0]
        max_val = row["max"].values[0]

        if value < min_val:
            status = "LOW"

        elif value > max_val:
            status = "HIGH"

        else:
            status = "NORMAL"

        print(
            f"{parameter}: {value} → {status}"
        )

        if status != "NORMAL":
            print(
                medical_explanations.get(
                    parameter,
                    "No explanation available."
                )
            )
            print()