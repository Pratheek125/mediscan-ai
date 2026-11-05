import sys
from pathlib import Path

from ocr.engine import extract_text_from_pdf
from parser.medical_parser import parse

if len(sys.argv) != 2:
    print("Usage: python test_real_report.py path_to_report.pdf")
    raise SystemExit(2)

pdf = Path(sys.argv[1])
if not pdf.exists():
    print(f"File not found: {pdf}")
    raise SystemExit(1)

text = extract_text_from_pdf(str(pdf))
data = parse(text)
print(f"Extracted supported parameters: {len(data)}")
for item in data:
    print(f"{item['Parameter']}: {item['Value']} {item['Unit']} [{item['Status']}; {item['Min']}-{item['Max']}]")
if not data:
    raise SystemExit("No supported parameters extracted")
