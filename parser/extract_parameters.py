import re

# Read OCR text
file_path = "outputs/extracted_text/report_text.txt"

with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()

# Split into lines
lines = text.split("\n")

# Keywords to detect
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

    line_lower = line.lower().strip()

    for parameter, keywords in parameters.items():

        for keyword in keywords:

            if keyword in line_lower:

                # Find all numbers in line
                numbers = re.findall(r"\d+\.\d+|\d+", line)

                # Ignore obvious reference range values
                filtered = []

                for num in numbers:
                    value = float(num)

                    # Ignore large reference ranges
                    if parameter == "WBC" and value > 20:
                        continue

                    if parameter == "Hemoglobin" and value > 25:
                        continue

                    if parameter == "Platelets" and value > 500:
                        continue

                    filtered.append(value)

                # Use first sensible value
                if filtered:
                    extracted_data[parameter] = filtered[0]

# Print results
print("\n===== EXTRACTED MEDICAL PARAMETERS =====\n")

for key, value in extracted_data.items():
    print(f"{key}: {value}")