import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash
from dbmodel import db, Admin as adm, Student as st, Company as com, Drive as dr, Skill as sk, Application as apl
from datetime import datetime

app = Flask(__name__)

load_dotenv()

app.secret_key = "bipin"

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db.init_app(app)

with app.app_context():
    db.create_all()

    if not adm.query.first():
        superadmin = adm(email=os.getenv("ADMIN_EMAIL"), password=generate_password_hash(os.getenv("ADMIN_PASSWORD")), name="admin")
        db.session.add(superadmin)
        db.session.commit()
    


#Landing Page
@app.route("/")
def main_page():
    # return render_template("index.html")
    return "<p>Hello</p>"

#Register Page
@app.route("/register", methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        level = request.form.get('level')
        role = request.form.get('role')
        file = request.files.get('resume') 
        cgpa = request.form.get('cgpa')


        if not request.form.get('declaration'):
            return render_template("registrationpage.html", error="Please accept the declaration")
        
        # Is it a Student?
        if role == 'student':
            checkStudent = st.query.filter_by(email=email).first()
            if checkStudent:
                return render_template("registrationpage.html", error = 'Email already registered')
            else:
                if name and email and password and level and cgpa and role and file and file.filename != '':
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    file.save(filepath)
                    student= st(name=name, password=password, email=email, level=level, resume=file.filename, cgpa = cgpa)
                    db.session.add(student)
                    db.session.commit()
                    return redirect("/login")
                else:
                    return render_template("registrationpage.html")
            
        # Is it a Company?    
        else:
            checkCompany = com.query.filter_by(email=email).first()
            if checkCompany:
                return render_template("registrationpage.html", error = 'Email already registered')
            else:
                if name and email and password and role:
                    company = com(name=name, password=password, email=email, status = 'pending')
                    db.session.add(company)
                    db.session.commit()
                    st.query.all()
                    return redirect("/login")
                else:
                    return render_template("registrationpage.html")
    else:
        return render_template("registrationpage.html")

#Login Page
@app.route("/login", methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        #Is it a student?
        checkStudent = st.query.filter_by(email=email).first()
        if checkStudent:
            if checkStudent.password == password and not checkStudent.blacklisted:
                session.clear()
                session['user'] = 'student'
                session['student_id'] = checkStudent.s_id
                s_id = checkStudent.s_id
                return redirect(url_for("student", st_id = s_id))
            else:
                return render_template("loginpage.html")
        #Is it a company?
        checkCompany = com.query.filter_by(email=email).first()
        if checkCompany:
            if checkCompany.status == 'approved' and checkCompany.password == password and not checkCompany.blacklisted:
                session.clear()
                session['user'] = 'company'
                session['company_id'] = checkCompany.c_id
                c_id = checkCompany.c_id
                return redirect(url_for("company", com_id = c_id))
            else:
                return render_template("loginpage.html")
            

        #Is it admin?
        if email == 'admin@tenacious.com' and password == "superior":
            session.clear()
            session['user'] = 'admin'
            return redirect("/administrator")
        else:
            return render_template("loginpage.html")
    else:
        return render_template("loginpage.html")
    
#Admin Dashboard
@app.route("/administrator", methods = ['GET', 'POST'])
def admin():
    if session.get('user') != 'admin':
        return redirect("/login")
    
    if request.method == 'POST':
        #Search
        role = request.form.get('role')
        demand = request.form.get('demand')
        
        if role == 'student':
            name_based_results = st.query.filter(st.name.ilike(f"%{demand}%")).all()
            email_based_results = st.query.filter(st.email.ilike(f"%{demand}%")).all()
            return render_template("adminsearch.html", name_based_results = name_based_results, email_based_results = email_based_results, role = role)

        elif role == 'company':
            name_based_results = com.query.filter(com.name.ilike(f"%{demand}%")).all()
            email_based_results = com.query.filter(com.email.ilike(f"%{demand}%")).all()
            return render_template("adminsearch.html", name_based_results = name_based_results, email_based_results = email_based_results, role = role)
        
        #Company Registration
        approval = request.form.get('approval')
        com_id = request.form.get('com_id')

        company = com.query.get(com_id)
        if company:
            if approval == 'yes':
                company.status = 'approved'
            else:
                company.status = 'rejected'

        #Job Application
        status = request.form.get('status')
        app_id = request.form.get('app_id')
        j_app = apl.query.get(app_id)
        if status and status == 'reject':
            j_app.status = 'college rejected'

        db.session.commit()

    pending_reg = com.query.filter_by(status = 'pending')
    black_companies = com.query.filter_by(blacklisted = True)
    black_students = st.query.filter_by(blacklisted = True)
    white_companies = com.query.filter_by(blacklisted = False, status = 'approved')
    white_students = st.query.filter_by(blacklisted = False)
    j_applications = apl.query.all()
    return render_template("admindashboard.html", pending_reg = pending_reg, black_students = black_students, black_companies = black_companies, white_students = white_students, white_companies = white_companies, j_applications = j_applications)

@app.route("/administrator/view/student/<int:st_id>", methods = ['GET', 'POST'])
def userview_st(st_id):
    if session.get('user') != 'admin':
        return redirect("/login")
    
    user = st.query.get(st_id)
    students = st.query.all()
    if request.method == 'POST':
        blacklist = request.form.get('blacklist')
        if blacklist == 'yes':
            user.blacklisted = True
        else:
            user.blacklisted = False
        db.session.commit()

    return render_template("userview.html", user = user, students = students)

@app.route("/administrator/view/company/<int:com_id>", methods = ['GET', 'POST'])
def userview_com(com_id):
    if session.get('user') != 'admin':
        return redirect("/login")
    
    user = com.query.get(com_id)
    students = st.query.all()
    if request.method == 'POST':
        #Drive deactivation
        status = request.form.get('status')
        drive_id = request.form.get('drive_id')
        drive = dr.query.get(drive_id)
        if drive:
            if status == 'activate':
                drive.status = 'active'
            else:
                drive.status = 'deactivated'

        #Blacklisting
        blacklist = request.form.get('blacklist')
        if blacklist:
            if blacklist == 'yes':
                user.blacklisted = True
                for drive in user.drives:
                    drive.status = 'closed'
            else:
                user.blacklisted = False
                for drive in user.drives:
                    drive.status = 'closed'
        db.session.commit()

    return render_template("userview.html", user = user, students = students)

#Company Dashboard
@app.route("/company/<int:com_id>")
def company(com_id):
    if session.get('user') != 'company':
        return redirect("/login")
    if session.get('company_id') != com_id:
        return "Unauthorized access"
    
    company = com.query.get(com_id)
    return render_template("comdashboard.html", company = company)

@app.route("/company/all-drives/<int:com_id>")
def com_drives(com_id):
    if session.get('user') != 'company':
        return redirect("/login")
    if session.get('company_id') != com_id:
        return "Unauthorized access"
    
    company = com.query.get(com_id)
    drives = company.drives
    return render_template("comdrives.html", drives = drives)

@app.route("/company/drive/<int:com_id>", methods=['GET', 'POST'])
def drive(com_id):
    if session.get('user') != 'company':
        return redirect("/login")
    if session.get('company_id') != com_id:
        return "Unauthorized access"
    
    if request.method == 'POST':
        role = request.form.get('role')
        package = request.form.get('package')
        experience = request.form.get('experience')

        if role and package and experience:
            drive = dr(role = role, package = package, experience = experience, status = 'active', company_id = com_id)
            db.session.add(drive)
            db.session.commit()
            drive_id = drive.d_id
            return redirect(url_for("edit", drive_id = drive_id, com_id = com_id))
        else:
            return render_template("createdrive.html", error = "All fields are mandatory.")
    else:
        return render_template("createdrive.html")

@app.route("/company/drive/edit/<int:drive_id>/<int:com_id>", methods = ['GET', 'POST'])
def edit(drive_id, com_id):
    if session.get('user') != 'company' and session.get('user') != 'admin':
        return redirect("/login")
    if session.get('user') == 'company' and session.get('company_id') != com_id:
        return "Unauthorized access"

    drive = dr.query.get(drive_id)
    if request.method == 'POST':
        skill = request.form.get('skill')
        status = request.form.get('status')
        if status:
            if status == 'closed':
                drive.status = 'closed'
            else:
                drive.status = 'active'
        if skill:
            new_skill = sk(name = skill, drive_id = drive_id)
            db.session.add(new_skill)

        db.session.commit()
        
    return render_template("driveupdate.html", drive = drive)

@app.route("/company/applications/<int:com_id>")
def applications(com_id):
    if session.get('user') != 'company':
        return redirect("/login")
    if session.get('company_id') != com_id:
        return "Unauthorized access"
    
    company = com.query.get(com_id)
    drives = company.drives
    j_apps = []
    for drive in drives:
        j_apps.extend(drive.applications)
    return render_template("comapplications.html", j_apps = j_apps)

@app.route("/company/applications/view/<int:app_id><int:com_id>", methods = ['GET', 'POST'])
def view_st_application(app_id, com_id):
    if session.get('user') != 'company':
        return redirect("/login")
    if session.get('company_id') != com_id:
        return "Unauthorized access"
    
    j_app = apl.query.get(app_id)
    if request.method == 'POST':
        approval = request.form.get('approval')
        sch_date = request.form.get('sch_date')
        interview = request.form.get('interview')
        select = request.form.get('select')

        if approval:
            if approval == 'yes':
                j_app.status = 'shortlisted'
            else:
                j_app.status == 'rejected'
        
        if sch_date and interview:
                j_app.status = 'interview scheduled'
                j_app.int_date = datetime.strptime(sch_date, "%Y-%m-%d").date()

        if select:
            if select == 'yes':
                j_app.status = 'selected'
            else:
                j_app.status = 'rejected'
        db.session.commit()

    return render_template("comapplicationview.html", j_app = j_app)

#Student Dashboard
@app.route("/student/<int:st_id>", methods = ['GET', 'POST'])
def student(st_id):
    if session.get('user') != 'student':
        return redirect("/login")
    if session.get('student_id') != st_id:
        return "Unauthorized access"

    student = st.query.get(st_id)
    if request.method == 'POST':
        demand = request.form.get('demand')
        results_com = com.query.filter(com.name.ilike(f"%{demand}%")).filter_by(status = 'approved', blacklisted = False).all()
        results_drives = dr.query.filter(dr.role.ilike(f"%{demand}%")).filter_by(status = 'active').all()
        results_skills = sk.query.join(sk.drive).filter(sk.name.ilike(f"%{demand}%"), dr.status == 'active').all()
        return render_template('search.html', results_com = results_com, results_drives = results_drives, results_skills = results_skills, student = student)

    return render_template("stdashboard.html", student = student)

@app.route("/student/all-drives/<int:st_id>")
def st_drives(st_id):
    if session.get('user') != 'student':
        return redirect("/login")
    if session.get('student_id') != st_id:
        return "Unauthorized access"
    
    drives = dr.query.filter_by(status = 'active')
    return render_template("stdrives.html", drives = drives, st_id = st_id)

@app.route("/student/all-companies/<int:st_id>")
def st_com(st_id):
    if session.get('user') != 'student':
        return redirect("/login")
    if session.get('student_id') != st_id:
        return "Unauthorized access"
    
    companies = com.query.filter_by(blacklisted = False, status = 'approved')
    return render_template("stcompanies.html", st_id = st_id, companies = companies)

@app.route("/student/apply/<int:st_id>/<int:drive_id>", methods=['GET', 'POST'])
def apply(st_id, drive_id):
    if session.get('user') != 'student':
        return redirect("/login")
    if session.get('student_id') != st_id:
        return "Unauthorized access"
    
    drive = dr.query.get(drive_id)
    if request.method == 'POST':
        declaration = request.form.get('declaration')
        apply = request.form.get('apply')
        if declaration and apply:
            application = apl(status = 'applied', student_id = st_id, drive_id = drive_id)
            db.session.add(application)
            db.session.commit()
            
    existing_application = apl.query.filter_by(student_id=st_id, drive_id=drive_id).first()
    return render_template("apply.html", drive = drive, applied_already = existing_application)


@app.route("/student/applications/<int:st_id>")
def st_applications(st_id):
    if session.get('user') != 'student':
        return redirect("/login")
    if session.get('student_id') != st_id:
        return "Unauthorized access"
    
    student = st.query.get(st_id)
    j_apps = student.applications
    return render_template("stapplications.html", j_apps = j_apps)

@app.route("/student/applications/track/<int:app_id>/<int:st_id>")
def track(app_id, st_id):
    if session.get('user') != 'student' and session.get('user') != 'admin' :
        return redirect("/login")
    if session.get('user') == 'student' and session.get('student_id') != st_id:
        return "Unauthorized access"
    
    j_app = apl.query.get(app_id)
    return render_template("track.html", j_app = j_app)

@app.route("/student/profile/<int:st_id>", methods = ['GET', 'POST'])
def profile(st_id):
    if session.get('user') != 'student':
        return redirect("/login")
    if session.get('student_id') != st_id:
        return "Unauthorized access"
    
    student = st.query.get(st_id)
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        level = request.form.get('level')
        cgpa = request.form.get('cgpa')
        password = request.form.get('password')
        resume = request.files.get('resume')

        if name:
            student.name = name

        if email:
            student.email = email

        if level:
            student.level = level

        if cgpa:
            student.cgpa = cgpa

        if password:
            student.password = password

        if resume and resume.filename != '':
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], resume.filename)
            resume.save(filepath)
            student.resume = resume.filename
            
        db.session.commit()

    return render_template("profilemgmt.html", student = student)


@app.route("/student/search/company/<int:com_id>/<int:st_id>")
def searched_com_drives(com_id, st_id):
    if session.get('user') != 'student':
        return redirect("/login")
    if session.get('student_id') != st_id:
        return "Unauthorized access"

    company = com.query.get(com_id)
    drives = company.drives
    for drive in drives:
        if drive.status == 'closed':
            drives.remove(drive)
    return render_template("stsearchcomdrives.html",drives = drives , st_id = st_id)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)