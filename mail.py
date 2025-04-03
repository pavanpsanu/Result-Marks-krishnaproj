import os
import pandas as pd
import smtplib
import matplotlib.pyplot as plt
from email.message import EmailMessage
from flask import Flask, request, render_template

app = Flask(__name__)

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "npdevandla@gmail.com"  # Use App Password
SMTP_PASS = "dkvq pepw msbc apyj"

UPLOAD_FOLDER = "uploads"
IMAGE_FOLDER = "images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["csvfile"]
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            send_emails(filepath)
            return "Emails with tables and visualizations sent successfully!"
    return render_template("upload.html")

def generate_pie_chart(row):
    """Generates a pie chart of a student's marks and saves it as an image."""
    subjects = ["acd", "dccn", "ml", "bc", "eh", "acd lab", "dccn lab", "ml lab", "mini project"]
    marks = [row[sub] for sub in subjects]

    plt.figure(figsize=(7, 7))
    plt.pie(marks, labels=subjects, autopct='%1.1f%%', startangle=140, 
            colors=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99", "#c2c2f0", 
                    "#ffb3e6", "#c4e17f", "#76d7c4", "#f7c6c7"])
    plt.title(f"Marks Distribution - {row['name']}")

    pie_chart_path = os.path.join(IMAGE_FOLDER, f"{row['rollno']}_pie.png")
    plt.savefig(pie_chart_path)
    plt.close()

    return pie_chart_path

def generate_bar_chart(row):
    """Generates a bar chart of a student's marks and saves it as an image."""
    subjects = ["acd", "dccn", "ml", "bc", "eh", "acd lab", "dccn lab", "ml lab", "mini project"]
    marks = [row[sub] for sub in subjects]

    plt.figure(figsize=(8, 4))
    plt.bar(subjects, marks, color=["blue", "green", "red", "orange", "purple", "brown", "pink", "cyan", "gray"])
    plt.xlabel("Subjects")
    plt.ylabel("Marks")
    plt.title(f"Marks for {row['name']} ({row['rollno']})")
    plt.xticks(rotation=45)

    bar_chart_path = os.path.join(IMAGE_FOLDER, f"{row['rollno']}_bar.png")
    plt.savefig(bar_chart_path)
    plt.close()

    return bar_chart_path

def send_emails(csv_filepath):
    """Reads the CSV file and sends emails with marks details and visualizations."""
    try:
        data = pd.read_csv(csv_filepath)
        data.columns = data.columns.str.strip()

        # Connect to SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)

        for _, row in data.iterrows():
            try:
                to_email = row['email']
                subject = "Your Results"

                # Generate Pie and Bar Charts
                pie_chart_path = generate_pie_chart(row)
                bar_chart_path = generate_bar_chart(row)

                # Email body with table
                body = f"""
                <html>
                <head>
                    <style>
                        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: center; }}
                        th {{ background-color: #007bff; color: white; }}
                        .low-marks {{ background-color: #f8d7da; color: #721c24; }}
                        .high-marks {{ background-color: #d4edda; color: #155724; }}
                    </style>
                </head>
                <body>
                    <p>Dear {row['name']},</p>
                    <p>Your MID {row['mid']} marks are as follows:</p>
                    <p><b>Roll No:</b> {row['rollno']}</p>
                    <p><b>Year/Semester:</b> {row['year/semester']}</p>
                    <p><b>Branch:</b> {row['branch']}</p>
                    
                    <table>
                        <tr><th>Subject</th><th>Marks</th></tr>
                        {generate_table_rows(row)}
                        <tr><td><b>Total</b></td><td><b>{row['total']}/360</b></td></tr>
                    </table>

                    <p><b>Overall Result:</b> {row['overall result']}</p>
                    <p>See the attached Pie Chart & Bar Chart for your subject-wise marks.</p>

                    <p>Best regards,<br>VBIT</p>
                </body>
                </html>
                """

                # Create email
                msg = EmailMessage()
                msg["From"] = SMTP_USER
                msg["To"] = to_email
                msg["Subject"] = subject
                msg.set_content("This email contains an HTML table with attached Pie & Bar charts.")
                msg.add_alternative(body, subtype="html")

                # Attach the Pie Chart
                with open(pie_chart_path, "rb") as pie_img:
                    msg.add_attachment(pie_img.read(), maintype="image", subtype="png", filename=f"{row['rollno']}_pie.png")

                # Attach the Bar Chart
                with open(bar_chart_path, "rb") as bar_img:
                    msg.add_attachment(bar_img.read(), maintype="image", subtype="png", filename=f"{row['rollno']}_bar.png")

                # Send email
                server.send_message(msg)
                print(f"✅ Email sent to {to_email}")

            except Exception as e:
                print(f"❌ Failed to send email to {to_email}: {e}")

        server.quit()
    except Exception as e:
        print(f"❌ Error processing CSV file: {e}")

def generate_table_rows(row):
    """Generates HTML table rows dynamically"""
    subjects = ["acd", "dccn", "ml", "bc", "eh", "acd lab", "dccn lab", "ml lab", "mini project"]
    rows = ""
    for sub in subjects:
        row_class = "low-marks" if row[sub] < 14 else "high-marks"
        rows += f'<tr class="{row_class}"><td>{sub.upper()}</td><td>{row[sub]}</td></tr>'
    return rows

if __name__ == "__main__":
    app.run(debug=True)
