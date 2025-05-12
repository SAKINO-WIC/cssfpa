from flask import Blueprint, redirect, url_for, render_template, current_app, session, request
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """主页路由，根据用户角色重定向到对应的首页"""
    current_app.logger.info('访问主页，用户认证状态：%s', current_user.is_authenticated)
    
    if current_user.is_authenticated:
        # 根据用户角色重定向到对应的首页
        if current_user.role == 'student':
            return redirect(url_for('student.index'))
        elif current_user.role == 'teacher':
            return redirect(url_for('teacher.index'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin.index'))
        else:
            current_app.logger.warning('未知用户角色：%s', current_user.role)
            return redirect(url_for('auth.login'))
    else:
        # 未登录用户重定向到登录页
        return redirect(url_for('auth.login'))

@main_bp.route('/set-language/<lang>')
def set_language(lang):
    """设置用户界面语言"""
    # 检验语言是否在支持的语言列表中
    if lang in current_app.config['LANGUAGES']:
        session['language'] = lang
        current_app.logger.info('用户语言已设置为: %s', lang)
    else:
        current_app.logger.warning('尝试设置不支持的语言: %s', lang)
    
    # 返回到用户来源页面，如果没有来源则返回主页
    return redirect(request.referrer or url_for('main.index')) 