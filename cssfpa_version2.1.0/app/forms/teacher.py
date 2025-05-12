from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SelectField, DateField, IntegerField, TextAreaField, BooleanField, EmailField, PasswordField
from wtforms.validators import DataRequired, Optional, Length, NumberRange, Regexp, Email

class StudentSearchForm(FlaskForm):
    """学生搜索表单"""
    search_type = SelectField('搜索类型', 
                            choices=[('student_id', '学号'), ('name', '姓名'), ('class_name', '班级')],
                            default='student_id')
    search_term = StringField('搜索内容')

class StudentFilterForm(FlaskForm):
    """学生筛选表单"""
    department = SelectField('学院', 
                         choices=[
                             ('', '全部'),
                             ('管理学院', '管理学院'),
                             ('计算机学院', '计算机学院'),
                             ('信息工程学院', '信息工程学院'),
                             ('经济学院', '经济学院'),
                             ('外国语学院', '外国语学院'),
                             ('艺术学院', '艺术学院')
                         ], default='管理学院')
    class_name = SelectField('班级', choices=[('', '全部')], default='')
    political_status = SelectField('政治面貌', 
                                choices=[
                                    ('', '全部'),
                                    ('群众', '群众'),
                                    ('共青团员', '共青团员'),
                                    ('入党积极分子', '入党积极分子'),
                                    ('预备党员', '预备党员'),
                                    ('中共党员', '中共党员')
                                ], default='')
    application_submitted = SelectField('递交申请书', 
                                choices=[
                                    ('', '全部'),
                                    ('1', '已递交'),
                                    ('0', '未递交')
                                ], default='')
    passed_exam = SelectField('通过党课考试', 
                            choices=[
                                ('', '全部'),
                                ('1', '已通过'),
                                ('0', '未通过')
                            ], default='')
    class_approved = SelectField('通过支部大会表决', 
                                choices=[
                                    ('', '全部'),
                                    ('1', '已通过'),
                                    ('0', '未通过')
                                ], default='')
    score_range = SelectField('综测成绩', 
                            choices=[
                                ('', '全部'),
                                ('90-100', '优秀(90-100分)'),
                                ('80-89', '良好(80-89分)'),
                                ('70-79', '中等(70-79分)'),
                                ('60-69', '及格(60-69分)'),
                                ('0-59', '不及格(60分以下)'),
                                ('none', '未评定')
                            ], default='')

class StudentForm(FlaskForm):
    """学生添加和编辑表单"""
    # 个人基本信息
    student_id = StringField('学号', validators=[
        DataRequired(message='学号不能为空'),
        Length(min=8, max=20, message='学号长度必须在8-20位之间'),
        Regexp(r'^\d+$', message='学号必须是数字')
    ])
    id_card = StringField('身份证号', validators=[
        Optional(),
        Length(min=18, max=18, message='身份证号必须是18位'),
        Regexp(r'^\d{17}[\dXx]$', message='请输入有效的身份证号')
    ])
    name = StringField('姓名', validators=[
        DataRequired(message='姓名不能为空'),
        Length(min=2, max=20, message='姓名长度必须在2-20位之间')
    ])
    gender = SelectField('性别', 
        choices=[('男', '男'), ('女', '女')],
        validators=[DataRequired(message='请选择性别')]
    )
    ethnicity = StringField('民族', validators=[DataRequired(), Length(max=20)])
    hometown = StringField('籍贯', validators=[Optional(), Length(max=100)])
    birth_date = DateField('出生日期', validators=[Optional()])
    phone = StringField('手机号码', validators=[
        Optional(),
        Length(min=11, max=11, message='手机号码必须是11位'),
        Regexp(r'^\d{11}$', message='请输入有效的手机号码')
    ])
    email = EmailField('电子邮箱', validators=[
        Optional(),
        Email(message='请输入有效的电子邮箱地址')
    ])
    address = StringField('家庭住址', validators=[
        Optional(),
        Length(max=200, message='地址长度不能超过200个字符')
    ])

    # 学籍信息
    department = StringField('学院', validators=[
        DataRequired(message='学院不能为空'),
        Length(max=100, message='学院名称不能超过100个字符')
    ])
    major = StringField('专业', validators=[
        DataRequired(message='专业不能为空'),
        Length(max=50, message='专业名称不能超过50个字符')
    ])
    class_name = StringField('班级', validators=[
        DataRequired(message='班级不能为空'),
        Length(max=50, message='班级名称不能超过50个字符')
    ])
    enrollment_date = DateField('入学日期', validators=[Optional()])
    
    # 政治信息
    political_status = SelectField('政治面貌', 
        choices=[
            ('群众', '群众'),
            ('共青团员', '共青团员'),
            ('入党积极分子', '入党积极分子'),
            ('预备党员', '预备党员'),
            ('中共党员', '中共党员')
        ],
        validators=[Optional()]
    )
    league_member_id = StringField('团员证号', validators=[Optional(), Length(max=20)], default=None)
    league_branch = StringField('所在团支部', validators=[Optional(), Length(max=100)])
    league_join_date = DateField('入团日期', validators=[Optional()])
    has_application = BooleanField('是否递交入党申请书')
    application_date = DateField('申请书递交日期', validators=[Optional()])
    passed_exam = BooleanField('是否通过党课考试')
    class_approved = BooleanField('是否通过支部大会表决')
    
    # 学业信息
    has_failed_course = BooleanField('是否有不及格课程')
    comprehensive_test_score = IntegerField('综合测评成绩', validators=[Optional(), NumberRange(min=0, max=100)])
    english_level = StringField('英语水平', validators=[Optional(), Length(max=20)])
    cet4_score = IntegerField('CET4成绩', validators=[Optional(), NumberRange(min=0, max=710)])
    cet6_score = IntegerField('CET6成绩', validators=[Optional(), NumberRange(min=0, max=710)])
    scholarship = TextAreaField('获得奖学金', validators=[Optional()])
    volunteer_hours = IntegerField('志愿服务时长', validators=[Optional(), NumberRange(min=0)])
    
    # 成就经历信息
    awards = TextAreaField('所获荣誉', validators=[Optional()])
    social_practice = TextAreaField('社会实践经历', validators=[Optional()])

    # 综合评分（由系统计算生成）
    comprehensive_score = IntegerField('综合评分', validators=[Optional(), NumberRange(min=0, max=100)])

    # 密码（仅用于添加新学生时）
    password = PasswordField('密码', validators=[
        Optional(),
        Length(min=6, max=20, message='密码长度必须在6-20位之间')
    ])

class ImportStudentsForm(FlaskForm):
    """批量导入学生表单"""
    file = FileField('Excel文件', validators=[
        FileRequired(message='请选择Excel文件'),
        FileAllowed(['xlsx', 'xls'], message='只允许上传Excel文件')
    ]) 