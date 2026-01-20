import sqlite3
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash
from flask import url_for, redirect

def send_email(
    to_email,
    subject,
    body,
    from_email="jay451428@gmail.com",
    from_password="xpya nqal apnd jxqe",  # Use environment variables in production!
):
    """Send email using Gmail SMTP"""
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Email sending failed:", e)  # Log in production


def generate_username(fname, lname):
    """Generate username from first and last name"""
    return f"{fname.lower()}.{lname.lower()}{random.randint(100, 999)}"