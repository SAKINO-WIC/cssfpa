from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, IntegerField, TextAreaField, BooleanField, EmailField
from wtforms.validators import DataRequired, Optional, Length, NumberRange, Regexp, Email

class StudentProfileForm(FlaskForm):
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
        validators=[DataRequired()]
    )
    league_member_id = StringField('团员编号', validators=[Optional(), Length(max=20)])
    league_branch = StringField('团支部', validators=[Optional(), Length(max=100)])
    league_join_date = StringField('入团时间', validators=[Optional()])
    has_application = BooleanField('是否递交入党申请书')
    application_date = StringField('递交申请书时间', validators=[Optional()])
    passed_exam = BooleanField('是否通过党课考试')
    class_approved = BooleanField('是否通过支部大会表决')

    # 学业信息
    has_failed_course = BooleanField('是否有不及格课程')
    comprehensive_test_score = IntegerField('综测成绩', validators=[Optional(), NumberRange(min=0, max=100)])
    cet4_score = IntegerField('CET4成绩', validators=[Optional(), NumberRange(min=0, max=710)])
    cet6_score = IntegerField('CET6成绩', validators=[Optional(), NumberRange(min=0, max=710)])
    english_level = StringField('英语等级', validators=[Optional(), Length(max=20)])
    volunteer_hours = IntegerField('志愿服务时长', validators=[Optional(), NumberRange(min=0)])
    scholarship = TextAreaField('奖学金获得情况', validators=[Optional(), Length(max=500)])

    # 成就经历信息
    awards = TextAreaField('获奖情况', validators=[Optional(), Length(max=1000)])
    social_practice = TextAreaField('社会实践经历', validators=[Optional(), Length(max=1000)]) 