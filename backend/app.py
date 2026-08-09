import os
from sqlalchemy import event
from sqlalchemy.engine import Engine
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_jwt_extended import JWTManager,jwt_required, create_access_token, get_jwt, get_jwt_identity
from dbmodel import db, Admin as adm, Student as st, Company as com, Drive as dr, Skill as sk, Application as apl
from flask_caching import Cache

load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/resumes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'

CORS(app)

jwt = JWTManager(app)

cache = Cache(app)

db.init_app(app)

# This runs everytime flask contacts sqlite for db operation
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, _):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

with app.app_context():
    db.create_all()

    if not adm.query.first():
        superadmin = adm(email=os.getenv("ADMIN_EMAIL"), password=generate_password_hash(os.getenv("ADMIN_PASSWORD")), name="admin")
        db.session.add(superadmin)
        db.session.commit()

    if sk.query.count() == 0:
        default_skills = [
            sk(name="Python"),
            sk(name="Java"),
            sk(name="JavaScript"),
            sk(name="C++"),
            sk(name="SQL"),
            sk(name="Machine Learning")
        ]
        db.session.add_all(default_skills)
        db.session.commit()
    

# Student Registration
@app.route('/api/auth/register/student', methods=['POST'])
def register_student():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    level = request.form.get('level', 'UG')
    cgpa = request.form.get('cgpa')

    if st.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already registered"}), 400

    resume_file = request.files.get('resume')
    if not resume_file:
        return jsonify({"msg": "Resume file is required"}), 400

    filename = secure_filename(f"{email}_{resume_file.filename}")
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    resume_file.save(save_path)

    new_student = st(
        name=name,
        email=email,
        password=generate_password_hash(password),
        level=level,
        cgpa=str(cgpa),
        resume=save_path
    )

    db.session.add(new_student)
    db.session.commit()
    return jsonify({"msg": "Student account created!"}), 201

# Company Registration
@app.route('/api/auth/register/company', methods=['POST'])
def register_company():
    data = request.get_json()
    
    if com.query.filter_by(email=data.get('email')).first():
        return jsonify({"msg": "Email already exists"}), 400

    new_company = com(
        name=data.get('name'),
        email=data.get('email'),
        password=generate_password_hash(data.get('password')),
        status='Pending'
    )
    
    db.session.add(new_company)
    db.session.commit()
    return jsonify({"msg": "Company registration submitted! Awaiting Admin approval."}), 201

# Login
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if not email or not password or not role:
        return jsonify({"msg": "Email, password, and role are required"}), 400

    user = None

    # Role Lookup
    if role == 'admin':
        user = adm.query.filter_by(email=email).first()
    elif role == 'company':
        user = com.query.filter_by(email=email).first()
        if user and user.status != 'Approved':
            return jsonify({"msg": "Company profile is pending approval or rejected."}), 403
    elif role == 'student':
        user = st.query.filter_by(email=email).first()

    # Validate Credentials
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid email or password"}), 401

    # Check Blacklist Status
    if getattr(user, 'blacklisted', False):
        return jsonify({"msg": "Account is blacklisted by Admin."}), 403

    user_id = getattr(user, 'a_id', None) or getattr(user, 'c_id', None) or getattr(user, 's_id', None)

    # Store role and details directly in JWT Claims
    access_token = create_access_token(
        identity=str(user_id),
        additional_claims={
            "role": role,
            "email": user.email,
            "name": user.name
        }
    )

    return jsonify({
        "msg": "Login successful",
        "token": access_token,
        "role": role,
        "name": user.name
    }), 200
    
# Admin
@app.route('/api/admin/stats', methods=['GET'])
@jwt_required()
def admin_stats():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"msg": "Admin access required"}), 403

    return jsonify({
        "total_students": st.query.count(),
        "total_companies": com.query.count(),
        "total_drives": dr.query.count(),
        "total_applications": apl.query.count(),
        "pending_companies": com.query.filter_by(status='Pending').count(),
        "pending_drives": dr.query.filter_by(status='Pending').count()
    }), 200


@app.route('/api/admin/companies', methods=['GET'])
@jwt_required()
def admin_get_companies():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"msg": "Admin access required"}), 403

    search_query = request.args.get('q', '')
    query = com.query
    if search_query:
        query = query.filter(com.name.ilike(f"%{search_query}%"))
    
    companies = query.all()
    return jsonify([{
        "id": c.c_id,
        "company_id": c.company_id,
        "name": c.name,
        "email": c.email,
        "status": c.status,
        "blacklisted": c.blacklisted
    } for c in companies]), 200


