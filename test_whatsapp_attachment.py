import os
from ui.send_whatsapp_attachment import (
    send_files_whatsapp
)

summary = """
Platelets → LOW
Low platelet count may affect blood clotting.

MCHC → HIGH
Abnormal MCHC may indicate blood disorders.
"""

send_files_whatsapp(
    phone_number=os.environ.get("TEST_PHONE", "+910000000000"),
    patient_name="Demo Patient",
    pdf_path=r"reports/pdf/cbc_report.pdf",
    audio_path=r"outputs/audio/Kannada_Report.mp3",
    report_summary=summary
)