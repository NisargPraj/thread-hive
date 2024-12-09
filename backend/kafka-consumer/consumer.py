from kafka import KafkaConsumer
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import time

def send_email_with_attachment(sender_email, sender_password, recipient_email, subject, message):
    try:
        # Set up the SMTP server
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587

        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        # Attach the file

        # Connect to the SMTP server and log in
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, recipient_email, msg.as_string())
        print("Email sent successfully!")

        # Close the server connection
        server.quit()

    except Exception as e:
        print(f"An error occurred: {e}")


consumer = KafkaConsumer(
    'user_signup',
    bootstrap_servers='kafka:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    group_id='email_service_group'
)

for message in consumer:
    user_data = message.value
    recipient_email = user_data['email']
    subject = "Welcome to Our Platform!"
    message = f"Hi {user_data['first_name']},\n\nWelcome to our platform. We're excited to have you!"
    
    # Send the email
    send_email_with_attachment(
        sender_email="", #Add email
        sender_password="", # Add password
        recipient_email=recipient_email,
        subject=subject,
        message=message 
    )