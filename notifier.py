import os
import time

NOTIF_FILE = "notifications.txt"
LAST_NOTIF_FILE = "last_notif.txt"

def setNotification(notif):
    os.environ["DBUS_SESSION_BUS_ADDRESS"] = "unix:path=/run/user/1000/bus"
    os.system(f"notify-send 'Assist' '{notif}'")

def read_notifications():
    if os.path.exists(NOTIF_FILE):
        with open(NOTIF_FILE, "r") as file:
            return file.read().strip()
    return ""

def get_last_notification():
    if os.path.exists(LAST_NOTIF_FILE):
        with open(LAST_NOTIF_FILE, "r") as file:
            return file.read().strip()
    return ""

def save_last_notification(notif):
    with open(LAST_NOTIF_FILE, "w") as file:
        file.write(notif)

def check_for_new_notifications():
    new_notif = read_notifications()
    last_notif = get_last_notification()

    if new_notif and new_notif != last_notif:
        setNotification(new_notif)
        save_last_notification(new_notif)

if __name__ == "__main__":
    while True:
        check_for_new_notifications()
        time.sleep(1)  # Check every 5 seconds
