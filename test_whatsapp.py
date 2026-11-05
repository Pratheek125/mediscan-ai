import os
from ui.send_whatsapp import send_whatsapp_message

report = """
Platelets → LOW
MCHC → HIGH

Low platelet count may affect blood clotting.
"""

send_whatsapp_message(
    phone_number=os.environ.get("TEST_PHONE", "+910000000000"),
    patient_name="Demo Patient",
    medical_report=report
)