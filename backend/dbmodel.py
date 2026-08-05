from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db=SQLAlchemy()

drive_skills = db.Table(
    'drive_skills',
    db.Column('drive_id', db.Integer, db.ForeignKey('drive.d_id', ondelete='CASCADE'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.s_id', ondelete='CASCADE'), primary_key=True)
)

class Skill(db.Model):
    __tablename__ = 'skill'
    s_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"{self.name}"

class Application(db.Model):
    __tablename__ = 'application'
    a_id = db.Column(db.Integer(), primary_key = True, unique = True, autoincrement = True)
    @property
    def application_id(self):
        return f"A{self.a_id}"
    status = db.Column(db.String(100), nullable = False)
    app_date = db.Column(db.DateTime, default = lambda: datetime.now(timezone.utc))
    int_date = db.Column(db.Date)
    student_id = db.Column(db.Integer, db.ForeignKey('student.s_id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.d_id'), nullable=False)



class Drive(db.Model):
    __tablename__ = 'drive'
    d_id = db.Column(db.Integer(), primary_key = True, unique = True, autoincrement = True)
    @property
    def drive_id(self):
        return f"D{self.d_id}"
    role = db.Column(db.String(100), nullable = False)
    package = db.Column(db.String(100), nullable = False)
    experience =  db.Column(db.String(100), nullable = False)
    status = db.Column(db.String(100), nullable = False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.c_id'), nullable=False)
    skills = db.relationship('Skill', secondary= drive_skills, backref='drives', lazy = True)
    applications = db.relationship('Application', backref = 'drive', lazy = True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"{self.role}"


class Student(db.Model):
    __tablename__ = 'student'
    s_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    @property
    def student_id(self):
        return f"S{self.s_id}"
    email = db.Column(db.String(200), unique = True, nullable = False)
    name = db.Column(db.String(200), nullable = False)
    password = db.Column(db.String(255), nullable = False)
    level = db.Column(db.String(10), nullable = False)
    cgpa = db.Column(db.String(10), nullable = False)
    blacklisted = db.Column(db.Boolean, default=False)
    resume = db.Column(db.String(200), nullable = False)
    applications = db.relationship('Application', backref = 'applicant', lazy = True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"{self.name}"
    
class Company(db.Model):
    __tablename__ = 'company'
    c_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    @property
    def company_id(self):
        return f"C{self.c_id}"
    email = db.Column(db.String(200), unique = True, nullable = False)
    name = db.Column(db.String(200), nullable = False)
    password = db.Column(db.String(255), nullable = False)
    status = db.Column(db.String(20), nullable = False)
    blacklisted = db.Column(db.Boolean, default=False)
    drives = db.relationship('Drive', backref = 'company', lazy = True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"{self.name}"

class Admin(db.Model):
    a_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    @property
    def admin_id(self):
        return f"A{self.a_id}"
    email = db.Column(db.String(200), unique = True, nullable = False)
    name = db.Column(db.String(200), nullable = False)
    password = db.Column(db.String(255), nullable = False)

    






    