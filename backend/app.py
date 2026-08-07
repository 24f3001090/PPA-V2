import os
from sqlalchemy import event
from sqlalchemy.engine import Engine
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_jwt_extended import JWTManager,jwt_required, create_access_token, get_jwt, get_jwt_identity
from dbmodel import db, Admin as adm, Student as st, Company as com, Drive as dr, Skill as sk, Application as apl
from datetime import datetime

app = Flask(__name__)
CORS(app)

load_dotenv()

app.secret_key = "bipin"

UPLOAD_FOLDER = 'uploads/resumes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db.init_app(app)
jwt = JWTManager(app)

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
    

#Student Registration
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

#Login
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
    
#Admin Dashboard
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
        return jsonify({"msg": "Drive removed successfully"}), 200

    data = request.get_json()
    if 'status' in data:
        drive.status = data['status']  
    
    db.session.commit()
    return jsonify({"msg": "Drive status updated"}), 200


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


if __name__ == "__main__":
    app.run(debug = True) 