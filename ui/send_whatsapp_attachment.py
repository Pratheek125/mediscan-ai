import pyautogui
import pyperclip
import time
import os
import subprocess


# --------------------------
# OPEN WHATSAPP DESKTOP
# --------------------------

def open_whatsapp():

    whatsapp_path = os.environ.get(
        "WHATSAPP_PATH",
        os.path.join(
            os.environ.get("LOCALAPPDATA", ""), "WhatsApp", "WhatsApp.exe"
        ),
    )

    print(
        "Opening WhatsApp Desktop..."
    )

    try:

        subprocess.Popen(
            [whatsapp_path]
        )

    except Exception as e:

        print(
            f"Failed to open WhatsApp: {e}"
        )

        return False

    # Wait for WhatsApp to load
    time.sleep(20)

    # Focus window
    pyautogui.click(
        700,
        500
    )

    time.sleep(2)

    return True


# --------------------------
# ATTACH FILE
# --------------------------

def attach_file(
    file_path
):

    absolute_path = os.path.abspath(
        file_path
    )

    print(
        f"Attaching:\n{absolute_path}"
    )

    time.sleep(3)

    # Paste path
    pyperclip.copy(
        absolute_path
    )

    pyautogui.hotkey(
        "ctrl",
        "v"
    )

    time.sleep(2)

    pyautogui.press(
        "enter"
    )

    print(
        "Path entered."
    )

    # Wait preview
    time.sleep(7)

    # Send attachment
    pyautogui.press(
        "enter"
    )

    print(
        "Attachment sent."
    )

    time.sleep(5)


# --------------------------
# MAIN FUNCTION
# --------------------------

def send_files_whatsapp(
    phone_number,
    patient_name,
    pdf_path,
    audio_path,
    report_summary
):

    print(
        "Starting WhatsApp automation..."
    )

    opened = open_whatsapp()

    if not opened:
        return

    # ==================================================
    # SEARCH CONTACT
    # ==================================================

    print(
        "Searching contact..."
    )

    # Click search bar
    pyautogui.click(
        309,
        165
    )

    time.sleep(2)

    # Clear previous search
    pyautogui.hotkey(
        "ctrl",
        "a"
    )

    time.sleep(1)

    pyautogui.press(
        "backspace"
    )

    time.sleep(1)

    # Paste number
    pyperclip.copy(
        phone_number
    )

    pyautogui.hotkey(
        "ctrl",
        "v"
    )

    print(
        f"Searching: {phone_number}"
    )

    time.sleep(4)

    # Open first result
    pyautogui.press(
        "enter"
    )

    print(
        "Opening chat..."
    )

    time.sleep(5)

    # ==================================================
    # SEND PDF
    # ==================================================

    print(
        "Sending PDF..."
    )

    # Attach button
    pyautogui.click(
        476,
        963
    )

    time.sleep(3)

    # Document
    pyautogui.click(
        497,
        622
    )

    time.sleep(5)

    attach_file(
        pdf_path
    )

    # ==================================================
    # SEND AUDIO
    # ==================================================

    print(
        "Sending audio..."
    )

    pyautogui.click(
        476,
        963
    )

    time.sleep(3)

    # Audio
    pyautogui.click(
        484,
        722
    )

    time.sleep(5)

    attach_file(
        audio_path
    )

    # ==================================================
    # SEND SUMMARY
    # ==================================================

    print(
        "Sending summary..."
    )

    message = f"""
Hello {patient_name},

Your medical report has been analyzed.

Summary:
{report_summary[:800]}

The AI medical report PDF and
regional language audio explanation
have been attached.

Thank you for using
AI Medical Assistant.
"""

    pyperclip.copy(
        message
    )

    pyautogui.hotkey(
        "ctrl",
        "v"
    )

    time.sleep(2)

    pyautogui.press(
        "enter"
    )

    print(
        "Everything sent successfully!"
    )