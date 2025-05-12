from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length
from flask_babel import lazy_gettext as _l

class LoginForm(FlaskForm):
    role = SelectField(_l('角色'), choices=[
        ('', _l('请选择登录角色')),
        ('student', _l('学生')),
        ('teacher', _l('教师')),
        ('admin', _l('管理员'))
    ], validators=[DataRequired(message=_l('请选择登录角色'))])
    
    username = StringField(_l('用户名'), validators=[
        DataRequired(message=_l('用户名不能为空')),
        Length(min=4, max=20, message=_l('用户名长度必须在4-20位之间'))
    ])
    
    password = PasswordField(_l('密码'), validators=[
        DataRequired(message=_l('密码不能为空')),
        Length(min=6, max=20, message=_l('密码长度必须在6-20位之间'))
    ])
    
    remember_me = BooleanField(_l('记住我'))
    
    submit = SubmitField(_l('登录')) 