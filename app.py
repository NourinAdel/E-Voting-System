from flask import Flask, render_template, request, flash
from database import db
from dotenv import load_dotenv
import models
from models import User
import os
from itsdangerous import URLSafeTimedSerializer
from email_services import send_email

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

@app.route('/')
def Login():
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
            
            # Generate token and mix in the salt for password.
            token = serializer.dumps(email, salt = 'password-reset-salt')
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
        # Try to decode the token. 
        # max_age=3600 means the token expires after 1 hour (3600 seconds).
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
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

if __name__ == '__main__':
    app.run(debug=True)