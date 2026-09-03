from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, session
from database import db
from dotenv import load_dotenv
import models
from models import User, Candidate, Election, Election_Candidate
import os
from itsdangerous import URLSafeTimedSerializer
from email_services import send_email
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import traceback

load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
        if user and check_password_hash(user.password, plain_pass + os.environ.get('PASSWORD_PEPPER')):
            if user.role == "Admin":
                return jsonify({
                    "status": "success",
                    "redirect_url": "/adminDashboard.html"
                })
            else:
                return jsonify({
                    "status": "success",
                    "redirect_url": "/viewElections"
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
        data = request.get_json()
        new_password = data.get('password')
        
        user = User.query.filter_by(email=email).first()

        if user:
            user.password = generate_password_hash(new_password + os.environ.get('PASSWORD_PEPPER'))
            db.session.commit()
            return jsonify({
                "status": "success",
                "redirect_url": "/"
            })
        else:
            return jsonify({
                "status": "error", 
                "message": "User not found."
            })
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
    email = data.get('email')
    phone = data.get('phone')
    gender = data.get('gender')

    #check if all fields were provided
    required_fields = [username, password, user_dob, email, phone, gender]
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
        return jsonify({"success": False, "message": "Phone is already registered"}), 409

    if not phone.isdigit() or len(phone) != 11:
        return jsonify({"success": False, "message": "Phone number must be exactly 11 digits."}), 400

    try:
        new_user = User(
            username = username,
            password = generate_password_hash(password + os.environ.get('PASSWORD_PEPPER')),
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

@app.route('/addElection', methods=['GET', 'POST'])
def add_election():
    if request.method == 'GET':
        return render_template('addElection.html')
    try:
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        date_str = request.form.get('date', '').strip()
        election_type = request.form.get('type')
        picture_file = request.files.get('picture')

        if not name or not date_str or not election_type or not description or not picture_file:
            return jsonify({"message": "Please fill in all required fields."}), 400

        filename = None
        if picture_file and picture_file.filename != '':
            filename = secure_filename(f"election_{int(datetime.utcnow().timestamp())}_{picture_file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            picture_file.save(filepath)

        new_election = Election(
            name = name,
            description = description,
            image_path = filename,
            end_date = date_str,
            type = election_type,
            status = 'ongoing'
        )

        db.session.add(new_election)
        db.session.commit()

        return jsonify({
            "status": "success",
            "election_id": new_election.id
        }), 201

    except Exception as e:
        db.session.rollback()
        print("====== BACKEND CRASH TRACEBACK ======")
        traceback.print_exc()
        print("=====================================")
        return jsonify({"message": f"Server error: {str(e)}"}), 500


@app.route('/addCandidates', methods=['POST', 'GET'])
def add_candidates():
    if request.method == 'GET':
        election_id = request.args.get('election_id')
        return render_template('addCandidates.html', election_id=election_id)

    try:
        election_id = request.form.get('election_id')
        if not election_id:
            return jsonify({"error": "Missing election ID."}), 400

        election = Election.query.filter_by(id=election_id).first()
        if not election:
            return jsonify({"error": "Election not found."}), 404
    
        names = request.form.getlist('names[]')
        descriptions = request.form.getlist('descriptions[]')
        images = request.files.getlist('images[]')

        if not(2 <= len(names) <= 5):
            return jsonify({"error", "You must submit between 2 and 5 candidates."}), 400

        added_count = 0

        for i in range(len(names)):
            cleaned_name = names[i].strip()
            cleaned_desc = descriptions[i].strip() if i < len(descriptions) else ""
            img_file = images[i] if i < len(images) else None

            filename = "default.png"
            if img_file and img_file.filename != '':
                filename = secure_filename(f"cand_{election.id}_{i}_{img_file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                img_file.save(filepath)

            # 1. Check/create Candidate record (attributes: name, description, image_path)
            candidate = Candidate.query.filter_by(name=cleaned_name, description=cleaned_desc).first()
            if not candidate:
                candidate = Candidate(
                    name=cleaned_name,
                    description=cleaned_desc,
                    image_path=filename
                )
                db.session.add(candidate)
                db.session.flush()  # Populates candidate.id

            # 2. Prevent enrolling in the same election twice
            is_enrolled = Election_Candidate.query.filter_by(
                election_id=election.id,
                candidate_id=candidate.id
            ).first()

            if not is_enrolled:
                link = Election_Candidate(
                    election_id=election.id,
                    candidate_id=candidate.id
                )
                db.session.add(link)
                added_count += 1

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": f"Successfully added {added_count} candidate(s)."
        }), 200

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/viewElections')
def view_elections():
    today = date.today()

    expired = Election.query.filter(
        Election.status == 'ongoing',
        Election.end_date <= today
    ).all()

    if expired:
        for election in expired:
            election.status = 'completed'
        db.session.commit()

    active = Election.query.filter(
        Election.status == 'ongoing',
        Election.end_date > today
    ).all()

    return render_template('viewElections.html', elections=active)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    if request.method == 'POST':
        return jsonify({"status": "success"}), 200
    return redirect(url_for('login'))
    

if __name__ == '__main__':
    app.run(debug=True)