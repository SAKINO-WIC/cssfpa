from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, send_file, abort, Response, jsonify, session, send_from_directory
from datetime import datetime, timedelta
import os
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.student import Student, StudentFile
from app.models.user import User
from app.models.score_config import StudentScore
from app.models.file import File
import mimetypes
from flask_wtf import FlaskForm, Form
from wtforms import StringField, SelectField, FileField, BooleanField, DateField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Optional, Length, Email
import json
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from sqlalchemy.sql import func
from sqlalchemy import case, extract
import uuid

# 文件上传表单
class FileUploadForm(FlaskForm):
    file_type = SelectField('文件类型', choices=[
        ('award', '获奖证书'),
        ('certificate', '资格证书'),
        ('practice', '社会实践证明'),
        ('other', '其他材料')
    ])
    description = StringField('文件描述')
    file = FileField('选择文件')

# 学生编辑表单
class StudentEditForm(FlaskForm):
    # 个人基本信息
    name = StringField('姓名', validators=[DataRequired()])
    gender = SelectField('性别', choices=[('男', '男'), ('女', '女')], validators=[DataRequired()])
    ethnicity = StringField('民族')
    hometown = StringField('籍贯')
    birth_date = DateField('出生日期', format='%Y-%m-%d', validators=[Optional()])
    id_card = StringField('身份证号', validators=[Length(max=18)])
    phone = StringField('手机号码', validators=[Length(max=11)])
    email = StringField('电子邮箱', validators=[Optional(), Email()])
    
    # 学籍信息
    department = StringField('学院')
    major = StringField('专业')
    class_name = StringField('班级')
    
    # 政治信息
    political_status = SelectField('政治面貌', choices=[
        ('群众', '群众'),
        ('共青团员', '共青团员'),
        ('入党积极分子', '入党积极分子'),
        ('党员发展对象', '党员发展对象'),
        ('预备党员', '预备党员'),
        ('中共党员', '中共党员')
    ])
    league_member_id = StringField('团员编号')
    league_branch = StringField('团支部')
    join_league_date = DateField('入团时间', format='%Y-%m-%d', validators=[Optional()])
    has_application = BooleanField('是否递交入党申请书')
    application_date = DateField('递交入党申请书时间', format='%Y-%m-%d', validators=[Optional()])
    
    # 学业信息
    has_failed_course = BooleanField('是否有挂科')
    comprehensive_test_score = IntegerField('综测成绩', validators=[Optional()])
    cet4_score = IntegerField('英语四级成绩', validators=[Optional()])
    cet6_score = IntegerField('英语六级成绩', validators=[Optional()])
    volunteer_hours = IntegerField('志愿服务时长', validators=[Optional()])

student_bp = Blueprint('student', __name__, url_prefix='/student')

# 允许上传的文件类型
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}

