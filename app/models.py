from app import db, bcrypt 
from flask_login import UserMixin 
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.sqlite import JSON

IST = timezone(timedelta(hours=5, minutes=30))
user_subjects = db.Table(
    'user_subjects',
    db.Column('profile_id', db.Integer, db.ForeignKey('user_profile.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
)

class User(db.Model,UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False,index=True)
    username = db.Column(db.String(80), unique=True, nullable=False,index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_premium = db.Column(db.Boolean, default=False)
    profile_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))

    profile = db.relationship('UserProfile', back_populates='user', uselist=False)

    @property
    def password(self):
        raise AttributeError("Password is write-only!")

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    class_level = db.Column(db.String(50), nullable=True)
    target_exam = db.Column(db.String(50), nullable=True)

    user = db.relationship('User', back_populates='profile')
    # Many-to-many: which subjects this user studies
    subjects = db.relationship('Subject', secondary=user_subjects, back_populates='students')

class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)   # e.g. "PHY101"
    name = db.Column(db.String(100), nullable=False)               # e.g. "Physics"

    # Which students have chosen this subject
    students = db.relationship('UserProfile', secondary=user_subjects, back_populates='subjects')
    # Mappings to class/exam
    mappings = db.relationship('SubjectMapping', back_populates='subject', cascade='all, delete-orphan')

class SubjectMapping(db.Model):
    __tablename__ = 'subject_mapping'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    class_level = db.Column(db.String(50), nullable=False)   # e.g. "Class 9", "BTech 2nd Sem"
    target_exam = db.Column(db.String(50), nullable=False)   # e.g. "School Exams", "JEE"

    subject = db.relationship('Subject', back_populates='mappings')

class Upload(db.Model):
    __tablename__ = 'upload'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # One of these will be filled
    pdf_url = db.Column(db.String(500), nullable=True)
    youtube_url = db.Column(db.String(500), nullable=True)

    # What kind of upload this is: "pdf" or "youtube"
    upload_type = db.Column(db.String(10), nullable=False)  

    # Timestamp for ordering
    uploaded_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # Optional fields
    status = db.Column(db.String(50), default="pending")  # "pending", "processed", "failed"
    notes_generated = db.Column(db.Boolean, default=False)
    quiz_generated = db.Column(db.Boolean, default=False)

    # Relationship
    user = db.relationship('User', backref='uploads')