@app.route('/api/admin/company/<int:c_id>/status', methods=['PATCH'])
@jwt_required()
def admin_update_company_status(c_id):
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"msg": "Admin access required"}), 403

    company = com.query.get_or_404(c_id)
    data = request.get_json()
    
    if 'status' in data:
        company.status = data['status']  
    if 'blacklisted' in data:
        company.blacklisted = data['blacklisted']

    db.session.commit()
    return jsonify({"msg": f"Company '{company.name}' updated successfully"}), 200


@app.route('/api/admin/drives', methods=['GET'])
@jwt_required()
def admin_get_drives():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"msg": "Admin access required"}), 403

    drives = dr.query.all()
    return jsonify([{
        "id": d.d_id,
        "drive_id": d.drive_id,
        "role": d.role,
        "company_name": d.company.name,
        "package": d.package,
        "status": d.status
    } for d in drives]), 200

@app.route('/api/admin/drive/<int:d_id>/status', methods=['PATCH', 'DELETE'])
@jwt_required()
def admin_manage_drive(d_id):
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"msg": "Admin access required"}), 403

    drive = dr.query.get_or_404(d_id)

    if request.method == 'DELETE':
        db.session.delete(drive)
        db.session.commit()
        return jsonify({"msg": "Drive deleted successfully"}), 200

    data = request.get_json()
    if 'status' in data:
        drive.status = data['status']
    
    db.session.commit()
    return jsonify({"msg": f"Drive status updated to {drive.status}"}), 200

@app.route('/api/admin/drive/<int:d_id>/applicants', methods=['GET'])
@jwt_required()
def admin_get_drive_applicants(d_id):
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"msg": "Admin access required"}), 403

    drive = dr.query.get_or_404(d_id)
    applications = apl.query.filter_by(drive_id=drive.d_id).all()

    return jsonify({
        "drive_role": drive.role,
        "applicants": [{
            "application_id": a.application_id,
            "a_id": a.a_id,
            "student_id": a.applicant.student_id,
            "name": a.applicant.name,
            "email": a.applicant.email,
            "cgpa": a.applicant.cgpa,
            "level": a.applicant.level,
            "resume": a.applicant.resume,
            "status": a.status,
            "app_date": a.app_date.strftime('%Y-%m-%d') if a.app_date else None,
            "int_date": a.int_date.strftime('%Y-%m-%d') if a.int_date else None
        } for a in applications]
    }), 200


@app.route('/api/admin/application/<int:a_id>', methods=['PATCH'])
@jwt_required()
def admin_update_application(a_id):
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"msg": "Admin access required"}), 403

    application = apl.query.get_or_404(a_id)
    data = request.get_json()

    if 'status' in data:
        application.status = data['status']

    db.session.commit()
    return jsonify({"msg": "Application updated by Admin"}), 200


@app.route('/api/admin/students', methods=['GET'])
@jwt_required()
def admin_get_students():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"msg": "Admin access required"}), 403

    search_query = request.args.get('q', '')
    query = st.query
    if search_query:
        query = query.filter((st.name.ilike(f"%{search_query}%")) | (st.email.ilike(f"%{search_query}%")))

    students = query.all()
    return jsonify([{
        "id": s.s_id,
        "student_id": s.student_id,
        "name": s.name,
        "email": s.email,
        "cgpa": s.cgpa,
        "level": s.level,
        "blacklisted": s.blacklisted
    } for s in students]), 200


@app.route('/api/admin/student/<int:s_id>/blacklist', methods=['PATCH'])
@jwt_required()
def admin_toggle_student_blacklist(s_id):
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"msg": "Admin access required"}), 403

    student = st.query.get_or_404(s_id)
    student.blacklisted = not student.blacklisted
    db.session.commit()
    return jsonify({"msg": f"Student blacklist status set to {student.blacklisted}"}), 200

#Company

# Dashboard Overview
@app.route('/api/company/dashboard', methods=['GET'])
@jwt_required()
def company_dashboard():
    claims = get_jwt()
    if claims.get('role') != 'company':
        return jsonify({"msg": "Company access required"}), 403

    company_id = int(get_jwt_identity())
    company = com.query.get(company_id)
    
    drives = dr.query.filter_by(company_id=company_id).all()
    drive_ids = [d.d_id for d in drives]
    
    total_drives = len(drives)
    applications = apl.query.filter(apl.drive_id.in_(drive_ids)).all() if drive_ids else []
    total_applications = len(applications)
    shortlisted_count = sum(1 for a in applications if a.status in ['Shortlisted', 'Interviewed', 'Selected'])

    skills_list = sk.query.order_by(sk.name.asc()).limit(5).all()

    return jsonify({
        "company_name": company.name,
        "stats": {
            "total_drives": total_drives,
            "total_applications": total_applications,
            "shortlisted_count": shortlisted_count
        },
        "drives": [{
            "id": d.d_id,
            "drive_id": d.drive_id,
            "role": d.role,
            "company_name": d.company.name,
            "package": d.package,
            "experience": d.experience,
            "status": d.status,
            "skills": [s.name for s in d.skills],
            "applicant_count": len(d.applications)
        } for d in drives],
        "available_skills": [{"id": s.s_id, "name": s.name} for s in skills_list]
    }), 200

