from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, abort
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
import datetime
import pandas as pd
import os
import json
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from flask_wtf import FlaskForm
from sqlalchemy import func, distinct, case
from app.utils.decorators import teacher_required

from app.models.student import Student
from app.models.user import User
from app.models.score_config import ScoreConfig, StudentScore
from app.forms.teacher import StudentSearchForm, StudentFilterForm, StudentForm, ImportStudentsForm
from app.services.score_service import ScoreService
from app import db

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

# 简单的删除表单，只用于CSRF保护
class DeleteForm(FlaskForm):
    pass

@teacher_bp.before_request
@login_required
def before_request():
    if current_user.role != 'teacher':
        abort(403)  # 禁止访问，如果不是教师

@teacher_bp.route('/')
def index():
    """教师主页，显示学生列表"""
    search_form = StudentSearchForm()
    filter_form = StudentFilterForm()
    import_form = ImportStudentsForm()  # 添加导入表单实例
    
    # 获取所有学院并填充过滤表单的学院选项
    departments = Student.query.with_entities(Student.department).distinct().all()
    department_choices = [('', '全部')]
    
    for dept_result in departments:
        if hasattr(dept_result, 'department'):
            dept = dept_result.department
        elif isinstance(dept_result, tuple) and len(dept_result) > 0:
            dept = dept_result[0]
        else:
            continue
            
        if dept:
            department_choices.append((dept, dept))
    
    filter_form.department.choices = department_choices
    
    # 获取所有班级并填充过滤表单的班级选项
    class_names = Student.query.with_entities(Student.class_name).distinct().all()
    class_name_choices = [('', '全部')]
    
    for class_result in class_names:
        if hasattr(class_result, 'class_name'):
            class_name = class_result.class_name
        elif isinstance(class_result, tuple) and len(class_result) > 0:
            class_name = class_result[0]
        else:
            continue
            
        if class_name:
            class_name_choices.append((class_name, class_name))
    
    filter_form.class_name.choices = class_name_choices
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 限制每页显示数量在合理范围内
    per_page = min(max(per_page, 10), 100)
    
    # 分页查询，按照comprehensive_score降序排序
    students_pagination = Student.query.order_by(Student.comprehensive_score.desc()).paginate(page=page, per_page=per_page, error_out=False)
    students = students_pagination.items
    students_total = students_pagination.total
    pages = students_pagination.pages
    
    # 统计数据
    total_students = Student.query.count()
    # 已提交入党申请书的学生数
    submitted_count = Student.query.filter(Student.has_application == True).count()
    # 已通过初党考试的学生数
    passed_exam_count = Student.query.filter(Student.passed_exam == True).count()
    
    # 计算班级推优通过率
    class_approved_count = Student.query.filter(Student.class_approved == True).count()
    class_approval_rate = round((class_approved_count / total_students * 100) if total_students > 0 else 0)
    
    return render_template('teacher/index.html', 
                          students=students,
                          students_total=students_total, 
                          page=page,
                          per_page=per_page,
                          pages=pages,
                          search_form=search_form,
                          filter_form=filter_form,
                          form=import_form,
                          total_students=total_students,
                          submitted_count=submitted_count,
                          passed_exam_count=passed_exam_count,
                          class_approval_rate=class_approval_rate)  # 传递统计数据给模板

@teacher_bp.route('/student/<string:student_id>')
@login_required
@teacher_required
def view_student(student_id):
    """查看学生详细信息"""
    student = Student.query.filter_by(student_id=student_id).first_or_404()
    return render_template('teacher/student_view.html', student=student)

