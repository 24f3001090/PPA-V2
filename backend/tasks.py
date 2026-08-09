from celery_worker import celery_app
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import smtplib
from dbmodel import Application as apl, Student as st, Company as com, Drive as dr
from flask import render_template
import csv
import os

SERVER_SMTP_HOST = 'localhost'
SERVER_SMTP_PORT = 1025
SENDER_ADDRESS = 'portal@college.edu'


def send_email(to_address, subject, message, content="text", attachment=None):
    msg = MIMEMultipart()
    msg['To'] = to_address
    msg['From'] = SENDER_ADDRESS
    msg['Subject'] = subject

    if content == "html":
        msg.attach(MIMEText(message, 'html'))
    else:
        msg.attach(MIMEText(message, 'plain'))

    if attachment:
        with open(attachment, "rb") as a:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(a.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment)}")
            msg.attach(part)

    s = smtplib.SMTP(host=SERVER_SMTP_HOST, port=SERVER_SMTP_PORT)
    s.send_message(msg)
    s.quit()
    return True


# Interview Reminder
@celery_app.task
def send_int_reminder():
    applications = apl.query.filter_by(status='Interview Scheduled').all()
    count = 0

    for job_app in applications:
        student = st.query.get(job_app.student_id)
        if student and student.email:
            company_name = job_app.drive.company.name if job_app.drive and job_app.drive.company else "Company"
            body = f"Dear {student.name},\n\nYour interview with {company_name} for the role of {job_app.drive.role} is scheduled for {job_app.int_date}.\n\nPlease be prepared on time."
            send_email(student.email, 'Upcoming Interview Reminder', body)
            count += 1

    return f"Sent {count} interview reminders."


# Monthly Placement Report
@celery_app.task
def send_report():
    companies = com.query.filter_by(status = 'Approved').all()
    
    for company in companies:
        drives = dr.query.filter_by(company_id=company.c_id).all()
        drive_ids = [d.d_id for d in drives]
        
        total_apps = apl.query.filter(apl.drive_id.in_(drive_ids)).count() if drive_ids else 0
        selected_apps = apl.query.filter(apl.drive_id.in_(drive_ids), apl.status == 'Selected').count() if drive_ids else 0

        html_content = render_template('report.html', company_name=company.name, total_drives=len(drives), total_applications=total_apps,
            total_selected=selected_apps)

        send_email(to_address=company.email, subject=f"Monthly Placement Report - {company.name}", message=html_content, content="html")

    return f"Monthly HTML reports sent to {len(companies)} companies."


# Export csv student
@celery_app.task
def export_student_csv(student_id):
    student = st.query.get_or_404(student_id)
    applications = apl.query.filter_by(student_id=student_id).all()

    file_path = f"static/exports/student_{student_id}_applications.csv"

    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Application ID', 'Company', 'Role', 'Package', 'Status', 'Interview Date'])
        for a in applications:
            writer.writerow([
                a.application_id,
                a.drive.company.name if a.drive and a.drive.company else 'N/A',
                a.drive.role if a.drive else 'N/A',
                a.drive.package if a.drive else 'N/A',
                a.status,
                a.int_date or 'N/A'
            ])

    send_email(
        student.email, 
        'Your Exported Application History (CSV)', 
        f"Hi {student.name},\n\nYour requested CSV export of your application history is attached below.",
        attachment=file_path
    )
    return file_path

# Export csv company
@celery_app.task
def export_company_csv(company_id):
    company = com.query.get_or_404(company_id)
    drives = dr.query.filter_by(company_id=company_id).all()
    
    file_path = f"static/exports/company_{company_id}_placements.csv"

    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        # Header row
        writer.writerow(['Drive ID', 'Role', 'Package', 'Student Name', 'Student Email', 'Status', 'Interview Date'])
        
        for d in drives:
            applications = apl.query.filter_by(drive_id=d.d_id).all()
            for a in applications:
                writer.writerow([
                    d.drive_id,
                    d.role,
                    d.package,
                    a.applicant.name if a.applicant else 'N/A',
                    a.applicant.email if a.applicant else 'N/A',
                    a.status,
                    a.int_date or 'N/A'
                ])

    send_email(
        to_address=company.email,
        subject='Your Requested Placement Data CSV Export',
        message=f"Hello {company.name},\n\nPlease find attached the exported placement summary report for your posted job drives.",
        attachment=file_path
    )
    return file_path