# Update skills
@app.route('/api/company/drive/<int:d_id>/skills', methods=['PATCH'])
@jwt_required()
def update_drive_skills(d_id):
    claims = get_jwt()
    if claims.get('role') != 'company':
        return jsonify({"msg": "Company access required"}), 403

    company_id = int(get_jwt_identity())
    drive = dr.query.filter_by(d_id=d_id, company_id=company_id).first_or_404()

    data = request.get_json()
    raw_skill_names = data.get('skills', [])

    drive.skills.clear()  
    for name in raw_skill_names:
        clean_name = name.strip()
        if not clean_name:
            continue
        existing_skill = sk.query.filter(sk.name.ilike(clean_name)).first()
        if existing_skill:
            drive.skills.append(existing_skill)
        else:
            new_skill = sk(name=clean_name)
            db.session.add(new_skill)
            drive.skills.append(new_skill)

    db.session.commit()
    return jsonify({"msg": "Skills updated successfully"}), 200

# Create Placement Drive
@app.route('/api/company/drives', methods=['POST'])
@jwt_required()
def create_drive():
    claims = get_jwt()
    if claims.get('role') != 'company':
        return jsonify({"msg": "Company access required"}), 403

    company_id = int(get_jwt_identity())
    company = com.query.get(company_id)
    
    if company.status != 'Approved':
        return jsonify({"msg": "Unapproved companies cannot post drives"}), 403

    data = request.get_json()
    role_name = data.get('role')
    package = data.get('package')
    experience = data.get('experience')
    
    raw_skill_names = data.get('skills', [])

    if not role_name or not package or not experience:
        return jsonify({"msg": "Missing required drive details"}), 400

    new_drive = dr(
        role=role_name,
        package=package,
        experience=experience,
        status='Pending',
        company_id=company_id
    )

    for name in raw_skill_names:
        clean_name = name.strip()
        if not clean_name:
            continue

        existing_skill = sk.query.filter(sk.name.ilike(clean_name)).first()

        if existing_skill:
            new_drive.skills.append(existing_skill)
        else:
            formatted_name = clean_name.capitalize() if clean_name.islower() else clean_name
            new_skill = sk(name=formatted_name)
            db.session.add(new_skill)
            new_drive.skills.append(new_skill)

    db.session.add(new_drive)
    db.session.commit()
    return jsonify({"msg": "Placement drive created successfully!"}), 201


# Update Drive Status
@app.route('/api/company/drive/<int:d_id>/status', methods=['PATCH'])
@jwt_required()
def toggle_drive_status(d_id):
    claims = get_jwt()
    if claims.get('role') != 'company':
        return jsonify({"msg": "Company access required"}), 403

    company_id = int(get_jwt_identity())
    drive = dr.query.filter_by(d_id=d_id, company_id=company_id).first_or_404()

    data = request.get_json()
    if 'status' in data:
        drive.status = data['status']

    db.session.commit()
    return jsonify({"msg": f"Drive status changed to {drive.status}"}), 200


# Fetch Applicants
@app.route('/api/company/drive/<int:d_id>/applicants', methods=['GET'])
@jwt_required()
def get_drive_applicants(d_id):
    claims = get_jwt()
    if claims.get('role') != 'company':
        return jsonify({"msg": "Company access required"}), 403

    company_id = int(get_jwt_identity())
    drive = dr.query.filter_by(d_id=d_id, company_id=company_id).first_or_404()

    applications = apl.query.filter_by(drive_id=drive.d_id).all()
    return jsonify({
        "drive_role": drive.role,
        "applicants": [{
            "application_id": a.application_id,
            "a_id": a.a_id,
            "student_id": a.applicant.student_id,
            "name": a.applicant.name,
            "email": a.applicant.email,
            "cgpa": a.applicant.cgpa,
            "level": a.applicant.level,
            "resume": a.applicant.resume,
            "status": a.status,
            "app_date": a.app_date.strftime('%Y-%m-%d') if a.app_date else None,
            "int_date": a.int_date.strftime('%Y-%m-%d') if a.int_date else None
        } for a in applications]
    }), 200


