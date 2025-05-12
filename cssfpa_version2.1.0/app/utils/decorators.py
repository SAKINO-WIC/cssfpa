from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user

def teacher_required(f):
    """
    确保只有教师角色可以访问该路由的装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'teacher':
            abort(403)  # 禁止访问
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    确保只有管理员角色可以访问该路由的装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)  # 禁止访问
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    """
    确保只有学生角色可以访问该路由的装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            abort(403)  # 禁止访问
        return f(*args, **kwargs)
    return decorated_function 