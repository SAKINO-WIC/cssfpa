from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)  # 对于学生来说，这里存储学号
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # 'student', 'teacher', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 学生用户关联到学生信息
    student = db.relationship('Student', backref='user', uselist=False)
    
    def __init__(self, username, role):
        self.username = username
        self.role = role
        # 移除自动设置密码的逻辑，由业务代码显式调用set_password方法
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def create_student_user(student):
        """
        根据学生信息创建学生用户账号
        使用学号作为用户名，学号后6位作为初始密码
        """
        user = User(
            username=student.student_id,
            role='student'
        )
        # 设置初始密码为学号后6位
        initial_password = student.student_id[-6:]
        user.set_password(initial_password)
        return user
    
    def __repr__(self):
        return f'<User {self.username}>' 