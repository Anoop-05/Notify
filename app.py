from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import threading
import time

app = Flask(__name__)

# --- MYSQL DATABASE CONFIGURATION ---
# Format: mysql+pymysql://username:password@hostname:port/database_name
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:0000@localhost:3306/test_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- DATABASE MODELS ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    password = db.Column(db.String(100), nullable=False) # Plain text for now
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

class NotificationLog(db.Model):
    __tablename__ = 'notification_logs'
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(100), nullable=False)
    recipient_email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    scheduled_for = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="Scheduled") # Scheduled, Sent, Failed


FUNNY_MESSAGES = [
    "Hey {name}, you're now officially registered! 🚀",
    "Welcome aboard, {name}! Time to shine! 🌟",
    "Yayy! {name}, your registration is successful! 🎉",
    "🎉 Welcome aboard {name}! Now you're officially awesome! 😎",
    "🚀 Congrats {name}! You've just unlocked Level 1 of 'Being Cool'! 🔥",
    "🥳 You did it {name}! The internet just got a little bit better because of you! 😂",
    "🔥 Boom! {name} Registration complete. Now go grab a coffee, you deserve it! ☕",
    "🎊 Mission accomplished {name}! But wait, where’s my cake? 🍰",
    "😜 You're in {name}! But don’t tell anyone, it's our little secret! 🤫"
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/schedule")
def schedule():
    return render_template("schedule.html")

@app.route("/send-sms", methods=["POST"])
def send_sms():
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        date_of_birth = data.get("dob")
        gender = data.get("gender")
        address = data.get("address")
        password = data.get("password")

        # 1. Check if user already exists in MySQL
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"message": "Email already registered!"}), 400

        # 2. Save new registration to MySQL
        new_user = User(
            name=name, email=email, phone=phone, 
            dob=date_of_birth, gender=gender, 
            address=address, password=password
        )
        db.session.add(new_user)
        db.session.commit()

        # 3. Generate content and fire email dispatch
        message_text = random.choice(FUNNY_MESSAGES).format(name=name) + f"\nYour Details:\n" \
                        f"Name: {name}\nEmail: {email}\nPhone: {phone}\n" \
                        f"Date of Birth: {date_of_birth}\nGender: {gender}\nAddress: {address}"

        send_email(email, "Registration Successful", message_text)
        
        # FIXED: Returning the exact string your frontend Javascript expects to clear the visual error
        return jsonify({"message": "Registration successful!"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Registration Error: {e}")
        return jsonify({"message": "Error processing registration!"}), 500

@app.route("/schedule-notification", methods=["POST"])
def schedule_notification():
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        dateTime = data.get("dateTime")
        message = data.get("message")

        if not name or not email or not dateTime or not message:
            return jsonify({"message": "All fields are required!"}), 400

        schedule_time = datetime.strptime(dateTime, "%Y-%m-%dT%H:%M")

        # Log scheduled event inside MySQL 
        new_log = NotificationLog(
            sender_name=name, 
            recipient_email=email, 
            message=message, 
            scheduled_for=schedule_time
        )
        db.session.add(new_log)
        db.session.commit()

        # Spawn asynchronous worker thread using the saved log ID reference
        threading.Thread(target=schedule_email, args=(new_log.id, name, email, message, schedule_time)).start()

        return jsonify({"message": "Notification scheduled successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Scheduling Error: {e}")
        return jsonify({"message": "Error scheduling notification!"}), 500

def schedule_email(log_id, name, email, message, schedule_time):
    time_diff = (schedule_time - datetime.now()).total_seconds()
    if time_diff > 0:
        time.sleep(time_diff)
    
    subject = f"Reminder: {name}"
    email_sent = send_email(email, subject, message)
    
    # Update execution log history inside database context
    with app.app_context():
        log_entry = NotificationLog.query.get(log_id)
        if log_entry:
            log_entry.status = "Sent" if email_sent else "Failed"
            db.session.commit()

def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = "notibot05@gmail.com"
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("notibot05@gmail.com", "azno ahfa lmoh jebs") 
            server.sendmail(msg['From'], msg['To'], msg.as_string())
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

if __name__ == "__main__":
    # Automatically establishes database tables inside notify_db on startup
    with app.app_context():
        db.create_all()
        
    app.run(debug=True)