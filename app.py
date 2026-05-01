from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database import db, User, Project, Task, TeamMember
from datetime import datetime
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///taskmanager.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables and sample data
with app.app_context():
    db.create_all()
    
    # Create admin user if not exists
    if not User.query.filter_by(username='admin').first():
        hashed = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
        admin = User(username='admin', email='admin@taskmanager.com', 
                     password=hashed.decode('utf-8'), role='admin')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created - Username: admin, Password: admin123")
    
    # Create demo user if not exists
    if not User.query.filter_by(username='john').first():
        hashed = bcrypt.hashpw('john123'.encode('utf-8'), bcrypt.gensalt())
        john = User(username='john', email='john@example.com', 
                    password=hashed.decode('utf-8'), role='member')
        db.session.add(john)
        db.session.commit()
        print("✅ Demo user created - Username: john, Password: john123")
    
    # Create demo project if no projects exist
    if Project.query.count() == 0:
        admin = User.query.filter_by(username='admin').first()
        demo_project = Project(
            name='Demo Project',
            description='This is a demo project to get you started',
            created_by=admin.id,
            status='active'
        )
        db.session.add(demo_project)
        db.session.commit()
        
        # Add team member
        john = User.query.filter_by(username='john').first()
        if john:
            team_member = TeamMember(project_id=demo_project.id, user_id=john.id)
            db.session.add(team_member)
            db.session.commit()
        
        # Create demo task
        demo_task = Task(
            title='Complete the project setup',
            description='Set up the task management system',
            due_date=datetime(2025, 12, 31, 23, 59, 59),
            created_by=admin.id,
            assigned_to=admin.id,
            project_id=demo_project.id,
            priority='high'
        )
        db.session.add(demo_task)
        db.session.commit()
        print("✅ Demo project and task created")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Authentication APIs
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User(username=username, email=email, password=hashed.decode('utf-8'), role='member')
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User created successfully', 'user_id': user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        user = User.query.filter_by(username=username).first()
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        login_user(user)
        return jsonify({'message': 'Login successful', 'user': {
            'id': user.id, 
            'username': user.username, 
            'role': user.role
        }}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    if current_user.is_authenticated:
        return jsonify({'authenticated': True, 'username': current_user.username}), 200
    return jsonify({'authenticated': False}), 401

@app.route('/api/user', methods=['GET'])
@login_required
def get_user():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'role': current_user.role
    })

# Project APIs
@app.route('/api/projects', methods=['GET'])
@login_required
def get_projects():
    if current_user.role == 'admin':
        projects = Project.query.all()
    else:
        team_projects = db.session.query(Project).join(TeamMember).filter(TeamMember.user_id == current_user.id).all()
        owned_projects = Project.query.filter_by(created_by=current_user.id).all()
        projects = list(set(team_projects + owned_projects))
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description or 'No description',
        'status': p.status,
        'created_by': p.created_by,
        'created_at': p.created_at.isoformat(),
        'owner_name': User.query.get(p.created_by).username if User.query.get(p.created_by) else 'Unknown',
        'task_count': len(p.tasks),
        'completed_tasks': sum(1 for task in p.tasks if task.status == 'completed')
    } for p in projects])

@app.route('/api/projects', methods=['POST'])
@login_required
def create_project():
    try:
        data = request.json
        project = Project(
            name=data['name'],
            description=data.get('description', ''),
            created_by=current_user.id,
            status='active'
        )
        db.session.add(project)
        db.session.commit()
        
        team_member = TeamMember(project_id=project.id, user_id=current_user.id)
        db.session.add(team_member)
        db.session.commit()
        
        return jsonify({'message': 'Project created', 'project_id': project.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user.role != 'admin' and project.created_by != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': 'Project deleted'})

# Task APIs
@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    if current_user.role == 'admin':
        tasks = Task.query.all()
    else:
        tasks = Task.query.filter(
            (Task.assigned_to == current_user.id) | (Task.created_by == current_user.id)
        ).all()
    
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'description': t.description or 'No description',
        'status': t.status,
        'priority': t.priority,
        'due_date': t.due_date.isoformat(),
        'created_by': t.created_by,
        'assigned_to': t.assigned_to,
        'project_id': t.project_id,
        'project_name': t.project.name,
        'assignee_name': User.query.get(t.assigned_to).username if User.query.get(t.assigned_to) else 'Unknown',
        'creator_name': User.query.get(t.created_by).username if User.query.get(t.created_by) else 'Unknown',
        'is_overdue': t.due_date < datetime.now() and t.status != 'completed'
    } for t in tasks])

@app.route('/api/tasks', methods=['POST'])
@login_required
def create_task():
    try:
        data = request.json
        
        project = Project.query.get_or_404(data['project_id'])
        if current_user.role != 'admin' and project.created_by != current_user.id:
            team_member = TeamMember.query.filter_by(project_id=project.id, user_id=current_user.id).first()
            if not team_member:
                return jsonify({'error': 'Permission denied'}), 403
        
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            due_date=datetime.fromisoformat(data['due_date']),
            created_by=current_user.id,
            assigned_to=data['assigned_to'],
            project_id=data['project_id'],
            priority=data.get('priority', 'medium')
        )
        db.session.add(task)
        db.session.commit()
        return jsonify({'message': 'Task created', 'task_id': task.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user.role != 'admin' and task.assigned_to != current_user.id and task.created_by != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.json
    if 'status' in data:
        task.status = data['status']
    if 'priority' in data:
        task.priority = data['priority']
    
    if task.status == 'completed' and not task.completed_at:
        task.completed_at = datetime.now()
    
    db.session.commit()
    return jsonify({'message': 'Task updated'})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user.role != 'admin' and task.created_by != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'})

# Dashboard stats API
@app.route('/api/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    if current_user.role == 'admin':
        total_tasks = Task.query.count()
        completed_tasks = Task.query.filter_by(status='completed').count()
        pending_tasks = Task.query.filter_by(status='pending').count()
        in_progress_tasks = Task.query.filter_by(status='in-progress').count()
        overdue_tasks = Task.query.filter(Task.due_date < datetime.now(), Task.status != 'completed').count()
        total_projects = Project.query.count()
        total_users = User.query.count()
    else:
        tasks = Task.query.filter(
            (Task.assigned_to == current_user.id) | (Task.created_by == current_user.id)
        ).all()
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == 'completed')
        pending_tasks = sum(1 for t in tasks if t.status == 'pending')
        in_progress_tasks = sum(1 for t in tasks if t.status == 'in-progress')
        overdue_tasks = sum(1 for t in tasks if t.due_date < datetime.now() and t.status != 'completed')
        total_projects = Project.query.filter(
            (Project.created_by == current_user.id) | 
            (Project.id.in_([tm.project_id for tm in TeamMember.query.filter_by(user_id=current_user.id).all()]))
        ).count()
        total_users = 1
    
    return jsonify({
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'overdue_tasks': overdue_tasks,
        'total_projects': total_projects,
        'total_users': total_users,
        'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    })

@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    if current_user.role != 'admin':
        return jsonify([{
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'role': current_user.role
        }])
    
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'role': u.role
    } for u in users])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)