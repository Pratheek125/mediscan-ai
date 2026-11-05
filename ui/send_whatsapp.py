import pywhatkit
from datetime import datetime, timedelta
import time


def send_whatsapp_message(
    phone_number,
    patient_name,
    medical_report
):

    # Schedule 3 minutes ahead
    send_time = datetime.now() + timedelta(minutes=3)

    hour = send_time.hour
    minute = send_time.minute

    message = f"""
Hello {patient_name},

Your medical report has been analyzed.

{medical_report}

Thank you for using
AI Medical Assistant.
"""

    print("Opening WhatsApp Web...")

    pywhatkit.sendwhatmsg(
        phone_no=phone_number,
        message=message,
        time_hour=hour,
        time_min=minute,
        wait_time=30,
        tab_close=False
    )

    print("Message scheduled successfully.")