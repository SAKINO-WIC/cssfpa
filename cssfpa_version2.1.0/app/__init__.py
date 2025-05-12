from flask import Flask, redirect, url_for, request, g, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel
from config import Config
from datetime import datetime
import logging
from app.utils.translation import translate_text

# 初始化扩展
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
babel = Babel()

def get_locale():
    # 优先使用用户在会话中存储的语言偏好
    if 'language' in session:
        return session['language']
    # 回退到请求头中的语言偏好
    return request.accept_languages.best_match(Config.LANGUAGES)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 添加内置函数到Jinja2环境
    app.jinja_env.globals.update(max=max, min=min)
    # 添加翻译函数到Jinja2环境
    app.jinja_env.globals.update(_=lambda text: translate_text(text, get_locale()))
    
    # 设置CSRF保护
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_SECRET_KEY'] = app.config['SECRET_KEY']
    
    # 初始化Babel - 使用config方式设置locale_selector
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = Config.BABEL_TRANSLATION_DIRECTORIES
    app.config['BABEL_DEFAULT_LOCALE'] = Config.BABEL_DEFAULT_LOCALE
    babel.init_app(app, locale_selector=get_locale)
    
    # 设置日志
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger(__name__)
    
    # 注册请求前钩子，记录请求信息
    @app.before_request
    def log_request_info():
        app.logger.debug('请求: %s %s', request.method, request.path)
        app.logger.debug('请求头: %s', request.headers)
        # 保存请求路径历史到g对象，以跟踪重定向链
        if not hasattr(g, 'request_history'):
            g.request_history = []
        g.request_history.append(request.path)
        if len(g.request_history) > 10:  # 如果超过10次重定向，可能存在循环
            app.logger.error('可能存在重定向循环: %s', g.request_history)
    
    # 注册请求后钩子，记录响应信息
    @app.after_request
    def log_response_info(response):
        app.logger.debug('响应状态: %s', response.status_code)
        
        # 检测重定向
        if 300 <= response.status_code < 400:
            # 重定向目标
            redirect_to = response.headers.get('Location', '未知')
            app.logger.warning('重定向发生: %s -> %s', request.path, redirect_to)
            
            # 检查是否是自我重定向（同一URL重定向到自己）
            if redirect_to.endswith(request.path):
                app.logger.error('⚠️ 检测到自我重定向: %s -> %s', request.path, redirect_to)
            
            # 检查历史中是否已经有过这个目标，表示循环重定向
            if hasattr(g, 'request_history') and redirect_to in g.request_history:
                app.logger.error('⚠️ 检测到循环重定向: %s 在历史 %s 中已存在', 
                               redirect_to, g.request_history)
                # 紧急处理循环重定向 - 返回错误页面而不是继续重定向
                if redirect_to.startswith('/auth/login') and len(g.request_history) > 5:
                    # 如果是在登录页面发生循环，中断这一过程
                    app.logger.error('中断登录重定向循环，返回错误页面')
                    return render_template('errors/redirect_loop.html', 
                                          history=g.request_history), 500
        
        # 添加缓存控制头，禁止浏览器缓存页面，确保数据实时刷新
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # 设置登录视图
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    login_manager.login_message_category = 'info'
    
    # 添加防止循环重定向的安全机制
    app.config['MAX_REDIRECTS'] = 5  # 最大重定向次数
    
    # 添加自定义过滤器
    @app.template_filter('format_date')
    def format_date(value, format='%Y-%m'):
        """格式化日期，处理异常情况"""
        if value is None:
            return '未设置'
        try:
            if isinstance(value, str):
                return value
            return value.strftime(format)
        except Exception:
            return str(value)
    
    @app.template_filter('from_json')
    def from_json(value):
        """将JSON字符串转换为Python对象"""
        if not value:
            return []
        try:
            import json
            return json.loads(value)
        except Exception as e:
            app.logger.error(f"JSON解析错误: {e}")
            return []
    
    # 导入并注册蓝图
    from app.controllers.auth import auth_bp
    from app.controllers.student import student_bp
    from app.controllers.teacher import teacher_bp
    from app.controllers.admin import admin_bp
    from app.controllers.main import main_bp
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)
    app.logger.info('成功注册所有蓝图')
    
    # 注册自定义错误处理器
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
        
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # 防止重定向循环的额外检查
    @app.before_request
    def check_redirect_loop():
        """检查是否存在重定向循环"""
        if hasattr(g, 'request_history') and len(g.request_history) > app.config['MAX_REDIRECTS']:
            # 检查是否有重复访问的页面
            if len(set(g.request_history)) < len(g.request_history):
                app.logger.error('⚠️ 重定向循环检测: %s', g.request_history)
                # 重置用户会话作为应急措施
                if current_user.is_authenticated:
                    from flask_login import logout_user
                    logout_user()
                    app.logger.warning('已强制登出用户以打破重定向循环')
                return render_template('errors/redirect_loop.html', 
                                      history=g.request_history), 500
    
    @app.before_request
    def check_user_role():
        """检查用户角色权限，避免角色与URL不匹配引起的重定向循环"""
        # 跳过静态文件
        if request.path.startswith('/static'):
            return
        
        # 跳过错误页面
        if request.path.startswith('/errors'):
            return
        
        # 跳过登录/登出相关页面
        if request.path.startswith('/auth'):
            return
        
        # 只有已登录用户才需要检查
        if current_user.is_authenticated:
            app.logger.debug('当前用户: %s, 角色: %s, 访问: %s', 
                            current_user.username, current_user.role, request.path)
            
            # 检查路径是否与用户角色匹配
            if current_user.role == 'student' and request.path.startswith('/teacher'):
                app.logger.warning('学生用户尝试访问教师页面，重定向到学生首页')
                return redirect(url_for('student.index'))
            
            elif current_user.role == 'teacher' and request.path.startswith('/student'):
                app.logger.warning('教师用户尝试访问学生页面，重定向到教师首页')
                return redirect(url_for('teacher.index'))
            
            elif current_user.role == 'admin' and (request.path.startswith('/student') or request.path.startswith('/teacher')):
                app.logger.warning('管理员尝试访问学生/教师页面，重定向到管理员首页')
                return redirect(url_for('admin.index'))
    
    return app

# 用户加载函数
@login_manager.user_loader
def load_user(id):
    from app.models.user import User
    return User.query.get(int(id))