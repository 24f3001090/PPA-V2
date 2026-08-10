# PPA-V2

About: In this placement portal application, 3 kinds of dashboards were needed to be created and role based access were needed to be provided to the users. Admin or college must approve companies’ registrations to give them access and admin can blacklist any student or company or manage any drive or job application. Companies can create placement drives and students can apply for jobs. You can refer to the report for more information about application and author.

This is the Version 2 of placement portal application.

The application helps students, companies and institute to efficiently run placement drives and apply for jobs.

Frameworks used:
Flask
SQLite
SQlAlchemy
Vue JS
Celery
Redis

# How to run the app:

1. Go to backend folder:
cd backend

2. Create virtual environment (optional but recommended)
python -m venv venv

Activate it:

Windows:
venv\Scripts\activate

Linux/Mac:
source venv/bin/activate

3. Install dependencies:
pip install -r requirements.txt

4. Run Flask app:
python3 app.py

5. Open separate terminals for following:
Run redis server:
redis-server

Run Mailhog:
~/go/bin/MailHog

Run worker:
celery -A celery_worker.celery_app worker --loglevel=info

Run beat:
celery -A celery_worker.celery_app worker --loglevel=info

6. Go to frontend and install dependencies:
npm install

7. Run frontend:
npm run dev