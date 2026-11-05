import pandas as pd
import re

# Read OCR extracted text
file_path = "outputs/extracted_text/report_text.txt"

with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()

# Load normal ranges
ranges = pd.read_csv("dataset/normal_ranges/cbc_ranges.csv")

# Patterns for extraction
patterns = {
    "Hemoglobin": r"(Hemoglobin|Hb)\s*[:\-]?\s*(\d+\.?\d*)",
    "WBC": r"(WBC|White Blood Cell|WBC Count)\s*[:\-]?\s*(\d+\.?\d*)",
    "RBC": r"(RBC|Red Blood Cell)\s*[:\-]?\s*(\d+\.?\d*)",
    "Platelets": r"(Platelet|Platelets)\s*[:\-]?\s*(\d+\.?\d*)",
    "RDW": r"(RDW)\s*[:\-]?\s*(\d+\.?\d*)",
    "MCV": r"(MCV)\s*[:\-]?\s*(\d+\.?\d*)",
    "MCH": r"(MCH)\s*[:\-]?\s*(\d+\.?\d*)",
    "MCHC": r"(MCHC)\s*[:\-]?\s*(\d+\.?\d*)",
}

extracted_data = {}

# Extract values
for parameter, pattern in patterns.items():
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        extracted_data[parameter] = float(match.group(2))

print("\n===== REPORT ANALYSIS =====\n")

# Compare with normal ranges
for parameter, value in extracted_data.items():

    row = ranges[ranges["parameter"] == parameter]

    if not row.empty:

        min_val = row["min"].values[0]
        max_val = row["max"].values[0]

        if value < min_val:
            status = "LOW"

        elif value > max_val:
            status = "HIGH"

        else:
            status = "NORMAL"

        print(f"{parameter}: {value} → {status}")