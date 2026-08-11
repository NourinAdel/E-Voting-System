from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from database import db
from dotenv import load_dotenv
import models
from models import User
import os
from itsdangerous import URLSafeTimedSerializer
from email_services import send_email
from datetime import datetime, date

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY')
if not app.secret_key:
    raise ValueError("No SECRET_KEY set")

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/e_voting_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def Login():
    if request.method == "POST":
        data = request.get_json()
        username = data.get('username')
        plain_pass = data.get('password')

        user = User.query.filter_by(username=username).first() 
        if user and user.password == plain_pass:
            if user.role == "Admin":
                return jsonify({
                    "status": "success",
                    "redirect_url": "/adminDashboard.html"
                })
            else:
                return jsonify({
                    "status": "success",
                    "redirect_url": "/userDashboard.html" # TO-DO: replace this later if it's different
                })

        else:
            return jsonify({
                "status": "error",
                "message": "Please check your login details and try again."
            })
    else:
        return render_template('login.html')

@app.route('/resetRequest.html', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')

        # Check if email exists in User table.
        user = User.query.filter_by(email=email).first()
        if user:

            # Create serializer using secret key.
            serializer = URLSafeTimedSerializer(app.secret_key)
            
            salt = os.environ.get('SECURITY_PASSWORD_SALT')
            # Generate token and mix in the salt for password.
            token = serializer.dumps(email, salt = salt)
            reset_url = f"http://127.0.0.1:5000/reset_password/{token}"

            sender_email = os.environ.get('MAIL_USERNAME')
            password = os.environ.get('MAIL_PASSWORD')
            receiver_email = email
            subject = "E-Voting System: Password Reset Request"
            body = f"Please click the link below to reset your password:\n\n{reset_url}\n\nIf you did not request this, please ignore this email."
            email_sent = send_email(sender_email, receiver_email, password, subject, body)
            
            if not email_sent:
                print("Failed to send email. Check your SMTP credentials.")

        flash("If an account exists, a password reset link has been sent.", "info")
        
    return render_template('resetRequest.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    # Initialize the serializer again.
    serializer = URLSafeTimedSerializer(app.secret_key)
    
    try:
        salt = os.environ.get('SECURITY_PASSWORD_SALT')
        # Try to decode the token. 
        # max_age=3600 means the token expires after 1 hour (3600 seconds).
        email = serializer.loads(token, salt=salt, max_age=3600)
    except:
        # If the token is expired, tampered with, or invalid, stop possible attack.
        flash("The reset link is invalid or has expired.", "error")
        return redirect(url_for('forgot_password'))
    
    # Token is valid.
    if request.method == 'POST':
        # TO-DO: Add the database update and password hashing logic here
        pass
        
    # Render the HTML form
    return render_template('resetPassword.html')

@app.route('/Signup.html', methods=['GET', 'POST'])
def signup():
    return render_template('Signup.html')

@app.route('/adminDashboard.html', methods=['GET', 'POST'])
def admin():
    return render_template('adminDashboard.html')
def calculate_age(born_date):
    today = date.today()
    return today.year - born_date.year - ((today.month, today.day) < (born_date.month, born_date.day))

@app.route('/api/signUp', methods=['POST'])
def signUp():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    user_dob = data.get('dob')
    user_age = data.get('age')
    email = data.get('email')
    phone = data.get('phone')
    gender = data.get('gender')

    #check if all fields were provided
    required_fields = [username, password, user_dob, user_age, email, phone, gender]
    if any(field is None or field == '' for field in required_fields):
        return jsonify({"success": False, "message": "All fields are required."}), 400

    #confirm unique username, email and phone number
    existing_username = User.query.filter_by(username = username).first()
    if existing_username:
        return jsonify({"success": False, "message": "Username already taken."}), 409

    existing_email = User.query.filter_by(email = email).first()
    if existing_email:
        return jsonify({"success": False, "message": "Email is already registered."}), 409

    existing_phone = User.query.filter_by(phone_number = phone).first()
    if existing_phone:
        return jsonify({"success": False, "message": "Email is already registered"}), 409

    #TO-DO password hashing and verification

    try:
        new_user = User(
            username = username,
            password = password,
            DOB = user_dob,
            email = email,
            phone_number = phone,
            gender = gender
        )

        db.session.add(new_user)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f"Database error: {e}")
        return jsonify({"success": False, "message": "Database error."}), 500

    return jsonify({"success": True, "message": "Registration successful!"}), 201

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)