@teacher_bp.route('/add', methods=['GET', 'POST'])
@login_required
@teacher_required
def add_student():
    form = StudentForm()
    
    # 确保league_member_id没有默认值
    if request.method == 'GET' and form.league_member_id.data:
        form.league_member_id.data = None
        
    if form.validate_on_submit():
        # 检查学号是否已经存在
        if Student.query.filter_by(student_id=form.student_id.data).first():
            flash('此学号已经存在', 'danger')
            return render_template('teacher/student_add.html', form=form)
            
        # 创建用户账户
        user = User(username=form.student_id.data, role='student')
        
        # 设置密码，如果表单中提供了密码则使用表单密码，否则使用学号后6位
        if form.password.data and form.password.data.strip():
            user.set_password(form.password.data.strip())
            current_app.logger.info(f"为学生 {form.student_id.data} 设置自定义密码")
        else:
            default_password = form.student_id.data[-6:]
            user.set_password(default_password)
            current_app.logger.info(f"为学生 {form.student_id.data} 设置默认密码（学号后6位：{default_password}）")
        
        db.session.add(user)
        
        # 创建学生信息
        student = Student(
            student_id=form.student_id.data,
            name=form.name.data,
            gender=form.gender.data,
            class_name=form.class_name.data,
            political_status=form.political_status.data,
            enrollment_date=form.enrollment_date.data,
            id_card=form.id_card.data,
            phone=form.phone.data,
            email=form.email.data,
            dormitory=form.dormitory.data,
            department=form.department.data,
            major=form.major.data,
            user=user,
            league_member_id=form.league_member_id.data if form.league_member_id.data else None
        )
        
        # 保存学生信息
        db.session.add(student)
        
        try:
            db.session.commit()
            flash('学生添加成功', 'success')
            return redirect(url_for('teacher.index'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"保存学生信息时出错: {str(e)}")
            flash(f'保存失败: {str(e)}', 'danger')
    
    return render_template('teacher/student_add.html', form=form)

@teacher_bp.route('/student/edit/<string:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    """编辑学生信息"""
    student = Student.query.filter_by(student_id=student_id).first_or_404()
    form = StudentForm(obj=student)
    
    # 处理表单提交
    if form.validate_on_submit():
        try:
            # 记录原始数据，用于日志记录
            old_data = student.to_dict()
            
            # 更新学生信息
            form.populate_obj(student)
            
            # 确保复选框字段正确处理，防止NoneType错误
            student.has_application = bool(form.has_application.data)
            student.passed_exam = bool(form.passed_exam.data)
            student.class_approved = bool(form.class_approved.data)
            student.has_failed_course = bool(form.has_failed_course.data)
            
            # 对数字字段进行验证和转换
            if form.comprehensive_test_score.data is not None:
                student.comprehensive_test_score = min(100, max(0, form.comprehensive_test_score.data))
                
            if form.cet4_score.data is not None:
                student.cet4_score = min(710, max(0, form.cet4_score.data))
                
            if form.cet6_score.data is not None:
                student.cet6_score = min(710, max(0, form.cet6_score.data))
                
            if form.volunteer_hours.data is not None:
                student.volunteer_hours = max(0, form.volunteer_hours.data)
            
            # 提交事务
            db.session.commit()
            
            # 记录修改的字段
            new_data = student.to_dict()
            changes = {key: (old_data.get(key), new_data.get(key)) 
                      for key in new_data if new_data.get(key) != old_data.get(key)}
            
            current_app.logger.info(
                f"教师 {current_user.username} 更新了学生 {student.student_id} 的信息，修改了以下字段: {changes}"
            )
            
            flash('学生信息更新成功', 'success')
            return redirect(url_for('teacher.view_student', student_id=student.student_id))
            
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"更新学生 {student_id} 信息出错 (完整性错误): {str(e)}")
            flash('更新失败，请检查输入信息，可能有重复的学号或其他数据完整性问题', 'danger')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"更新学生 {student_id} 信息出错 (未知错误): {str(e)}")
            flash(f'更新失败: {str(e)}', 'danger')
    elif form.errors:
        # 记录表单验证错误
        current_app.logger.warning(f"学生 {student_id} 编辑表单验证失败: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')
    
    return render_template('teacher/student_edit.html', form=form, student=student)

@teacher_bp.route('/student/delete/<string:student_id>', methods=['GET', 'POST'])
def delete_student(student_id):
    """删除学生记录"""
    # 创建删除表单用于CSRF保护
    form = DeleteForm()
    
    # 如果是GET请求，显示确认页面
    if request.method == 'GET':
        student = Student.query.filter_by(student_id=student_id).first_or_404()
        return render_template('teacher/student_delete.html', form=form, student=student)
    
    # 如果是POST请求且表单有效，执行删除
    if form.validate_on_submit():
        student = Student.query.filter_by(student_id=student_id).first_or_404()
        user = User.query.get(student.user_id)
        
        try:
            # 删除学生记录
            db.session.delete(student)
            
            # 如果用户存在，也删除用户账号
            if user:
                db.session.delete(user)
                
            db.session.commit()
            flash('学生删除成功', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"删除学生失败: {e}")
            flash('删除学生失败', 'danger')
    else:
        flash('表单验证失败，可能是CSRF令牌无效', 'danger')
    
    return redirect(url_for('teacher.index'))

@teacher_bp.route('/student/search', methods=['GET'])
def search_students():
    """搜索学生"""
    search_form = StudentSearchForm()
    filter_form = StudentFilterForm()
    import_form = ImportStudentsForm()  # 添加导入表单实例
    
    # 获取所有学院并填充过滤表单的学院选项
    departments = Student.query.with_entities(Student.department).distinct().all()
    department_choices = [('', '全部')]
    
    for dept_result in departments:
        if hasattr(dept_result, 'department'):
            dept = dept_result.department
        elif isinstance(dept_result, tuple) and len(dept_result) > 0:
            dept = dept_result[0]
        else:
            continue
            
        if dept:
            department_choices.append((dept, dept))
    
    filter_form.department.choices = department_choices
    
    # 获取所有班级并填充过滤表单的班级选项
    class_names = Student.query.with_entities(Student.class_name).distinct().all()
    class_name_choices = [('', '全部')]
    
    for class_result in class_names:
        if hasattr(class_result, 'class_name'):
            class_name = class_result.class_name
        elif isinstance(class_result, tuple) and len(class_result) > 0:
            class_name = class_result[0]
        else:
            continue
            
        if class_name:
            class_name_choices.append((class_name, class_name))
    
    filter_form.class_name.choices = class_name_choices
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 限制每页显示数量
    per_page = min(max(per_page, 10), 100)
    
    # 获取搜索关键词
    query_term = request.args.get('query', '').strip()
    
    if query_term:
        # 构建搜索查询
        query = Student.query.filter(
            (Student.student_id.like(f'%{query_term}%')) | 
            (Student.name.like(f'%{query_term}%'))
        )
            
        # 添加排序：按照综合评分降序排序
        query = query.order_by(Student.comprehensive_score.desc())
            
        # 执行分页查询
        students_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        students = students_pagination.items
        students_total = students_pagination.total
        pages = students_pagination.pages
        
        # 统计数据
        total_students = Student.query.count()
        submitted_count = Student.query.filter(Student.has_application == True).count()
        passed_exam_count = Student.query.filter(Student.passed_exam == True).count()
        
        # 计算班级推优通过率
        class_approved_count = Student.query.filter(Student.class_approved == True).count()
        class_approval_rate = round((class_approved_count / total_students * 100) if total_students > 0 else 0)
        
        return render_template('teacher/index.html', 
                              students=students,
                              students_total=students_total,
                              page=page,
                              per_page=per_page,
                              pages=pages,
                              search_form=search_form,
                              filter_form=filter_form,
                              form=import_form,
                              total_students=total_students,
                              submitted_count=submitted_count,
                              passed_exam_count=passed_exam_count,
                              class_approval_rate=class_approval_rate)
    
    return redirect(url_for('teacher.index'))

@teacher_bp.route('/student/filter', methods=['GET', 'POST'])
def filter_students():
    """筛选学生"""
    search_form = StudentSearchForm()
    filter_form = StudentFilterForm()
    import_form = ImportStudentsForm()  # 添加导入表单实例
    
    # 获取所有学院并填充过滤表单的学院选项
    departments = Student.query.with_entities(Student.department).distinct().all()
    department_choices = [('', '全部')]
    
    for dept_result in departments:
        if hasattr(dept_result, 'department'):
            dept = dept_result.department
        elif isinstance(dept_result, tuple) and len(dept_result) > 0:
            dept = dept_result[0]
        else:
            continue
            
        if dept:
            department_choices.append((dept, dept))
    
    filter_form.department.choices = department_choices
    
    # 获取所有班级并填充过滤表单的班级选项
    class_names = Student.query.with_entities(Student.class_name).distinct().all()
    class_name_choices = [('', '全部')]
    
    for class_result in class_names:
        if hasattr(class_result, 'class_name'):
            class_name = class_result.class_name
        elif isinstance(class_result, tuple) and len(class_result) > 0:
            class_name = class_result[0]
        else:
            continue
            
        if class_name:
            class_name_choices.append((class_name, class_name))
    
    filter_form.class_name.choices = class_name_choices
    
    # 定义筛选参数，优先从request取值
    selected_department = ''
    selected_class = ''
    selected_score_range = ''
    
    # 处理筛选参数，优先从form取值，其次从args取值
    if request.method == 'POST':
        selected_department = request.form.get('department', '')
        selected_class = request.form.get('class_name', '')
        selected_score_range = request.form.get('score_range', '')
        
        # POST请求后重定向到GET请求，保留筛选参数
        return redirect(url_for('teacher.filter_students', 
                               department=selected_department,
                               class_name=selected_class, 
                               score_range=selected_score_range))
    else:
        # 从URL参数获取筛选条件
        selected_department = request.args.get('department', '')
        selected_class = request.args.get('class_name', '')
        selected_score_range = request.args.get('score_range', '')
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 限制每页显示数量
    per_page = min(max(per_page, 10), 100)
    
    # 构建查询
    query = Student.query
    
    # 应用筛选条件
    if selected_department:
        query = query.filter(Student.department == selected_department)
        filter_form.department.data = selected_department
        
    if selected_class:
        query = query.filter(Student.class_name == selected_class)
        filter_form.class_name.data = selected_class
        
    # 处理综合成绩筛选
    if selected_score_range:
        if selected_score_range == 'none':
            # 筛选未评分的学生
            query = query.filter(Student.comprehensive_score == None)
        else:
            # 解析分数范围
            try:
                min_score, max_score = map(int, selected_score_range.split('-'))
                # 筛选分数在范围内的学生
                query = query.filter(Student.comprehensive_score >= min_score, 
                                    Student.comprehensive_score <= max_score)
            except Exception as e:
                current_app.logger.error(f"解析分数范围出错: {str(e)}")
    
    # 添加排序：按照综合评分降序排序
    query = query.order_by(Student.comprehensive_score.desc())
    
    # 执行分页查询
    students_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    students = students_pagination.items
    students_total = students_pagination.total
    pages = students_pagination.pages
    
    # 统计数据
    total_students = Student.query.count()
    submitted_count = Student.query.filter(Student.has_application == True).count()
    passed_exam_count = Student.query.filter(Student.passed_exam == True).count()
    
    # 计算班级推优通过率
    class_approved_count = Student.query.filter(Student.class_approved == True).count()
    class_approval_rate = round((class_approved_count / total_students * 100) if total_students > 0 else 0)
    
    return render_template('teacher/index.html', 
                          students=students,
                          students_total=students_total,
                          page=page,
                          per_page=per_page,
                          pages=pages,
                          search_form=search_form,
                          filter_form=filter_form,
                          form=import_form,
                          total_students=total_students,
                          submitted_count=submitted_count,
                          passed_exam_count=passed_exam_count,
                          class_approval_rate=class_approval_rate,
                          selected_department=selected_department,
                          selected_class=selected_class,
                          selected_score_range=selected_score_range)

@teacher_bp.route('/student/import', methods=['POST'])
def bulk_import():
    """批量导入学生数据"""
    form = ImportStudentsForm()
    
    if form.validate_on_submit():
        try:
            # 获取上传的文件
            file = form.file.data
            filename = secure_filename(file.filename)
            
            # 保存文件
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'imports', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)
            
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            # 记录学生模型的所有可用字段
            student_fields = [
                # 必填字段
                'student_id', 'name', 'gender', 
                # 个人基本信息
                'ethnicity', 'hometown', 'birth_date', 'id_card', 'phone', 'email', 'address',
                # 学籍信息
                'department', 'major', 'class_name', 'enrollment_date',
                # 政治信息
                'political_status', 'league_member_id', 'league_branch', 'league_join_date', 
                'has_application', 'application_date', 'passed_exam', 'class_approved',
                # 学业信息
                'has_failed_course', 'comprehensive_test_score', 'english_level', 
                'cet4_score', 'cet6_score', 'scholarship', 'volunteer_hours',
                # 成就经历信息
                'awards', 'social_practice'
            ]
            
            # 布尔字段列表
            boolean_fields = ['has_application', 'passed_exam', 'class_approved', 'has_failed_course']
            
            # 日期字段列表
            date_fields = ['birth_date', 'enrollment_date', 'league_join_date', 'application_date']
            
            # 导入学生数据
            success_count = 0
            error_count = 0
            error_details = []
            
            for index, row in df.iterrows():
                try:
                    # 检查必要字段
                    if 'student_id' not in row or pd.isna(row['student_id']) or 'name' not in row or pd.isna(row['name']):
                        error_count += 1
                        error_details.append(f"行 {index+2}: 缺少必填字段 (学号或姓名)")
                        continue
                    
                    # 检查学号是否已存在
                    existing_student = Student.query.filter_by(student_id=str(row['student_id'])).first()
                    if existing_student:
                        error_count += 1
                        error_details.append(f"行 {index+2}: 学号 {row['student_id']} 已存在")
                        continue
                    
                    # 创建用户
                    user = User(
                        username=str(row['student_id']),
                        role='student'
                    )
                    # 明确设置密码为学号后6位，不使用User类的默认初始化
                    user.set_password(str(row['student_id'])[-6:])
                    db.session.add(user)
                    db.session.flush()  # 获取用户ID但不提交事务
                    
                    # 创建学生记录并准备数据
                    student_data = {
                        'user_id': user.id,
                        'student_id': str(row['student_id']),
                        'name': str(row['name']),
                    }
                    
                    # 设置性别，确保默认值
                    if 'gender' in row and not pd.isna(row['gender']):
                        student_data['gender'] = str(row['gender'])
                    else:
                        student_data['gender'] = '男'  # 默认性别
                    
                    # 处理所有其他字段
                    for field in student_fields:
                        if field in ['student_id', 'name', 'gender', 'user_id']:
                            continue  # 已处理的字段跳过
                        
                        if field in row and not pd.isna(row[field]):
                            # 处理布尔值字段
                            if field in boolean_fields:
                                # 处理各种可能的布尔值表示
                                value = row[field]
                                if isinstance(value, bool):
                                    student_data[field] = value
                                elif isinstance(value, (int, float)):
                                    student_data[field] = bool(value)
                                else:
                                    value_str = str(value).lower()
                                    student_data[field] = value_str in ['true', 'yes', '1', 'y', '是', '真', 't']
                            
                            # 处理日期字段
                            elif field in date_fields:
                                # 尝试解析日期
                                try:
                                    if isinstance(row[field], (datetime.date, datetime.datetime)):
                                        student_data[field] = row[field]
                                    else:
                                        # 尝试解析字符串日期
                                        student_data[field] = pd.to_datetime(row[field]).date()
                                except:
                                    # 无法解析为日期，跳过
                                    current_app.logger.warning(f"无法解析日期值: {row[field]} 对于字段 {field}")
                            
                            # 处理普通字段
                            else:
                                student_data[field] = row[field]
                    
                    # 确保没有团员证号的默认值，如果Excel中不包含该字段则不设置
                    if 'league_member_id' in student_data:
                        # 如果是空字符串或者'admin666'，则删除该字段
                        if not student_data['league_member_id'] or student_data['league_member_id'] == 'admin666' or student_data['league_member_id'].strip() == '':
                            del student_data['league_member_id']
                            current_app.logger.info(f"学生 {row['student_id']} 的团员证号为空或admin666，已删除该字段")
                    
                    # 创建学生对象
                    student = Student(**student_data)
                    db.session.add(student)
                    success_count += 1
                    
                except Exception as e:
                    current_app.logger.error(f"导入学生时出错 (行 {index+2}): {str(e)}")
                    error_count += 1
                    error_details.append(f"行 {index+2}: {str(e)}")
            
            db.session.commit()
            
            # 删除临时文件
            os.remove(file_path)
            
            if error_count > 0:
                flash(f'成功导入{success_count}名学生，{error_count}名学生导入失败', 'warning')
                # 记录错误详情
                for error in error_details[:10]:  # 只显示前10个错误
                    current_app.logger.warning(error)
                if len(error_details) > 10:
                    current_app.logger.warning(f"... 以及 {len(error_details) - 10} 个其他错误")
            else:
                flash(f'成功导入{success_count}名学生', 'success')
                
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"批量导入学生失败: {str(e)}")
            flash(f'导入失败: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{error}', 'danger')
    
    return redirect(url_for('teacher.index'))

