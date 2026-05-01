# Team Task Manager - Complete Project Management Solution

A modern, full-stack team task management application with role-based access control, real-time dashboard, and beautiful glassmorphism UI.

## ✨ Features

### Authentication & Security
- User registration and login system
- Password hashing with Werkzeug security
- Session management with Flask-Login
- Role-based access control (Admin/Member)

### Dashboard Analytics
- Real-time statistics overview
- Task completion rate with progress bars
- Overdue tasks tracking
- Recent activities timeline

### Project Management
- Create, view, and delete projects
- Add team members to projects
- Track project progress

### Task Management
- Create tasks with due dates
- Assign tasks to team members
- Priority levels (Low/Medium/High)
- Status tracking (Pending/In Progress/Completed)
- Overdue task alerts

### Team Collaboration
- View all team members
- Role-based permissions
- Admin can see all users

### Modern UI/UX
- Glassmorphism design
- Smooth animations
- Responsive layout
- Toast notifications

## 🛠️ Tech Stack

- **Backend**: Python 3.8+, Flask 2.3.3, Flask-SQLAlchemy, Flask-Login
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript, Font Awesome

## 📂 Project Structure
team-task-manager/
├── app.py # Main application
├── database.py # Database models
├── requirements.txt # Dependencies
├── static/
│ ├── css/style.css # Styles
│ └── js/main.js # JavaScript
└── templates/
├── base.html
├── index.html
└── dashboard.html


## 🚀 Installation

### Prerequisites
- Python 3.8 or higher

### Steps

```bash
# 1. Clone or download project
cd team-task-manager

# 2. Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application
python app.py

Access at http://localhost:5000

🔑 Login Credentials
Role	Username	Password
Admin	admin	    admin123
Member	john	    john123
Member	sarah	    sarah123
You can also register a new account.

📖 API Documentation
1. Authentication
Method	Endpoint	            Description
POST	/api/register	        Register new user
POST	/api/login	            Login user
POST	/api/logout         	Logout user
GET	    /api/user	            Get current user

2. Projects
Method	    Endpoint            Description
GET	        /api/projects	    Get all projects
POST    	/api/projects	    Create project
DELETE	    /api/projects/<id>	Delete project

3. Tasks
Method	        Endpoint	            Description
GET	            /api/tasks	            Get all tasks
POST        	/api/tasks	            Create task
PUT	            /api/tasks/<id>	        Update task
DELETE	        /api/tasks/<id>	        Delete task

4. Team
Method	        Endpoint	            Description
GET	            /api/users	            Get all users
GET	            /api/dashboard/stats	Get statistics

🎯 Usage Guide
1. For Admin Users

Login with admin credentials
Create projects from Projects section
Add team members to projects
Create and assign tasks
Monitor all activities from dashboard

2. For Member Users

Login with member credentials
View assigned tasks on dashboard
Update task status (Pending/In Progress/Completed)
Create your own projects
View team members



📖 Deployment to Railway
# 1. Push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/team-task-manager.git
git push -u origin main

# 2. Create railway.json
{
  "build": { "builder": "NIXPACKS" },
  "deploy": { "startCommand": "gunicorn app:app" }
}

# 3. Add gunicorn to requirements.txt
echo "gunicorn==21.2.0" >> requirements.txt

# 4. Deploy on Railway
# - Sign up at railway.app
# - Connect GitHub repo
# - Add environment variable: SECRET_KEY


📊 Database Schema
Users: id, username, email, password, role, created_at
Projects: id, name, description, status, created_by, created_at
Tasks: id, title, description, status, priority, due_date, created_by, assigned_to, project_id
TeamMembers: id, project_id, user_id, joined_at


🔒 Security Features
Password hashing (Werkzeug)
Session management (Flask-Login)
Role-based access control
SQL injection prevention (SQLAlchemy ORM)
Protected API endpoints


📝 License
MIT License - Free for personal and commercial use

📧 Support
For issues, check GitHub repository or create an issue.