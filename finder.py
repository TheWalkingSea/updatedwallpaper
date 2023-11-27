import http.client as http
from datetime import datetime, timedelta
import time
import ssl
import smtplib

IP = "192.168.50.63"
IP2= "192.168.50.53"
# sms_gateway = "tmomail.net"
NUMBER = "14079283958@tmomail.net"
NUMBER2 = "14077668937@tmomail.net"
# NUMBER = "14076860266@tmomail.net"
def check(ip):
    conn = http.HTTPConnection(ip, timeout=3)
    try:
        conn.request("HEAD", "/") # Connect
        print("TRUE")
        return True
    except ConnectionRefusedError:
        print("TRUE")
        return True
    except:
        print("FALSE")
        return False
    finally:
        conn.close()

def send_message(number):
    print("SENDING")
    if number == "192.168.50.63": number = "Hunter"
    elif number == "192.168.50.53": number = "Austin"
    SMTP_SERVER, SMTP_PORT = "smtp.gmail.com", 587
#     sender_email, email_password = ("austinscodeautomated@outlook.com", "N98M28Pea52mD*d#")
    sender_email, email_password = ("austinscodeautomated@gmail.com", "isfaeznyelcrwcrk")
    email_message = f"Subject:{number} is safely home!\nTo:{NUMBER}\nAlso, Austin loves you more!"
    with smtplib.SMTP(
        SMTP_SERVER, SMTP_PORT
    ) as email:
        email.ehlo()
        email.starttls(context=ssl.create_default_context())
        email.ehlo()
        email.login(sender_email, email_password)
        email.sendmail(sender_email, NUMBER, email_message)

    with smtplib.SMTP(
        SMTP_SERVER, SMTP_PORT
    ) as email:
        email.ehlo()
        email.starttls(context=ssl.create_default_context())
        email.ehlo()
        email.login(sender_email, email_password)
        email.sendmail(sender_email, NUMBER2, email_message)
    print("SENT")



def main(hr, min, ip):
    now = datetime.utcnow() - timedelta(hours=5)
    delta = timedelta(days=now.day, hours=hr, minutes=min)
    date = delta - timedelta(days=now.day, hours=now.hour, minutes=now.minute)
    if date.total_seconds() > 0:
        print(f"Sleeping for {date}, seconds: {date.total_seconds()}")
        time.sleep(date.total_seconds())
    else:
        now = datetime.utcnow() - timedelta(hours=5)
        delta = timedelta(days=now.day+1, hours=hr, minutes=min)
        date = delta - timedelta(days=now.day, hours=now.hour, minutes=now.minute)
        print(f"Sleeping for {date}, seconds: {date.total_seconds()}")
        time.sleep(date.total_seconds())
    while True:
        if check(ip):
            send_message(ip)
            now = datetime.utcnow() - timedelta(hours=5)
            delta = timedelta(days=now.day+1, hours=hr, minutes=min)
            date = delta - timedelta(days=now.day, hours=now.hour, minutes=now.minute)
            print(f"Sleeping for {date}, seconds: {date.total_seconds()}")
            time.sleep(date.total_seconds())
        else:
            time.sleep(15)

from threading import Thread

if __name__ == "__main__":
    send_message(IP)
    # threads = [Thread(target=main, args=(15, 25, IP)), Thread(target=main, args=(13, 25, IP2))]
    # for thread in threads:
    #     thread.start()
