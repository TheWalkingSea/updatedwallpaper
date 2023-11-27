import requests
import json
import time
import smtplib
import ssl

IP = "http://192.168.50.237:4000/updatewallpaper"
NUMBER = "14076860266@tmomail.net"
TOKEN = "1124~qOyLYOXZ1K64MQJhcbY4mO7W7ifLLidRv4A5s2K82xhXGGMVcm9f9oV2Kv4AueYC"
def main():
    print("STARTED")
    payload = {"access_token": TOKEN}
    req = requests.get('https://pasco.instructure.com/api/v1/users/self/todo_item_count', params=payload)
    req = req.json()
    itemsneeded = req['assignments_needing_submitting']
    while True:
        time.sleep(10)
        payload = {"access_token": TOKEN}
        req = requests.get('https://pasco.instructure.com/api/v1/users/self/todo_item_count', params=payload)
        req = req.json()
        if req['assignments_needing_submitting'] != itemsneeded:
            itemsneeded = req['assignments_needing_submitting']
            send_message()
            requests.get(IP)

def send_message():
    print("SENDING")
    SMTP_SERVER, SMTP_PORT = "smtp.gmail.com", 465
    sender_email, email_password = ("austinstodolist@gmail.com", "N98M28Pea52mD*d#")

    email_message = f"Subject:Assignment Complete\nTo:{NUMBER}\nPlease update wallpaper"
    with smtplib.SMTP_SSL(
        SMTP_SERVER, SMTP_PORT, context=ssl.create_default_context()
    ) as email:
        email.login(sender_email, email_password)
        email.sendmail(sender_email, NUMBER, email_message)
    print("SENT")




if __name__ == "__main__":
    main()