# Application Management
@app.route('/api/company/application/<int:a_id>', methods=['PATCH'])
@jwt_required()
def update_application(a_id):
    claims = get_jwt()
    if claims.get('role') not in ['company', 'admin']:
        return jsonify({"msg": "Unauthorized access"}), 403

    application = apl.query.get_or_404(a_id)
    data = request.get_json()

    if 'status' in data:
        application.status = data['status']

    if 'int_date' in data:
        int_date_str = data.get('int_date')
        if int_date_str:
            from datetime import datetime
            application.int_date = datetime.strptime(int_date_str, '%Y-%m-%d').date()
        else:
            application.int_date = None

    db.session.commit()
    return jsonify({"msg": "Application updated successfully"}), 200


# View resume
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads/resumes', filename)

#Triggered Job
@app.route('/api/company/export-csv', methods=['POST'])
@jwt_required()
def trigger_company_csv_export():
    claims = get_jwt()
    if claims.get('role') != 'company':
        return jsonify({"msg": "Company access required"}), 403

    company_id = int(get_jwt_identity())
    
    from tasks import export_company_csv
    export_company_csv.delay(company_id)

    return jsonify({"msg": "Placement CSV export triggered! Check your registered email shortly."}), 200

#Student

# Dashboard Overview
@app.route('/api/student/dashboard', methods=['GET'])
@jwt_required()
def student_dashboard():
    claims = get_jwt()
    if claims.get('role') != 'student':
        return jsonify({"msg": "Student access required"}), 403

    student_id = int(get_jwt_identity())
    student = st.query.get_or_404(student_id)

    if student.blacklisted:
        return jsonify({"msg": "Account blacklisted. Contact support."}), 403

    search_query = request.args.get('q', '')

    query = dr.query.filter_by(status='Approved')
    if search_query:
        query = query.join(com).filter(
            (dr.role.ilike(f"%{search_query}%")) | 
            (com.name.ilike(f"%{search_query}%"))
        )

    approved_drives = query.all()
    
    applied_drive_ids = [a.drive_id for a in apl.query.filter_by(student_id=student_id).all()]

    return jsonify({
        "student": {
            "name": student.name,
            "email": student.email,
            "cgpa": student.cgpa,
            "level": student.level,
            "resume": student.resume
        },
        "drives": [{
            "id": d.d_id,
            "drive_id": d.drive_id,
            "company_name": d.company.name,
            "role": d.role,
            "package": d.package,
            "experience": d.experience,
            "status": d.status,
            "skills": [s.name for s in d.skills],
            "already_applied": d.d_id in applied_drive_ids
        } for d in approved_drives]
    }), 200


# Apply for a Placement Drive
@app.route('/api/student/apply/<int:d_id>', methods=['POST'])
@jwt_required()
def apply_to_drive(d_id):
    claims = get_jwt()
    if claims.get('role') != 'student':
        return jsonify({"msg": "Student access required"}), 403

    student_id = int(get_jwt_identity())
    student = st.query.get_or_404(student_id)

    if student.blacklisted:
        return jsonify({"msg": "Blacklisted students cannot apply to drives."}), 403

    drive = dr.query.filter_by(d_id=d_id, status='Approved').first_or_404()

    existing_application = apl.query.filter_by(student_id=student_id, drive_id=drive.d_id).first()
    if existing_application:
        return jsonify({"msg": "You have already applied for this drive"}), 400

    new_application = apl(
        student_id=student_id,
        drive_id=drive.d_id,
        status='Applied'
    )

    db.session.add(new_application)
    db.session.commit()
    return jsonify({"msg": f"Successfully applied for {drive.role} at {drive.company.name}!"}), 201


# Applied Drives & Status Trackers
@app.route('/api/student/applications', methods=['GET'])
@jwt_required()
def student_applications():
    claims = get_jwt()
    if claims.get('role') != 'student':
        return jsonify({"msg": "Student access required"}), 403

    student_id = int(get_jwt_identity())
    applications = apl.query.filter_by(student_id=student_id).all()

    return jsonify([{
        "a_id": a.a_id,
        "application_id": a.application_id,
        "role": a.drive.role,
        "company_name": a.drive.company.name,
        "package": a.drive.package,
        "status": a.status,
        "app_date": a.app_date.strftime('%Y-%m-%d') if a.app_date else None,
        "int_date": a.int_date.strftime('%Y-%m-%d') if a.int_date else None
    } for a in applications]), 200

# Triggered Job
@app.route('/api/student/export-csv', methods=['POST'])
@jwt_required()
def trigger_student_csv_export():
    claims = get_jwt()
    if claims.get('role') != 'student':
        return jsonify({"msg": "Student access required"}), 403

    student_id = int(get_jwt_identity())
    
    from tasks import export_student_csv
    export_student_csv.delay(student_id)

    return jsonify({"msg": "CSV export initiated. You will receive an email shortly with your CSV file!"}), 200

if __name__ == "__main__":
    app.run(debug = True) 