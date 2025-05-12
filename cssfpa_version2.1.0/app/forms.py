from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, Optional
from flask_babel import lazy_gettext as _l

# 从子模块导入forms
from app.forms.auth import LoginForm

class StudentForm(FlaskForm):
    student_id = StringField(_l('学号'), validators=[DataRequired(), Length(min=4, max=20)])
    name = StringField(_l('姓名'), validators=[DataRequired(), Length(max=50)])
    gender = SelectField(_l('性别'), choices=[('男', _l('男')), ('女', _l('女'))], validators=[DataRequired()])
    class_name = StringField(_l('班级'), validators=[DataRequired(), Length(max=50)])
    major = StringField(_l('专业'), validators=[DataRequired(), Length(max=50)])
    department = StringField(_l('院系'), validators=[DataRequired(), Length(max=50)])
    phone = StringField(_l('联系电话'), validators=[Optional(), Length(max=20)])
    submit = SubmitField(_l('提交'))