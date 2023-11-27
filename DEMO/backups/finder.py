import http.client as http
from datetime import datetime, timedelta
import time
import smtplib, ssl

IP = "192.168.50.119"
# sms_gateway = "tmomail.net"
NUMBER = "14079283958@tmomail.net"
# NUMBER = "14076860266@tmomail.net"
def check():
    conn = http.HTTPConnection(IP, timeout=3)
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

def send_message():
    print("SENDING")
    SMTP_SERVER, SMTP_PORT = "smtp.gmail.com", 465
    sender_email, email_password = ("austinstodolist@gmail.com", "N98M28Pea52mD*d#")

    email_message = f"Subject:Hunter is safely home!\nTo:{NUMBER}\nAlso, Austin loves you more!"
    with smtplib.SMTP_SSL(
        SMTP_SERVER, SMTP_PORT, context=ssl.create_default_context()
    ) as email:
        email.login(sender_email, email_password)
        email.sendmail(sender_email, NUMBER, email_message)
    print("SENT")



def main():
    now = datetime.utcnow() - timedelta(hours=5)
    delta = timedelta(days=now.day, hours=15, minutes=20)
    date = delta - timedelta(days=now.day, hours=now.hour, minutes=now.minute)
    if date.total_seconds() > 0:
        print(f"Sleeping for {date}, seconds: {date.total_seconds()}")
        time.sleep(date.total_seconds())
    else:
        now = datetime.utcnow() - timedelta(hours=5)
        delta = timedelta(days=now.day+1, hours=15, minutes=20)
        date = delta - timedelta(days=now.day, hours=now.hour, minutes=now.minute)
        print(f"Sleeping for {date}, seconds: {date.total_seconds()}")
        time.sleep(date.total_seconds())
    while True:
        if check():
            send_message()
            now = datetime.utcnow() - timedelta(hours=5)
            delta = timedelta(days=now.day+1, hours=15, minutes=20)
            date = delta - timedelta(days=now.day, hours=now.hour, minutes=now.minute)
            print(f"Sleeping for {date}, seconds: {date.total_seconds()}")
            time.sleep(date.total_seconds())
        else:
            time.sleep(15)



if __name__ == "__main__":
    main()

