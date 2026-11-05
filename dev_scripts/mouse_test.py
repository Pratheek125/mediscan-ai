import pyautogui
import time

print("Starting in 5 seconds...")
time.sleep(5)

pyautogui.moveTo(393, 164, duration=1)
pyautogui.click()

print("Clicked search area")