@teacher_bp.route('/dashboard')
@login_required
@teacher_required
def dashboard():
    """仪表盘页面（重定向到reports页面）"""
    return redirect(url_for('teacher.reports'))

@teacher_bp.route('/calculate_score/<string:student_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def calculate_score(student_id):
    """计算学生的综合评分"""
    # 查找学生
    student = Student.query.filter_by(student_id=student_id).first_or_404()
    
    # 查找当前活跃的评分配置
    current_config = ScoreConfig.get_active_config()
    
    # 获取所有评分配置
    configs = ScoreConfig.query.filter_by(active=True).all()
    
    # 获取评分历史
    score_history = StudentScore.query.filter_by(student_id=student_id).order_by(StudentScore.created_at.desc()).all()
    
    # 执行评分计算，使用静态方法而非实例化
    score_result = ScoreService.calculate_total_score(student, current_config)
    
    # 处理表单提交 - 保存评分结果
    if request.method == 'POST':
        config_id = request.form.get('config_id', current_config.id)
        remark = request.form.get('remark', '')
        
        # 查找选定的评分配置
        selected_config = ScoreConfig.query.get_or_404(config_id)
        
        # 重新计算使用选定配置的评分，使用静态方法
        score_result = ScoreService.calculate_total_score(student, selected_config)
        
        # 创建学生评分记录
        student_score = StudentScore(
            student_id=student.student_id,
            score_config_id=config_id,
            base_score=score_result['base_score'],
            academic_score=score_result['academic_score'],
            scholarship_score=score_result['scholarship_score'],
            volunteer_score=score_result['volunteer_score'],
            english_score=score_result['english_score'],
            total_score=score_result['total_score'],
            passed_base_conditions=score_result['passed_base_conditions'],
            remark=remark,
            created_by=current_user.id,
            score_detail=score_result
        )
        
        # 更新学生的综合评分 - 不进行四舍五入，保留原始值
        student.comprehensive_score = score_result['total_score']
        
        # 保存评分记录
        db.session.add(student_score)
        
        try:
            db.session.commit()
            flash('评分结果已成功保存', 'success')
            return redirect(url_for('teacher.calculate_score', student_id=student_id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"保存评分结果失败: {str(e)}")
            flash(f'保存评分结果失败: {str(e)}', 'danger')
    
    return render_template('teacher/calculate_score.html',
                         student=student,
                         score_result=score_result,
                         current_config=current_config,
                         configs=configs,
                         score_history=score_history)

@teacher_bp.route('/delete_score_record/<int:record_id>/<string:student_id>')
@login_required
@teacher_required
def delete_score_record(record_id, student_id):
    """删除评分记录"""
    try:
        # 查找评分记录
        score_record = StudentScore.query.get_or_404(record_id)
        
        # 验证学生ID是否匹配（安全检查）
        if score_record.student_id != student_id:
            flash('评分记录与学生不匹配，无法删除', 'danger')
            return redirect(url_for('teacher.calculate_score', student_id=student_id))
        
        # 保存创建时间用于日志
        record_time = score_record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        
        # 检查是否是最新的评分记录
        is_latest = not StudentScore.query.filter(
            StudentScore.student_id == student_id,
            StudentScore.created_at > score_record.created_at
        ).first()
        
        # 删除评分记录
        db.session.delete(score_record)
        
        # 如果是最新记录，则更新学生的综合评分
        student = Student.query.filter_by(student_id=student_id).first()
        if is_latest and student:
            # 查找该生的最新评分记录（删除当前记录后的最新记录）
            latest_score = StudentScore.query.filter_by(student_id=student_id).order_by(StudentScore.created_at.desc()).first()
            
            if latest_score:
                student.comprehensive_score = latest_score.total_score
                current_app.logger.info(f"删除后更新学生 {student_id} 的综合评分为 {student.comprehensive_score}，基于记录ID {latest_score.id}")
            else:
                student.comprehensive_score = None
                current_app.logger.info(f"删除后清空学生 {student_id} 的综合评分，因为没有评分记录")
        
        # 提交更改
        db.session.commit()
        
        flash(f'评分记录 ({record_time}) 删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除评分记录失败: {str(e)}")
        flash(f'删除评分记录失败: {str(e)}', 'danger')
    
    return redirect(url_for('teacher.calculate_score', student_id=student_id))

@teacher_bp.route('/batch_calculate', methods=['GET', 'POST'])
@login_required
@teacher_required
def batch_calculate():
    """批量计算学生评分"""
    # 创建一个简单的表单以支持CSRF保护
    form = FlaskForm()
    
    # 记录请求信息和参数
    current_app.logger.info(f"批量计算请求 - 方法: {request.method}, 路径: {request.path}, 请求参数: {request.args}")
    current_app.logger.info(f"请求参数详情: {dict(request.args)}")
    
    if request.method == 'POST':
        current_app.logger.info(f"POST表单数据键: {list(request.form.keys())}")
        current_app.logger.info(f"POST表单数据详情: {dict(request.form)}")
    
    # 获取所有学院和班级列表（用于筛选）
    departments_query = Student.query.with_entities(Student.department).distinct().all()
    departments = []
    
    for dept_result in departments_query:
        if hasattr(dept_result, 'department'):
            dept = dept_result.department
        elif isinstance(dept_result, tuple) and len(dept_result) > 0:
            dept = dept_result[0]
        else:
            continue
            
        if dept:
            departments.append(dept)
    
    class_names_query = Student.query.with_entities(Student.class_name).distinct().all()
    class_names = []
    
    for class_result in class_names_query:
        if hasattr(class_result, 'class_name'):
            class_name = class_result.class_name
        elif isinstance(class_result, tuple) and len(class_result) > 0:
            class_name = class_result[0]
        else:
            continue
            
        if class_name:
            class_names.append(class_name)
    
    # 获取评分配置
    configs = ScoreConfig.query.all()
    
    # 如果没有配置，则创建默认配置
    if not configs:
        default_config = ScoreConfig.create_default_config()
        configs = [default_config]
    
    # 获取当前使用的配置
    current_config = ScoreConfig.get_active_config()
    config_id = request.args.get('config_id', str(current_config.id))
    selected_config = ScoreConfig.query.get(config_id) or current_config
    current_app.logger.info(f"使用评分配置: {selected_config.name} (ID: {selected_config.id})")
    
    # 构建查询
    query = Student.query
    
    # 应用筛选条件
    department = request.args.get('department', '')
    if department:
        current_app.logger.info(f"筛选学院: {department}")
        query = query.filter(Student.department == department)
        
    class_name = request.args.get('class_name', '')
    if class_name:
        current_app.logger.info(f"筛选班级: {class_name}")
        query = query.filter(Student.class_name == class_name)
        
    political_status = request.args.get('political_status', '')
    if political_status:
        current_app.logger.info(f"筛选政治面貌: {political_status}")
        query = query.filter(Student.political_status == political_status)
    
    has_application = request.args.get('has_application', '')
    if has_application:
        current_app.logger.info(f"筛选入党申请: {has_application}")
        query = query.filter(Student.has_application == (has_application == '1'))
    
    # 获取筛选后的学生列表
    students = query.all()
    current_app.logger.info(f"筛选到 {len(students)} 名学生")
    
    # 调试日志：输出第一个学生的详细信息
    if students and len(students) > 0:
        first_student = students[0]
        current_app.logger.info(f"第一个学生详情 - ID: {first_student.student_id}, 姓名: {first_student.name}")
        current_app.logger.info(f"数据类型检查 - has_application: {type(first_student.has_application)}, 值: {first_student.has_application}")
        current_app.logger.info(f"数据类型检查 - passed_exam: {type(first_student.passed_exam)}, 值: {first_student.passed_exam}")
        current_app.logger.info(f"数据类型检查 - class_approved: {type(first_student.class_approved)}, 值: {first_student.class_approved}")
        current_app.logger.info(f"数据类型检查 - has_failed_course: {type(first_student.has_failed_course)}, 值: {first_student.has_failed_course}")
        current_app.logger.info(f"数据类型检查 - comprehensive_test_score: {type(first_student.comprehensive_test_score)}, 值: {first_student.comprehensive_test_score}")
        current_app.logger.info(f"数据类型检查 - volunteer_hours: {type(first_student.volunteer_hours)}, 值: {first_student.volunteer_hours}")
    
    # 如果通过GET方法提供了student_ids参数，则只计算指定的学生
    specified_student_ids = request.args.getlist('student_ids')
    if specified_student_ids:
        current_app.logger.info(f"GET请求提供的学生ID: {specified_student_ids}")
        student_dict = {s.student_id: s for s in students}
        students = [student_dict[sid] for sid in specified_student_ids if sid in student_dict]
        current_app.logger.info(f"筛选后剩余 {len(students)} 名学生")
    
    # 评分结果初始化
    score_results = {}
    
    # 处理批量评分保存
    if request.method == 'POST':
        current_app.logger.info(f"表单验证状态: {'成功' if form.validate_on_submit() else '失败'}")
        
        if form.validate_on_submit():
            student_ids = request.form.getlist('student_ids')
            current_app.logger.info(f"POST请求: 收到 {len(student_ids)} 个学生ID")
            
            # 获取备注，同时兼容remark和batch_remark两个字段名
            batch_remark = request.form.get('batch_remark', '') or request.form.get('remark', '')
            current_app.logger.info(f"收到评分备注: {batch_remark}")
            
            # 指定配置ID
            config_id = request.form.get('config_id', str(selected_config.id))
            selected_config = ScoreConfig.query.get(config_id) or current_config
            current_app.logger.info(f"使用评分配置: {selected_config.name} (ID: {selected_config.id})")
            
            if not student_ids:
                flash('请至少选择一名学生', 'warning')
                return redirect(url_for('teacher.batch_calculate'))
            
            # 批量计算并保存评分
            batch_results = ScoreService.batch_calculate_scores(
                student_ids=student_ids, 
                config=selected_config, 
                user_id=current_user.id,
                update_student=True,
                remark=batch_remark
            )
            
            # 确保总分不超过100分上限
            for result in batch_results:
                if result.get('score', 0) > 100:
                    result['score'] = 100
                if result.get('details', {}).get('total_score', 0) > 100:
                    result['details']['total_score'] = 100
            
            # 处理保存评分结果（添加评分记录到数据库）
            saved_count = 0
            error_count = 0
            
            try:
                for student_id in student_ids:
                    student_obj = Student.query.filter_by(student_id=student_id).first()
                    if not student_obj:
                        current_app.logger.warning(f"在保存评分结果时找不到学生ID: {student_id}")
                        error_count += 1
                        continue
                    
                    # 查找当前学生的评分结果
                    student_result = None
                    for result in batch_results:
                        if result.get('student_id') == student_id:
                            student_result = result
                            break
                    
                    if not student_result or not student_result.get('details'):
                        current_app.logger.warning(f"找不到学生ID: {student_id} 的评分结果")
                        error_count += 1
                        continue
                    
                    # 创建学生评分记录
                    student_score = StudentScore(
                        student_id=student_id,
                        score_config_id=config_id,
                        base_score=student_result['details'].get('base_score', 0),
                        academic_score=student_result['details'].get('academic_score', 0),
                        scholarship_score=student_result['details'].get('scholarship_score', 0),
                        volunteer_score=student_result['details'].get('volunteer_score', 0),
                        english_score=student_result['details'].get('english_score', 0),
                        total_score=student_result['details'].get('total_score', 0),
                        passed_base_conditions=student_result['details'].get('passed_base_conditions', False),
                        remark=batch_remark,
                        created_by=current_user.id,
                        score_detail=student_result['details']
                    )
                    
                    db.session.add(student_score)
                    
                    # 更新学生的综合评分 - 直接使用原始值，不进行四舍五入
                    student_obj.comprehensive_score = student_result['details'].get('total_score', 0)
                    saved_count += 1
                
                db.session.commit()
                flash(f'成功保存 {saved_count} 名学生的评分结果', 'success')
                if error_count > 0:
                    flash(f'有 {error_count} 名学生的评分结果保存失败', 'warning')
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"保存评分结果出错: {str(e)}")
                flash(f'保存评分结果失败: {str(e)}', 'danger')
        else:
            # 记录表单验证失败的原因
            current_app.logger.error(f"表单验证失败: {form.errors}")
            flash('表单验证失败，请刷新页面后重试', 'danger')
    
    # 如果是计算请求（GET带参数），计算评分但不保存
    calculate_param = request.args.get('calculate')
    current_app.logger.info(f"Calculate参数: {calculate_param}")
    
    if calculate_param == '1':
        current_app.logger.info(f"GET请求，带calculate=1参数: 计算 {len(students)} 名学生的评分")
        
        # 没有学生时提示
        if not students:
            flash('没有找到符合条件的学生，请调整筛选条件后重试', 'warning')
            return render_template(
                'teacher/batch_calculate.html',
                form=form,
                students=[],
                score_results={},
                configs=configs,
                current_config=selected_config,
                departments=departments,
                class_names=class_names
            )
        
        # 准备学生ID列表
        student_ids = [s.student_id for s in students]
        current_app.logger.info(f"计算评分的学生ID列表: {student_ids}")
        
        try:
            # 批量计算评分
            batch_results = ScoreService.batch_calculate_scores(
                student_ids=student_ids, 
                config=selected_config, 
                user_id=None,
                update_student=False
            )
            
            # 确保总分不超过100分上限
            for result in batch_results:
                if result.get('score', 0) > 100:
                    result['score'] = 100
                if result.get('details', {}).get('total_score', 0) > 100:
                    result['details']['total_score'] = 100
            
            # 更新评分结果
            score_results = batch_results
            current_app.logger.info(f"成功计算 {len(batch_results)} 名学生的评分")
            
            # 记录第一个结果用于调试
            if batch_results and len(batch_results) > 0:
                first_result = batch_results[0]
                current_app.logger.info(f"第一个学生评分结果 - ID: {first_result.get('student_id')}, 结果: {first_result}")
                
        except Exception as e:
            current_app.logger.error(f"批量计算评分时出错: {str(e)}")
            flash(f'批量计算评分失败: {str(e)}', 'danger')
    
    save = request.args.get('save') == '1'
    current_app.logger.info(f"Save参数: {save}")
    
    return render_template(
        'teacher/batch_calculate.html',
        form=form,
        students=students,
        score_results=score_results,
        configs=configs,
        current_config=selected_config,
        departments=departments,
        class_names=class_names
    )

@teacher_bp.route('/score_configs', methods=['GET'])
@login_required
@teacher_required
def score_configs():
    """评分配置管理页面"""
    # 添加一个空表单以提供CSRF令牌
    form = FlaskForm()
    
    configs = ScoreConfig.query.order_by(ScoreConfig.is_active.desc(), ScoreConfig.created_at.desc()).all()
    
    # 检查是否有编辑请求
    edit_config_id = request.args.get('edit')
    edit_config = None
    
    if edit_config_id:
        try:
            edit_config = ScoreConfig.query.get(edit_config_id)
            if edit_config:
                current_app.logger.info(f"正在编辑配置: {edit_config.name}")
                # 预处理配置数据以便在模板中使用
                for config in configs:
                    if str(config.id) == edit_config_id:
                        # 确保配置数据完整，设置为可编辑状态
                        edit_config = config
                        break
        except Exception as e:
            current_app.logger.error(f"获取编辑配置时出错: {str(e)}")
    
    # 准备配置数据供JSON序列化
    configs_for_json = []
    
    # 确保每个配置对象都有必要的属性，避免JSON序列化错误
    for config in configs:
        config_data = config.config
        
        # 添加缺失的所有设置字段的默认值
        if not config_data.get('base_score'):
            config_data['base_score'] = 60
            
        if not config_data.get('academic_weight'):
            config_data['academic_weight'] = 0.2
            
        if 'scholarship_settings' not in config_data:
            config_data['scholarship_settings'] = {
                'national_first': 10,
                'national_second': 8,
                'national_third': 6,
                'school_first': 5,
                'school_second': 3,
                'school_third': 2
            }
            
        if 'volunteer_settings' not in config_data:
            config_data['volunteer_settings'] = {
                'base_score': 5,
                'per_hour': 0.5,
                'min_hours': 10,
                'max_hours': 30
            }
            
        if 'english_settings' not in config_data:
            config_data['english_settings'] = {
                'cet4_pass_score': 425,
                'cet4_pass_points': 5,
                'cet4_excellent_score': 550,
                'cet4_excellent_points': 8,
                'cet6_pass_score': 425,
                'cet6_pass_points': 8,
                'cet6_excellent_score': 550,
                'cet6_excellent_points': 10
            }
        
        # 添加到JSON数据列表
        configs_for_json.append({
            'id': config.id,
            'name': config.name,
            'is_active': config.is_active,
            'created_at': config.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': config.updated_at.strftime('%Y-%m-%d %H:%M:%S') if config.updated_at else None,
            'created_by': config.created_by,
            'config': config_data
        })
    
    # 将配置列表转换为JSON字符串
    import json
    configs_json = json.dumps(configs_for_json, ensure_ascii=False)
    
    current_app.logger.info(f"传递了{len(configs_for_json)}个配置到模板")
    
    return render_template('teacher/score_config.html', 
                          configs=configs, 
                          form=form, 
                          edit_config=edit_config,
                          configs_json=configs_json)

@teacher_bp.route('/add_score_config', methods=['POST'])
@login_required
@teacher_required
def add_score_config():
    """添加评分配置"""
    # 获取基本配置
    name = request.form.get('name', '默认评分配置')
    base_score = int(request.form.get('base_score', 60))
    academic_weight = float(request.form.get('academic_weight', 0.15))
    is_active = 'is_active' in request.form
    
    # 构建配置字典
    config = {
        'base_score': base_score,
        'academic_weight': academic_weight,
        'scholarship_settings': {
            'national_first': int(request.form.get('scholarship_settings.national_first', 8)),
            'national_second': int(request.form.get('scholarship_settings.national_second', 6)),
            'national_third': int(request.form.get('scholarship_settings.national_third', 4)),
            'school_first': int(request.form.get('scholarship_settings.school_first', 5)),
            'school_second': int(request.form.get('scholarship_settings.school_second', 3)),
            'school_third': int(request.form.get('scholarship_settings.school_third', 2))
        },
        'english_settings': {
            'cet4_pass_score': int(request.form.get('english_settings.cet4_pass_score', 425)),
            'cet6_pass_score': int(request.form.get('english_settings.cet6_pass_score', 425)),
            'cet4_level1_points': int(request.form.get('english_settings.cet4_level1_points', 1)),  # 425-450
            'cet4_level2_points': int(request.form.get('english_settings.cet4_level2_points', 2)),  # 451-500
            'cet4_level3_points': int(request.form.get('english_settings.cet4_level3_points', 3)),  # 501-550
            'cet4_level4_points': int(request.form.get('english_settings.cet4_level4_points', 4)),  # 551-600
            'cet4_level5_points': int(request.form.get('english_settings.cet4_level5_points', 5)),  # 600+
            'cet6_level1_points': int(request.form.get('english_settings.cet6_level1_points', 3)),  # 425-450
            'cet6_level2_points': int(request.form.get('english_settings.cet6_level2_points', 5)),  # 451-500
            'cet6_level3_points': int(request.form.get('english_settings.cet6_level3_points', 6)),  # 501-550
            'cet6_level4_points': int(request.form.get('english_settings.cet6_level4_points', 8)),  # 551-600
            'cet6_level5_points': int(request.form.get('english_settings.cet6_level5_points', 10))  # 600+
        },
        'volunteer_settings': {
            'level0_points': 0,  # 0小时
            'level1_points': 1,  # 1-5小时
            'level2_points': 2,  # 6-15小时
            'level3_points': 3,  # 16-30小时
            'level4_points': 4,  # 31-50小时
            'level5_points': 5   # 51+小时
        }
    }
    
    # 如果设置为活跃配置，需要将其他配置设为非活跃
    if is_active:
        ScoreConfig.query.update({'is_active': False})
    
    # 创建新配置
    new_config = ScoreConfig(
        name=name,
        config=config,
        is_active=is_active,
        created_by=current_user.id
    )
    
    # 保存到数据库
    db.session.add(new_config)
    try:
        db.session.commit()
        flash(f'成功创建评分配置：{name}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'创建评分配置失败：{str(e)}', 'danger')
    
    return redirect(url_for('teacher.score_configs'))

@teacher_bp.route('/update_score_config', methods=['POST'])
@login_required
@teacher_required
def update_score_config():
    """更新评分配置"""
    form = FlaskForm()
    if not form.validate_on_submit():
        flash('表单验证失败，请重试', 'danger')
        return redirect(url_for('teacher.score_configs'))
        
    config_id = request.form.get('config_id')
    if not config_id:
        flash('未指定配置ID', 'danger')
        return redirect(url_for('teacher.score_configs'))
    
    # 查找配置
    config = ScoreConfig.query.get_or_404(config_id)
    
    # 更新基本信息
    config.name = request.form.get('name', config.name)
    is_active = 'is_active' in request.form
    
    # 如果设置为活跃配置，需要将其他配置设为非活跃
    if is_active and not config.is_active:
        ScoreConfig.query.update({'is_active': False})
        config.is_active = True
    
    # 更新配置详情
    config_data = config.config
    
    # 基础信息
    config_data['base_score'] = int(request.form.get('base_score', config_data.get('base_score', 60)))
    config_data['academic_weight'] = float(request.form.get('academic_weight', config_data.get('academic_weight', 0.15)))
    
    # 更新奖学金设置
    if 'scholarship_settings' not in config_data:
        config_data['scholarship_settings'] = {}
    config_data['scholarship_settings'].update({
        'national_first': int(request.form.get('scholarship_settings.national_first', config_data['scholarship_settings'].get('national_first', 8))),
        'national_second': int(request.form.get('scholarship_settings.national_second', config_data['scholarship_settings'].get('national_second', 6))),
        'national_third': int(request.form.get('scholarship_settings.national_third', config_data['scholarship_settings'].get('national_third', 4))),
        'school_first': int(request.form.get('scholarship_settings.school_first', config_data['scholarship_settings'].get('school_first', 5))),
        'school_second': int(request.form.get('scholarship_settings.school_second', config_data['scholarship_settings'].get('school_second', 3))),
        'school_third': int(request.form.get('scholarship_settings.school_third', config_data['scholarship_settings'].get('school_third', 2)))
    })
    
    # 更新英语能力评估设置
    if 'english_settings' not in config_data:
        config_data['english_settings'] = {}
    config_data['english_settings'].update({
        'cet4_pass_score': int(request.form.get('english_settings.cet4_pass_score', config_data['english_settings'].get('cet4_pass_score', 425))),
        'cet6_pass_score': int(request.form.get('english_settings.cet6_pass_score', config_data['english_settings'].get('cet6_pass_score', 425))),
        'cet4_level1_points': int(request.form.get('english_settings.cet4_level1_points', config_data['english_settings'].get('cet4_level1_points', 1))),
        'cet4_level2_points': int(request.form.get('english_settings.cet4_level2_points', config_data['english_settings'].get('cet4_level2_points', 2))),
        'cet4_level3_points': int(request.form.get('english_settings.cet4_level3_points', config_data['english_settings'].get('cet4_level3_points', 3))),
        'cet4_level4_points': int(request.form.get('english_settings.cet4_level4_points', config_data['english_settings'].get('cet4_level4_points', 4))),
        'cet4_level5_points': int(request.form.get('english_settings.cet4_level5_points', config_data['english_settings'].get('cet4_level5_points', 5))),
        'cet6_level1_points': int(request.form.get('english_settings.cet6_level1_points', config_data['english_settings'].get('cet6_level1_points', 3))),
        'cet6_level2_points': int(request.form.get('english_settings.cet6_level2_points', config_data['english_settings'].get('cet6_level2_points', 5))),
        'cet6_level3_points': int(request.form.get('english_settings.cet6_level3_points', config_data['english_settings'].get('cet6_level3_points', 6))),
        'cet6_level4_points': int(request.form.get('english_settings.cet6_level4_points', config_data['english_settings'].get('cet6_level4_points', 8))),
        'cet6_level5_points': int(request.form.get('english_settings.cet6_level5_points', config_data['english_settings'].get('cet6_level5_points', 10)))
    })
    
    # 更新志愿服务设置
    if 'volunteer_settings' not in config_data:
        config_data['volunteer_settings'] = {}
    config_data['volunteer_settings'].update({
        'level0_points': 0,  # 0小时
        'level1_points': 1,  # 1-5小时
        'level2_points': 2,  # 6-15小时
        'level3_points': 3,  # 16-30小时
        'level4_points': 4,  # 31-50小时
        'level5_points': 5   # 51+小时
    })
    
    # 更新配置
    config.config = config_data
    
    # 保存到数据库
    try:
        db.session.commit()
        flash(f'成功更新评分配置：{config.name}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'更新评分配置失败：{str(e)}', 'danger')
    
    return redirect(url_for('teacher.score_configs'))

@teacher_bp.route('/delete_score_config', methods=['POST'])
@login_required
@teacher_required
def delete_score_config():
    """删除评分配置"""
    form = FlaskForm()
    if not form.validate_on_submit():
        flash('表单验证失败，请重试', 'danger')
        return redirect(url_for('teacher.score_configs'))
        
    config_id = request.form.get('config_id')
    if not config_id:
        flash('未指定配置ID', 'danger')
        return redirect(url_for('teacher.score_configs'))
    
    # 查找配置
    config = ScoreConfig.query.get_or_404(config_id)
    
    # 不允许删除活跃配置
    if config.is_active:
        flash('不能删除当前使用中的配置，请先将其他配置设为活跃', 'danger')
        return redirect(url_for('teacher.score_configs'))
    
    # 删除配置
    try:
        db.session.delete(config)
        db.session.commit()
        flash(f'成功删除评分配置：{config.name}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除评分配置失败：{str(e)}', 'danger')
    
    return redirect(url_for('teacher.score_configs'))

@teacher_bp.route('/set_active_config', methods=['POST'])
@login_required
@teacher_required
def set_active_config():
    """设置活跃配置"""
    form = FlaskForm()
    if not form.validate_on_submit():
        flash('表单验证失败，请重试', 'danger')
        return redirect(url_for('teacher.score_configs'))
        
    config_id = request.form.get('config_id')
    if not config_id:
        flash('未指定配置ID', 'danger')
        return redirect(url_for('teacher.score_configs'))
    
    # 将所有配置设为非活跃
    ScoreConfig.query.update({'is_active': False})
    
    # 设置指定配置为活跃
    config = ScoreConfig.query.get_or_404(config_id)
    config.is_active = True
    
    # 保存到数据库
    try:
        db.session.commit()
        flash(f'已将 {config.name} 设为当前使用的配置', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'设置活跃配置失败：{str(e)}', 'danger')
    
    return redirect(url_for('teacher.score_configs'))

@teacher_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
@teacher_required
def change_password():
    """教师修改密码"""
    # 创建一个简单的表单用于CSRF保护
    form = FlaskForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # 验证表单数据
        if not old_password or not new_password or not confirm_password:
            flash('所有字段都为必填项', 'danger')
            return render_template('teacher/change_password.html', form=form)
            
        if new_password != confirm_password:
            flash('新密码与确认密码不匹配', 'danger')
            return render_template('teacher/change_password.html', form=form)
            
        if len(new_password) < 6:
            flash('新密码长度必须至少为6个字符', 'danger')
            return render_template('teacher/change_password.html', form=form)
            
        # 验证旧密码
        user = User.query.get(current_user.id)
        if not user.check_password(old_password):
            flash('旧密码不正确', 'danger')
            return render_template('teacher/change_password.html', form=form)
            
        # 更新密码
        user.set_password(new_password)
        
        # 保存到数据库
        try:
            db.session.commit()
            flash('密码修改成功', 'success')
            return redirect(url_for('teacher.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'密码修改失败：{str(e)}', 'danger')
    
    return render_template('teacher/change_password.html', form=form)

@teacher_bp.route('/profile')
@login_required
@teacher_required
def profile():
    """教师个人资料页面"""
    return render_template('teacher/profile.html', teacher=current_user)

@teacher_bp.route('/reports')
@login_required
@teacher_required
def reports():
    """教师数据可视化分析页面"""
    # 1. 获取基本统计数据
    total_students = Student.query.count()
    submitted_count = Student.query.filter(Student.has_application == True).count()
    passed_exam_count = Student.query.filter(Student.passed_exam == True).count()
    class_approved_count = Student.query.filter(Student.class_approved == True).count()
    
    # 2. 获取评分统计
    # 确保获取正确的已评分学生数量（应该使用去重后的学生ID）
    scored_students = db.session.query(func.count(func.distinct(StudentScore.student_id))).scalar() or 0
    
    # 记录实际数量
    current_app.logger.info(f"统计数据 - 总学生数: {total_students}, 已评分学生数: {scored_students}")
    
    # 计算平均分
    average_score = db.session.query(func.avg(StudentScore.total_score)).scalar()
    average_score = round(average_score, 1) if average_score else 0
    current_app.logger.info(f"平均分: {average_score}")
    
    # 3. 获取所有院系和班级列表（用于筛选下拉菜单）
    departments_query = db.session.query(Student.department).distinct().filter(Student.department != None, Student.department != '').order_by(Student.department).all()
    departments = []
    
    for result in departments_query:
        if hasattr(result, 'department'):
            departments.append(result.department)
        elif isinstance(result, tuple) and len(result) > 0:
            departments.append(result[0])
        else:
            current_app.logger.warning(f"意外的院系查询结果格式: {result}")
    
    class_names_query = db.session.query(Student.class_name).distinct().filter(Student.class_name != None, Student.class_name != '').order_by(Student.class_name).all()
    class_names = []
    
    for result in class_names_query:
        if hasattr(result, 'class_name'):
            class_names.append(result.class_name)
        elif isinstance(result, tuple) and len(result) > 0:
            class_names.append(result[0])
        else:
            current_app.logger.warning(f"意外的班级查询结果格式: {result}")
    
    # 4. 计算评分分布数据
    score_ranges = ['0-59', '60-64', '65-69', '70-74', '75-79', '80-84', '85-89', '90-94', '95-100']
    score_distribution = [0] * len(score_ranges)
    
    score_stats = db.session.query(
        case(
            (StudentScore.total_score < 60, 0),
            ((StudentScore.total_score >= 60) & (StudentScore.total_score < 65), 1),
            ((StudentScore.total_score >= 65) & (StudentScore.total_score < 70), 2),
            ((StudentScore.total_score >= 70) & (StudentScore.total_score < 75), 3),
            ((StudentScore.total_score >= 75) & (StudentScore.total_score < 80), 4),
            ((StudentScore.total_score >= 80) & (StudentScore.total_score < 85), 5),
            ((StudentScore.total_score >= 85) & (StudentScore.total_score < 90), 6),
            ((StudentScore.total_score >= 90) & (StudentScore.total_score < 95), 7),
            ((StudentScore.total_score >= 95), 8)
        ).label('score_range'),
        func.count().label('count')
    ).group_by('score_range').all()
    
    for stat in score_stats:
        # 安全地解包 - 确保查询结果包含两个值
        if hasattr(stat, 'score_range') and hasattr(stat, 'count'):
            range_index = stat.score_range
            count = stat.count
        elif isinstance(stat, tuple) and len(stat) >= 2:
            range_index, count = stat
        else:
            current_app.logger.warning(f"意外的分数统计格式: {stat}")
            continue
            
        if range_index is not None and 0 <= range_index < len(score_distribution):
            score_distribution[range_index] = count
    
    # 5. 计算评分等级分布
    grade_distribution = [0] * 5  # 5个等级
    
    grade_stats = db.session.query(
        case(
            (StudentScore.total_score < 60, 0),
            ((StudentScore.total_score >= 60) & (StudentScore.total_score < 70), 1),
            ((StudentScore.total_score >= 70) & (StudentScore.total_score < 80), 2),
            ((StudentScore.total_score >= 80) & (StudentScore.total_score < 90), 3),
            ((StudentScore.total_score >= 90), 4)
        ).label('grade'),
        func.count().label('count')
    ).group_by('grade').all()
    
    for stat in grade_stats:
        # 安全地解包 - 确保查询结果包含两个值
        if hasattr(stat, 'grade') and hasattr(stat, 'count'):
            grade_index = stat.grade
            count = stat.count
        elif isinstance(stat, tuple) and len(stat) >= 2:
            grade_index, count = stat
        else:
            current_app.logger.warning(f"意外的等级统计格式: {stat}")
            continue
            
        if grade_index is not None and 0 <= grade_index < len(grade_distribution):
            grade_distribution[grade_index] = count
    
    # 计算优秀比例（80分以上）
    excellent_students = grade_distribution[3] + grade_distribution[4]  # 优秀 + 特别优秀
    excellent_rate = (excellent_students / scored_students * 100) if scored_students > 0 else 0
    # 确保百分比不超过100%
    excellent_rate = min(excellent_rate, 100)
    # 四舍五入到一位小数
    excellent_rate = round(excellent_rate, 1)
    
    current_app.logger.info(f"优秀比例计算 - 优秀人数: {excellent_students}, 已评分学生: {scored_students}, 比例: {excellent_rate}%")
    
    # 6. 获取各班级评分平均分
    class_scores = db.session.query(
        Student.class_name,
        func.avg(StudentScore.total_score).label('avg_score'),
        func.count(func.distinct(StudentScore.student_id)).label('student_count')
    ).join(StudentScore, Student.student_id == StudentScore.student_id)\
     .filter(Student.class_name != None, Student.class_name != '')\
     .group_by(Student.class_name)\
     .order_by(func.avg(StudentScore.total_score).desc())\
     .all()
    
    class_names_for_chart = []
    class_avg_scores = []
    
    for result in class_scores:
        # 安全地解包查询结果
        if hasattr(result, 'class_name') and hasattr(result, 'avg_score'):
            class_name = result.class_name
            avg_score = result.avg_score
        elif isinstance(result, tuple) and len(result) >= 2:
            class_name = result[0]
            avg_score = result[1]
        else:
            current_app.logger.warning(f"意外的班级分数统计格式: {result}")
            continue
            
        class_names_for_chart.append(class_name)
        class_avg_scores.append(round(avg_score, 1) if avg_score is not None else 0)
    
    # 7. 计算评分组成分析（各项得分）
    score_components_avg = db.session.query(
        func.avg(StudentScore.base_score).label('base_score'),
        func.avg(StudentScore.academic_score).label('academic_score'),
        func.avg(StudentScore.volunteer_score).label('volunteer_score'),
        func.avg(StudentScore.scholarship_score).label('scholarship_score'),
        func.avg(StudentScore.english_score).label('english_score')
    ).first()
    
    # 将组件平均分格式化为列表
    score_components = []
    
    # 安全地获取各组件分数
    if score_components_avg:
        if hasattr(score_components_avg, 'base_score'):
            base_score = score_components_avg.base_score
            academic_score = score_components_avg.academic_score
            volunteer_score = score_components_avg.volunteer_score
            scholarship_score = score_components_avg.scholarship_score
            english_score = score_components_avg.english_score
        else:
            # 尝试通过索引访问
            base_score = score_components_avg[0] if len(score_components_avg) > 0 else 0
            academic_score = score_components_avg[1] if len(score_components_avg) > 1 else 0
            volunteer_score = score_components_avg[2] if len(score_components_avg) > 2 else 0
            scholarship_score = score_components_avg[3] if len(score_components_avg) > 3 else 0
            english_score = score_components_avg[4] if len(score_components_avg) > 4 else 0
        
        # 添加各组件并处理空值
        score_components = [
            round(base_score or 0, 1),
            round(academic_score or 0, 1),
            round(volunteer_score or 0, 1),
            round(scholarship_score or 0, 1),
            round(english_score or 0, 1)
        ]
    else:
        # 如果没有结果，使用默认值
        score_components = [0, 0, 0, 0, 0]
    
    # 8. 获取各学院评分均分
    department_scores = db.session.query(
        Student.department,
        func.avg(StudentScore.total_score).label('avg_score'),
        func.count(func.distinct(StudentScore.student_id)).label('student_count')
    ).join(StudentScore, Student.student_id == StudentScore.student_id)\
     .filter(Student.department != None, Student.department != '')\
     .group_by(Student.department)\
     .order_by(func.avg(StudentScore.total_score).desc())\
     .all()
    
    departments_for_chart = []
    department_avg_scores = []
    
    for result in department_scores:
        # 安全地解包查询结果
        if hasattr(result, 'department') and hasattr(result, 'avg_score'):
            dept = result.department
            avg_score = result.avg_score
        elif isinstance(result, tuple) and len(result) >= 2:
            dept = result[0]
            avg_score = result[1]
        else:
            current_app.logger.warning(f"意外的学院分数统计格式: {result}")
            continue
            
        departments_for_chart.append(dept)
        department_avg_scores.append(round(avg_score, 1) if avg_score is not None else 0)
    
    # 9. 详细的学院统计数据
    department_stats = {}
    
    # 首先按学院统计总人数
    all_departments = db.session.query(
        Student.department,
        func.count(Student.id).label('total')
    ).filter(Student.department != None, Student.department != '')\
     .group_by(Student.department)\
     .all()
    
    for result in all_departments:
        # 安全地解包查询结果
        if hasattr(result, 'department') and hasattr(result, 'total'):
            dept = result.department
            total = result.total
        elif isinstance(result, tuple) and len(result) >= 2:
            dept, total = result
        else:
            current_app.logger.warning(f"意外的部门统计格式: {result}")
            continue
            
        department_stats[dept] = {'name': dept, 'total': total}
    
    # 计算已评分人数和平均分
    scored_departments = db.session.query(
        Student.department,
        func.count(func.distinct(StudentScore.student_id)).label('scored'),
        func.avg(StudentScore.total_score).label('avg_score')
    ).join(StudentScore, Student.student_id == StudentScore.student_id)\
     .filter(Student.department != None, Student.department != '')\
     .group_by(Student.department)\
     .all()
    
    for result in scored_departments:
        # 安全地解包查询结果
        if hasattr(result, 'department') and hasattr(result, 'scored') and hasattr(result, 'avg_score'):
            dept = result.department
            scored = result.scored
            avg_score = result.avg_score
        elif isinstance(result, tuple) and len(result) >= 3:
            dept, scored, avg_score = result
        else:
            current_app.logger.warning(f"意外的部门分数统计格式: {result}")
            continue
            
        if dept in department_stats:
            department_stats[dept]['scored'] = scored
            department_stats[dept]['avg_score'] = round(avg_score, 1) if avg_score else 0
    
    # 计算各学院各等级人数
    grade_departments = db.session.query(
        Student.department,
        case(
            (StudentScore.total_score < 60, 'fail'),
            ((StudentScore.total_score >= 60) & (StudentScore.total_score < 70), 'pass'),
            ((StudentScore.total_score >= 70) & (StudentScore.total_score < 80), 'good'),
            ((StudentScore.total_score >= 80) & (StudentScore.total_score < 90), 'excellent'),
            ((StudentScore.total_score >= 90), 'outstanding')
        ).label('grade'),
        func.count().label('count')
    ).join(StudentScore, Student.student_id == StudentScore.student_id)\
     .filter(Student.department != None, Student.department != '')\
     .group_by(Student.department, 'grade')\
     .all()
    
    for result in grade_departments:
        # 安全地解包查询结果
        if hasattr(result, 'department') and hasattr(result, 'grade') and hasattr(result, 'count'):
            dept = result.department
            grade = result.grade
            count = result.count
        elif isinstance(result, tuple) and len(result) >= 3:
            dept, grade, count = result
        else:
            current_app.logger.warning(f"意外的部门等级统计格式: {result}")
            continue
            
        if dept in department_stats and grade:
            department_stats[dept][grade] = count
    
    # 计算评分率和各等级比率
    for dept_data in department_stats.values():
        # 添加默认值
        if 'scored' not in dept_data:
            dept_data['scored'] = 0
        if 'avg_score' not in dept_data:
            dept_data['avg_score'] = 0
        
        # 添加各等级默认值
        for grade in ['fail', 'pass', 'good', 'excellent', 'outstanding']:
            if grade not in dept_data:
                dept_data[grade] = 0
            
        total = dept_data['total']
        scored = dept_data['scored']
        
        dept_data['scored_rate'] = scored / total if total > 0 else 0
        
        # 计算等级比率
        total_scored = dept_data['fail'] + dept_data['pass'] + dept_data['good'] + dept_data['excellent'] + dept_data['outstanding']
        
        dept_data['pass_rate'] = (dept_data['pass'] / total_scored) if total_scored > 0 else 0
        dept_data['good_rate'] = (dept_data['good'] / total_scored) if total_scored > 0 else 0
        dept_data['excellent_rate'] = ((dept_data['excellent'] + dept_data['outstanding']) / total_scored) if total_scored > 0 else 0
    
    # 转换为列表并按总人数排序
    departments_data = list(department_stats.values())
    departments_data.sort(key=lambda x: x['total'], reverse=True)
    
    return render_template('teacher/reports.html',
                         total_students=total_students,
                         submitted_count=submitted_count,
                         passed_exam_count=passed_exam_count,
                         class_approved_count=class_approved_count,
                         scored_students=scored_students,
                         average_score=average_score,
                         excellent_rate=excellent_rate,
                         departments=departments,
                         class_names=class_names,
                         score_ranges=score_ranges,
                         score_distribution=score_distribution,
                         grade_distribution=grade_distribution,
                         class_names_for_chart=class_names_for_chart,
                         class_avg_scores=class_avg_scores,
                         score_components=score_components,
                         departments_for_chart=departments_for_chart, 
                         department_avg_scores=department_avg_scores,
                         departments_data=departments_data)

@teacher_bp.route('/get_student_details', methods=['GET'])
@login_required
@teacher_required
def get_student_details():
    """获取学生详细信息的API"""
    try:
        student_id = request.args.get('student_id')
        if not student_id:
            current_app.logger.error("未提供student_id参数")
            return jsonify({'success': False, 'error': '缺少学生ID参数'}), 400
        
        current_app.logger.info(f"获取学生详细信息: {student_id}")
        
        # 查询学生基本信息
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            current_app.logger.error(f"未找到学生: {student_id}")
            return jsonify({'success': False, 'error': f'未找到ID为 {student_id} 的学生'}), 404
        
        # 获取最新的评分记录
        latest_score = StudentScore.query.filter_by(student_id=student.id).order_by(StudentScore.created_at.desc()).first()
        
        # 构建响应数据
        response = {
            'success': True,
            'student': {
                'id': student.id,
                'student_id': student.student_id,
                'name': student.name,
                'gender': student.gender,
                'department': student.department,
                'class_name': student.class_name,
                'political_status': student.political_status,
                'has_application': bool(student.has_application),
                'passed_exam': bool(student.passed_exam),
                'class_approved': bool(student.class_approved),
                'has_failed_course': bool(student.has_failed_course),
                'comprehensive_test_score': student.comprehensive_test_score,
                'volunteer_hours': student.volunteer_hours,
                'scholarship': student.scholarship,
                'position': getattr(student, 'position', None)
            },
            'has_score': latest_score is not None
        }
        
        # 如果有评分记录，添加到响应中
        if latest_score:
            response['score'] = {
                'id': latest_score.id,
                'total_score': latest_score.total_score,
                'base_condition_satisfied': latest_score.base_condition_satisfied,
                'academic_score': latest_score.academic_score,
                'volunteer_score': latest_score.volunteer_score,
                'political_score': latest_score.political_score,
                'english_score': latest_score.english_score,
                'scholarship_score': latest_score.scholarship_score,
                'position_score': latest_score.position_score,
                'evaluation_result': latest_score.evaluation_result,
                'created_at': latest_score.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'evaluated_by': latest_score.evaluated_by,
                'remark': latest_score.remark
            }
        
        # 检查数据完整性
        required_fields = [
            ('comprehensive_test_score', '综合测评成绩'), 
            ('volunteer_hours', '志愿服务时长'),
            ('has_application', '是否递交入党申请书'),
            ('passed_exam', '是否通过党课考试'),
            ('class_approved', '是否通过班级推优'),
            ('has_failed_course', '是否有挂科记录')
        ]
        
        missing_fields = []
        for field, desc in required_fields:
            # 注意：因为布尔值可能是False，所以我们只检查它是否为None
            attr_value = getattr(student, field, None)
            if attr_value is None:
                missing_fields.append({'field': field, 'description': desc})
        
        response['missing_fields'] = missing_fields
        response['data_complete'] = len(missing_fields) == 0
        
        current_app.logger.info(f"成功获取学生 {student_id} 的详细信息")
        return jsonify(response)
    
    except Exception as e:
        current_app.logger.error(f"获取学生详细信息时出错: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

@teacher_bp.route('/check_student_info', methods=['GET'])
@login_required
@teacher_required
def check_student_info():
    """检查学生信息完整性"""
    try:
        # 获取筛选参数
        department = request.args.get('department', '')
        class_name = request.args.get('class_name', '')
        political_status = request.args.get('political_status', '')
        
        # 构建基本查询
        query = Student.query
        
        # 应用筛选条件
        if department:
            query = query.filter(Student.department == department)
        
        if class_name:
            query = query.filter(Student.class_name == class_name)
            
        if political_status:
            query = query.filter(Student.political_status == political_status)
        
        # 获取学生列表
        students = query.all()
        
        # 检查每个学生的数据完整性
        incomplete_students = []
        required_fields = [
            ("comprehensive_test_score", "综合测评成绩"), 
            ("volunteer_hours", "志愿服务时长"),
            ("has_application", "是否递交入党申请书"),
            ("passed_exam", "是否通过党课考试"),
            ("class_approved", "是否通过班级推优"),
            ("has_failed_course", "是否有挂科记录")
        ]
        
        for student in students:
            missing_fields = []
            for field, desc in required_fields:
                if getattr(student, field, None) is None:
                    missing_fields.append((field, desc))
            
            if missing_fields:
                incomplete_students.append({
                    'student_id': student.student_id,
                    'name': student.name,
                    'class_name': student.class_name,
                    'missing_fields': missing_fields
                })
        
        current_app.logger.info(f"发现 {len(incomplete_students)} 名学生信息不完整")
        
        # 获取所有院系和班级列表（用于筛选）
        departments = []
        for student in Student.query.all():
            if student.department and student.department not in departments:
                departments.append(student.department)
        departments.sort()
        
        class_names = []
        for student in Student.query.all():
            if student.class_name and student.class_name not in class_names:
                class_names.append(student.class_name)
        class_names.sort()
        
        return render_template(
            'teacher/student_info_check.html',
            incomplete_students=incomplete_students,
            departments=departments,
            class_names=class_names
        )
    except Exception as e:
        current_app.logger.error(f"检查学生信息完整性出错: {str(e)}")
        flash(f"检查学生信息时出错: {str(e)}", 'danger')
        return redirect(url_for('teacher.batch_calculate'))

@teacher_bp.route('/get_latest_scores', methods=['POST'])
@login_required
@teacher_required
def get_latest_scores():
    """批量获取学生的最新评分"""
    try:
        data = request.json
        if not data or 'student_ids' not in data:
            return jsonify({'success': False, 'error': '缺少学生ID列表'}), 400
        
        student_ids = data['student_ids']
        if not student_ids or not isinstance(student_ids, list):
            return jsonify({'success': False, 'error': '学生ID列表格式错误'}), 400
        
        # 构建结果字典
        results = {}
        
        # 查询每个学生的最新评分
        for student_id in student_ids:
            student = Student.query.filter_by(student_id=student_id).first()
            if student:
                results[student_id] = student.comprehensive_score
            else:
                results[student_id] = None
        
        return jsonify({
            'success': True,
            'scores': results
        })
    except Exception as e:
        current_app.logger.error(f"获取最新评分出错: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@teacher_bp.route('/get_student_latest_score', methods=['GET'])
@login_required
@teacher_required
def get_student_latest_score():
    """获取单个学生的最新评分"""
    try:
        student_id = request.args.get('student_id')
        if not student_id:
            return jsonify({'success': False, 'error': '缺少学生ID参数'}), 400
        
        # 查询学生信息
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            return jsonify({'success': False, 'error': f'未找到ID为 {student_id} 的学生'}), 404
        
        # 获取学生的最新评分记录
        latest_score = StudentScore.query.filter_by(student_id=student_id).order_by(StudentScore.created_at.desc()).first()
        
        return jsonify({
            'success': True,
            'student_id': student_id,
            'score': student.comprehensive_score,
            'has_latest_record': latest_score is not None,
            'record_id': latest_score.id if latest_score else None,
            'record_time': latest_score.created_at.strftime('%Y-%m-%d %H:%M:%S') if latest_score else None
        })
    except Exception as e:
        current_app.logger.error(f"获取学生最新评分出错: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500 