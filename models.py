from datetime import datetime, timezone
from enum import Enum
from database import db

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('Admin', 'Voter', name='user_roles'), nullable=False, default='Voter')
    email = db.Column(db.String(120), unique=True, nullable=False)
    DOB = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum('Male', 'Female', name='gender_enum'), nullable=False)
    phone_number = db.Column(db.String(11), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Election(db.Model):
    __tablename__ = 'election'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('ongoing', 'completed', name='election_status'), nullable=False)
    type = db.Column(db.Enum('Poll', 'Election', name='election_type'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Candidate(db.Model):
    __tablename__ = 'candidate'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    is_human = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    image_path = db.Column(db.String(200), nullable=False)

class Voter_History(db.Model):
    __tablename__ = 'voter_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), nullable=False)
    candidate_hash = db.Column(db.String(64), nullable=False)
    candidate_encrypted = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_verified = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'election_id', name='unique_user_election_vote'),
    )

class Election_Result_History(db.Model):
    __tablename__ = 'election_result_history'

    id = db.Column(db.Integer, primary_key=True)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    is_winner = db.Column(db.Boolean, default=False)
    final_vote_count = db.Column(db.Integer, default=0)
    image_path = db.Column(db.String(200), nullable=False)

class Election_Candidate(db.Model):
    __tablename__ = 'election_candidate'

    id = db.Column(db.Integer, primary_key=True)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    
    __table_args__ = (
    db.UniqueConstraint('election_id', 'candidate_id', name='unique_election_candidate'),
)