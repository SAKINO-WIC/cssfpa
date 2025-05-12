from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models.user import User
from app.models.student import Student
from app.utils.decorators import admin_required
from app import db
from flask_wtf.csrf import generate_csrf

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
@admin_required
def index():
    """管理员控制面板页面"""
    users = User.query.all()
    return render_template('admin/index.html', users=users)

@admin_bp.route('/api/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    """获取所有用户的API"""
    try:
        users = User.query.all()
        users_data = []
        for user in users:
            user_data = {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '从未登录'
            }
            users_data.append(user_data)
        return jsonify(users_data)
    except Exception as e:
        return jsonify({'error': f'获取用户列表失败: {str(e)}'}), 500

@admin_bp.route('/api/users/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def get_user(user_id):
    """获取单个用户详情的API"""
    try:
        user = User.query.get_or_404(user_id)
        user_data = {
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '从未登录'
        }
        
        # 如果是学生用户，获取关联的学生信息
        if user.role == 'student' and user.student:
            student = user.student
            user_data['student'] = {
                'id': student.id,
                'student_id': student.student_id,
                'name': student.name,
                'class_name': student.class_name,
                'department': student.department,
                'major': student.major
            }
        
        return jsonify(user_data)
    except Exception as e:
        return jsonify({'error': f'获取用户详情失败: {str(e)}'}), 500

@admin_bp.route('/api/users', methods=['POST'])
@login_required
@admin_required
def add_user():
    """添加新用户的API"""
    try:
        data = request.json
        
        # 验证数据
        if not data or not data.get('username') or not data.get('role') or not data.get('password'):
            return jsonify({'success': False, 'message': '缺少必要的用户信息'}), 400
        
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        
        # 创建新用户
        user = User(username=data['username'], role=data['role'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        
        # 如果是学生，创建关联的学生记录
        if data['role'] == 'student' and data.get('student_info'):
            student_info = data['student_info']
            student = Student(
                student_id=data['username'],
                name=student_info.get('name', '未命名'),
                class_name=student_info.get('class_name', ''),
                department=student_info.get('department', ''),
                major=student_info.get('major', ''),
                user_id=user.id
            )
            db.session.add(student)
            db.session.commit()
        
        # 返回成功信息和CSRF token
        return jsonify({
            'success': True, 
            'message': '用户添加成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role
            },
            'csrf_token': generate_csrf()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加用户失败: {str(e)}'}), 500

@admin_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
def update_user(user_id):
    """更新用户信息的API"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.json
        
        # 验证数据
        if not data:
            return jsonify({'success': False, 'message': '没有提供数据'}), 400
        
        # 更新用户基本信息
        if 'username' in data and data['username'] != user.username:
            # 检查新用户名是否已存在
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'success': False, 'message': '用户名已存在'}), 400
            user.username = data['username']
        
        if 'role' in data and data['role'] != user.role:
            # 如果从学生变为其他角色，处理关联的学生记录
            if user.role == 'student' and data['role'] != 'student':
                if user.student:
                    student = user.student
                    db.session.delete(student)
            user.role = data['role']
        
        # 如果提供了新密码，更新密码
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        # 更新学生信息（如果适用）
        if user.role == 'student' and data.get('student_info'):
            student_info = data['student_info']
            student = user.student
            
            # 如果学生记录不存在，创建新的
            if not student:
                student = Student(
                    student_id=user.username,
                    user_id=user.id
                )
                db.session.add(student)
            
            # 更新学生信息
            if 'name' in student_info:
                student.name = student_info['name']
            if 'class_name' in student_info:
                student.class_name = student_info['class_name']
            if 'department' in student_info:
                student.department = student_info['department']
            if 'major' in student_info:
                student.major = student_info['major']
        
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': '用户信息更新成功',
            'csrf_token': generate_csrf()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新用户失败: {str(e)}'}), 500

@admin_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    """删除用户的API"""
    try:
        user = User.query.get_or_404(user_id)
        
        # 不允许删除唯一的管理员账户
        if user.role == 'admin' and User.query.filter_by(role='admin').count() <= 1:
            return jsonify({'success': False, 'message': '无法删除唯一的管理员账户'}), 400
        
        # 如果是学生，同时删除关联的学生记录
        if user.role == 'student' and user.student:
            db.session.delete(user.student)
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': '用户删除成功',
            'csrf_token': generate_csrf()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除用户失败: {str(e)}'}), 500

@admin_bp.route('/api/csrf-token', methods=['GET'])
@login_required
@admin_required
def get_csrf_token():
    """获取CSRF令牌"""
    return jsonify({'csrf_token': generate_csrf()})

@admin_bp.route('/users')
@login_required
@admin_required
def user_management():
    """用户管理页面"""
    users = User.query.all()
    return render_template('admin/user_management.html', users=users)

@admin_bp.route('/students')
@login_required
@admin_required
def student_management():
    """学生管理页面"""
    students = Student.query.all()
    return render_template('admin/student_management.html', students=students) 