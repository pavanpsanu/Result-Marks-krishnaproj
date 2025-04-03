import smtplib

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT= 587
SMTP_USER= "npdevandla@gmail.com"
SMTP_PASS= "dkvq pepw msbc apyj"  # Use an App Password

try:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.ehlo()
    server.starttls()  # Secure the connection
    server.login(SMTP_USER, SMTP_PASS)
    print("✅ SMTP Connection Successful!")
    server.quit()
except Exception as e:
    print(f"❌ SMTP Error: {e}")
