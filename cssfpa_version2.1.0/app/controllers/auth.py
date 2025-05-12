from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.forms import LoginForm
from app.models.user import User
from datetime import datetime
from flask_babel import _

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'student':
            return redirect(url_for('student.index'))
        elif current_user.role == 'teacher':
            return redirect(url_for('teacher.index'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data) or user.role != form.role.data:
            flash(_('用户名或密码错误，或所选角色与账号不匹配'), 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            if user.role == 'student':
                next_page = url_for('student.index')
            elif user.role == 'teacher':
                next_page = url_for('teacher.index')
            elif user.role == 'admin':
                next_page = url_for('admin.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', title=_('登录'), form=form, now=datetime.now())

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    # 暂时实现为提示功能
    flash(_('密码重置功能即将推出，请联系管理员重置密码'), 'info')
    return redirect(url_for('auth.login'))