# 学生权限装饰器
def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('无权限访问此页面', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_date(date_str):
    """转换日期字符串为datetime.date对象"""
    if not date_str:
        return None
    try:
        # 先尝试年月日格式
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        try:
            # 再尝试年月格式
            date_obj = datetime.strptime(date_str, '%Y-%m')
            return date_obj.date()
        except ValueError:
            return None

@student_bp.route('/')
@login_required
@student_required
def index():
    """学生首页"""
    # 获取学生信息
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash('您的学生信息不存在，请联系管理员', 'danger')
        return redirect(url_for('auth.logout'))
    
    # 获取学生的所有成绩
    try:
        scores = StudentScore.query.filter_by(student_id=student.id).all()
    except Exception as e:
        print(f"加载学生成绩时出错: {str(e)}")
        scores = []
    
    # 获取学生文件 - 使用File模型而不是StudentFile模型
    files = File.query.filter_by(user_id=current_user.id).all()
    
    # 处理入团时间
    join_date = "未设置"
    if student.league_join_date:
        try:
            join_date = student.league_join_date.strftime('%Y-%m-%d')
        except Exception as e:
            join_date = str(student.league_join_date)
    
    # 处理递交入党申请书时间
    app_date = "无"  # 默认为"无"
    if student.has_application:
        if student.application_date:
            try:
                app_date = student.application_date.strftime('%Y-%m-%d')
            except Exception as e:
                app_date = str(student.application_date)
    
    # 处理获奖情况数据
    awards = []
    if student.awards:
        try:
            awards = json.loads(student.awards)
        except Exception as e:
            print(f"解析奖项信息时出错: {str(e)}")
            awards = []
    
    # 处理社会实践数据
    practice_list = []
    if student.social_practice:
        try:
            practice_list = json.loads(student.social_practice)
        except Exception as e:
            print(f"解析社会实践信息时出错: {str(e)}")
            practice_list = []
            
    # 统计文件类型数量
    file_counts = {
        'award': sum(1 for f in files if f.file_type == 'award'),
        'certificate': sum(1 for f in files if f.file_type == 'certificate'),
        'practice': sum(1 for f in files if f.file_type == 'practice'),
        'other': sum(1 for f in files if f.file_type == 'other')
    }
    
    # 使用已解析的数据
    return render_template('student/index.html', 
                          student=student, 
                          scores=scores,
                          achievements=awards,
                          practices=practice_list,
                          join_date=join_date,
                          app_date=app_date,
                          awards=awards,
                          file_counts=file_counts)

@student_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if current_user.role != 'student':
        return render_template('errors/403.html'), 403
    
    student = Student.query.filter_by(student_id=current_user.username).first()
    if not student:
        flash('学生信息不存在', 'danger')
        return redirect(url_for('student.index'))
    
    # 创建专门的学生编辑表单
    form = StudentEditForm()
    
    # 处理获奖情况数据
    awards = []
    if student.awards:
        try:
            awards = json.loads(student.awards)
        except Exception as e:
            print(f"解析奖项信息时出错: {str(e)}")
    
    # 处理社会实践数据
    practices = []
    if student.social_practice:
        try:
            practices = json.loads(student.social_practice)
        except Exception as e:
            print(f"解析社会实践信息时出错: {str(e)}")
    
    # GET请求：用学生数据填充表单
    if request.method == 'GET':
        form.name.data = student.name
        form.gender.data = student.gender
        form.ethnicity.data = student.ethnicity
        form.hometown.data = student.hometown
        form.birth_date.data = student.birth_date
        form.id_card.data = student.id_card
        form.phone.data = student.phone
        form.email.data = student.email
        
        form.department.data = student.department
        form.major.data = student.major
        form.class_name.data = student.class_name
        
        form.political_status.data = student.political_status
        form.league_member_id.data = student.league_member_id
        form.league_branch.data = student.league_branch
        form.join_league_date.data = student.league_join_date
        form.has_application.data = student.has_application
        form.application_date.data = student.application_date
        
        form.has_failed_course.data = student.has_failed_course
        form.comprehensive_test_score.data = student.comprehensive_test_score
        form.cet4_score.data = student.cet4_score
        form.cet6_score.data = student.cet6_score
        form.volunteer_hours.data = student.volunteer_hours
    
    # POST请求：处理表单提交
    if form.validate_on_submit():
        try:
            # 基本信息更新
            student.name = form.name.data
            student.gender = form.gender.data
            student.ethnicity = form.ethnicity.data
            student.hometown = form.hometown.data
            student.birth_date = form.birth_date.data
            student.id_card = form.id_card.data
            student.phone = form.phone.data
            student.email = form.email.data
            
            # 学籍信息更新
            student.department = form.department.data
            student.major = form.major.data
            student.class_name = form.class_name.data
            
            # 政治面貌信息更新
            student.political_status = form.political_status.data
            student.league_member_id = form.league_member_id.data
            student.league_branch = form.league_branch.data
            student.league_join_date = form.join_league_date.data
            student.has_application = form.has_application.data
            student.application_date = form.application_date.data
            
            # 不再是团员，清空团员加入日期
            if student.political_status != '共青团员' and student.political_status != '中共党员':
                student.league_join_date = None
            
            # 学业信息更新
            student.has_failed_course = form.has_failed_course.data
            student.comprehensive_test_score = form.comprehensive_test_score.data
            student.cet4_score = form.cet4_score.data
            student.cet6_score = form.cet6_score.data
            student.volunteer_hours = form.volunteer_hours.data
            
            # 获奖信息 (JSON 格式) - 这部分通过表单的隐藏字段提交
            awards_json = request.form.get('awards', '')
            if awards_json:
                try:
                    # 尝试验证JSON格式
                    json.loads(awards_json)
                    student.awards = awards_json
                except json.JSONDecodeError:
                    flash('获奖信息格式不正确，请使用有效的JSON格式', 'danger')
                    return render_template('student/edit.html', student=student, form=form, awards=awards, practices=practices)
            else:
                student.awards = None
            
            # 社会实践经历 (JSON 格式) - 这部分通过表单的隐藏字段提交
            social_practice_json = request.form.get('social_practice', '')
            if social_practice_json:
                try:
                    # 尝试验证JSON格式
                    json.loads(social_practice_json)
                    student.social_practice = social_practice_json
                except json.JSONDecodeError:
                    flash('社会实践经历格式不正确，请使用有效的JSON格式', 'danger')
                    return render_template('student/edit.html', student=student, form=form, awards=awards, practices=practices)
            else:
                student.social_practice = None
            
            db.session.commit()
            flash('个人信息更新成功', 'success')
            return redirect(url_for('student.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'danger')
    
    return render_template('student/edit.html', student=student, form=form, awards=awards, practices=practices)

@student_bp.route('/my_files', methods=['GET', 'POST'])
@login_required
@student_required
def my_files():
    """学生文件管理页面"""
    # 创建文件上传表单
    form = FileUploadForm()
    
    # 处理POST请求（文件上传）
    if request.method == 'POST':
        # 检查是否为AJAX请求
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.form.get('is_ajax') == 'true'
        
        if 'file' not in request.files:
            flash('没有选择文件', 'danger')
            if is_ajax:
                return jsonify({'status': 'error', 'message': '没有选择文件'}), 400
            return redirect(url_for('student.my_files'))
        
        file = request.files['file']
        if file.filename == '':
            flash('没有选择文件', 'danger')
            if is_ajax:
                return jsonify({'status': 'error', 'message': '没有选择文件'}), 400
            return redirect(url_for('student.my_files'))
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_type = request.form.get('file_type', '其他')
            description = request.form.get('description', '')
            
            # 确保上传目录存在 - 使用用户ID作为目录名
            upload_dir = os.path.join(current_app.root_path, 'uploads', str(current_user.id))
            os.makedirs(upload_dir, exist_ok=True)
            
            # 使用UUID生成唯一文件名避免冲突
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            
            # 保存文件记录到数据库
            new_file = File(
                user_id=current_user.id,
                filename=unique_filename,
                original_filename=filename,
                file_type=file_type,
                description=description,
                file_path=os.path.join('uploads', str(current_user.id), unique_filename),
                file_size=file_size
            )
            db.session.add(new_file)
            db.session.commit()
            
            flash('文件上传成功！', 'success')
            
            # 如果是AJAX请求，返回JSON响应
            if is_ajax:
                return jsonify({
                    'status': 'success',
                    'message': '文件上传成功！',
                    'file_id': new_file.id,
                    'redirect_url': url_for('student.my_files')
                })
        else:
            flash('不支持的文件类型', 'danger')
            if is_ajax:
                return jsonify({'status': 'error', 'message': '不支持的文件类型'}), 400
    
    # 获取当前用户的所有文件（无论是GET还是POST请求都需要）
    files = File.query.filter_by(user_id=current_user.id).order_by(File.upload_date.desc()).all()
    
    # 渲染带有侧边栏的完整页面
    return render_template('student/my_files.html', files=files, form=form)

@student_bp.route('/my_files_content')
@login_required
@student_required
def my_files_content():
    """加载文件管理页面内容部分（用于AJAX请求）"""
    # 获取当前用户的所有文件
    files = File.query.filter_by(user_id=current_user.id).order_by(File.upload_date.desc()).all()
    # 创建文件上传表单
    form = FileUploadForm()
    return render_template('student/my_files_content.html', files=files, form=form)

@student_bp.route('/upload', methods=['POST'])
@login_required
@student_required
def upload_file():
    """上传文件处理"""
    # 检查请求是否来自AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if 'file' not in request.files:
        flash('没有选择文件', 'danger')
        if is_ajax:
            return jsonify({'status': 'error', 'message': '没有选择文件'}), 400
        return redirect(url_for('student.my_files'))
    
    file = request.files['file']
    if file.filename == '':
        flash('没有选择文件', 'danger')
        if is_ajax:
            return jsonify({'status': 'error', 'message': '没有选择文件'}), 400
        return redirect(url_for('student.my_files'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_type = request.form.get('file_type', '其他')
        description = request.form.get('description', '')
        
        # 确保上传目录存在 - 使用用户ID作为目录名
        upload_dir = os.path.join(current_app.root_path, 'uploads', str(current_user.id))
        os.makedirs(upload_dir, exist_ok=True)
        
        # 使用UUID生成唯一文件名避免冲突
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 保存文件记录到数据库
        new_file = File(
            user_id=current_user.id,
            filename=unique_filename,
            original_filename=filename,
            file_type=file_type,
            description=description,
            file_path=os.path.join('uploads', str(current_user.id), unique_filename),
            file_size=file_size
        )
        db.session.add(new_file)
        db.session.commit()
        
        flash('文件上传成功！', 'success')
        
        # 如果是AJAX请求，返回JSON响应
        if is_ajax:
            return jsonify({
                'status': 'success',
                'message': '文件上传成功！',
                'file_id': new_file.id,
                'redirect_url': url_for('student.my_files')  # 添加重定向URL
            })
    else:
        flash('不支持的文件类型', 'danger')
        if is_ajax:
            return jsonify({
                'status': 'error',
                'message': '不支持的文件类型'
            }), 400
    
    # 无论是否是AJAX请求，都重定向到my_files路由（带有侧边栏的完整页面）
    return redirect(url_for('student.my_files'))

@student_bp.route('/download/<int:file_id>')
@login_required
@student_required
def download_file(file_id):
    """下载文件"""
    # 获取文件记录
    user_file = File.query.get_or_404(file_id)
    
    # 确保用户只能下载自己的文件
    if user_file.user_id != current_user.id:
        return render_template('errors/403.html'), 403
    
    file_path = os.path.join(current_app.root_path, user_file.file_path)
    if not os.path.exists(file_path):
        flash('文件不存在或已被删除', 'danger')
        return redirect(url_for('student.my_files'))
        
    return send_file(file_path, as_attachment=True, download_name=user_file.original_filename)

@student_bp.route('/delete/<int:file_id>')
@login_required
@student_required
def delete_file(file_id):
    """删除文件"""
    # 获取文件记录
    user_file = File.query.get_or_404(file_id)
    
    # 确保用户只能删除自己的文件
    if user_file.user_id != current_user.id:
        return render_template('errors/403.html'), 403
    
    # 删除物理文件
    file_path = os.path.join(current_app.root_path, user_file.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 删除数据库记录
    db.session.delete(user_file)
    db.session.commit()
    
    # 检查是否为AJAX请求
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if is_ajax:
        # 返回JSON响应
        return jsonify({
            'status': 'success',
            'message': '文件已成功删除'
        })
    else:
        # 常规请求返回重定向
        flash('文件已成功删除', 'success')
        return redirect(url_for('student.my_files'))

@student_bp.route('/preview/<int:file_id>')
@login_required
@student_required
def preview_file(file_id):
    """预览文件内容"""
    # 获取文件记录
    user_file = File.query.get_or_404(file_id)
    
    # 确保用户只能预览自己的文件
    if user_file.user_id != current_user.id:
        return render_template('errors/403.html'), 403
    
    file_path = os.path.join(current_app.root_path, user_file.file_path)
    if not os.path.exists(file_path):
        flash('文件不存在或已被删除', 'danger')
        return redirect(url_for('student.my_files'))
    
    # 获取文件扩展名和MIME类型
    file_ext = os.path.splitext(user_file.original_filename)[1].lower()
    mime_type = mimetypes.guess_type(file_path)[0]
    
    # 根据文件类型处理预览
    if file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
        # 图片直接在页面中显示
        return render_template('student/preview_image.html', file=user_file, mime_type=mime_type)
    elif file_ext == '.pdf':
        # PDF使用PDF.js预览
        return render_template('student/preview_pdf.html', file=user_file)
    elif file_ext in ['.doc', '.docx', '.txt']:
        # 文档文件使用Office Online或Google Docs预览
        return render_template('student/preview_document.html', file=user_file)
    else:
        # 其他类型文件无法预览，提示用户下载
        flash('该文件类型暂不支持在线预览，请下载后查看', 'warning')
        return redirect(url_for('student.download_file', file_id=file_id))

@student_bp.route('/preview-content/<int:file_id>')
@login_required
@student_required
def preview_file_content(file_id):
    """直接提供文件内容，用于内嵌预览"""
    # 获取文件记录
    user_file = File.query.get_or_404(file_id)
    
    # 确保用户只能预览自己的文件
    if user_file.user_id != current_user.id:
        abort(403)
    
    file_path = os.path.join(current_app.root_path, user_file.file_path)
    if not os.path.exists(file_path):
        flash('文件不存在或已被删除', 'danger')
        return redirect(url_for('student.my_files'))
    
    # 获取MIME类型
    mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    
    # 返回文件内容
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    return Response(file_content, mimetype=mime_type)

@student_bp.route('/init-sample-achievements')
@login_required
def init_sample_achievements():
    if current_user.role != 'student':
        return render_template('errors/403.html'), 403
    
    student = Student.query.filter_by(student_id=current_user.username).first()
    if not student:
        flash('学生信息不存在', 'danger')
        return redirect(url_for('student.index'))
    
    # 初始化示例获奖情况
    awards_data = [
        {
            "name": "三好学生",
            "level": "校级",
            "organization": "天津师范大学",
            "date": "2022-06-10"
        },
        {
            "name": "优秀团员",
            "level": "院级",
            "organization": "计算机科学与技术学院",
            "date": "2023-05-04"
        }
    ]
    
    # 初始化示例社会实践经历
    practice_data = [
        {
            "title": "暑期社会实践活动",
            "organization": "天津市红十字会",
            "start_date": "2022-07-05",
            "end_date": "2022-08-10",
            "description": "参与社区防疫宣传和志愿服务工作，累计服务时长80小时"
        },
        {
            "title": "校园文化节志愿者",
            "organization": "校团委学生会",
            "start_date": "2023-04-15",
            "end_date": "2023-04-20",
            "description": "负责校园文化节的场地布置和活动引导工作"
        }
    ]
    
    # 将数据转换为JSON并保存到数据库
    student.awards = json.dumps(awards_data, ensure_ascii=False)
    student.social_practice = json.dumps(practice_data, ensure_ascii=False)
    
    try:
        db.session.commit()
        flash('示例成就经历数据初始化成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'数据初始化失败: {str(e)}', 'danger')
    
    return redirect(url_for('student.index'))

@student_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if current_user.role != 'student':
        return render_template('errors/403.html'), 403
    
    form = FlaskForm()
    if request.method == 'POST' and form.validate_on_submit():
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        user = User.query.get(current_user.id)
        
        if not check_password_hash(user.password_hash, old_password):
            flash('原密码不正确', 'danger')
            return render_template('student/change_password.html', form=form)
        
        if new_password != confirm_password:
            flash('两次输入的新密码不一致', 'danger')
            return render_template('student/change_password.html', form=form)
        
        if len(new_password) < 6:
            flash('新密码长度不能少于6个字符', 'danger')
            return render_template('student/change_password.html', form=form)
        
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        flash('密码修改成功', 'success')
        return redirect(url_for('student.index'))
    
    return render_template('student/change_password.html', form=form)

@student_bp.route('/personal_info_content')
@login_required
@student_required
def personal_info_content():
    """加载个人信息中心内容部分（用于AJAX请求）"""
    # 获取学生信息
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return '<div class="alert alert-danger">无法找到您的学生信息，请联系管理员</div>'
    
    # 获取学生的所有成绩
    try:
        scores = StudentScore.query.filter_by(student_id=student.id).all()
    except Exception as e:
        print(f"加载学生成绩时出错: {str(e)}")
        scores = []
    
    # 处理入团时间
    join_date = "未设置"
    if student.league_join_date:
        try:
            join_date = student.league_join_date.strftime('%Y-%m-%d')
        except Exception as e:
            join_date = str(student.league_join_date)
    
    # 处理递交入党申请书时间
    app_date = "无"  # 默认为"无"
    if student.has_application:
        if student.application_date:
            try:
                app_date = student.application_date.strftime('%Y-%m-%d')
            except Exception as e:
                app_date = str(student.application_date)
    
    # 处理获奖情况数据
    awards = []
    if student.awards:
        try:
            awards = json.loads(student.awards)
        except Exception as e:
            print(f"解析奖项信息时出错: {str(e)}")
            awards = []
    
    # 处理社会实践数据
    practice_list = []
    if student.social_practice:
        try:
            practice_list = json.loads(student.social_practice)
        except Exception as e:
            print(f"解析社会实践信息时出错: {str(e)}")
            practice_list = []
    
    return render_template('student/personal_info_content.html', 
                          student=student, 
                          scores=scores,
                          awards=awards,
                          practices=practice_list,
                          join_date=join_date,
                          app_date=app_date)