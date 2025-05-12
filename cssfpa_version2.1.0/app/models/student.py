from app import db
from datetime import datetime

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # 个人基本信息
    student_id = db.Column(db.String(20), unique=True, nullable=False)  # 学号
    name = db.Column(db.String(50), nullable=False)                    # 姓名
    gender = db.Column(db.String(10), nullable=False)                  # 性别
    ethnicity = db.Column(db.String(20))                              # 民族
    hometown = db.Column(db.String(100))                              # 籍贯
    birth_date = db.Column(db.Date)                                   # 出生日期
    id_card = db.Column(db.String(18))                               # 身份证号
    phone = db.Column(db.String(11))                                 # 手机号码
    email = db.Column(db.String(64))                                 # 电子邮箱
    address = db.Column(db.String(200))                              # 家庭住址

    # 学籍信息
    department = db.Column(db.String(100))                           # 院系
    major = db.Column(db.String(100))                               # 专业
    class_name = db.Column(db.String(50))                           # 班级
    enrollment_date = db.Column(db.Date)                            # 入学日期
    
    # 政治信息
    political_status = db.Column(db.String(20))                     # 政治面貌
    league_member_id = db.Column(db.String(20))                     # 团员编号
    league_branch = db.Column(db.String(100))                       # 团支部
    league_join_date = db.Column(db.Date)                           # 入团时间
    has_application = db.Column(db.Boolean, default=False, comment="是否递交入党申请书")
    application_date = db.Column(db.Date)                           # 递交入党申请书时间
    passed_exam = db.Column(db.Boolean, default=False, comment="是否通过党课考试")
    class_approved = db.Column(db.Boolean, default=False, comment="是否通过班级推优")
    has_failed_course = db.Column(db.Boolean, default=False, comment="是否有挂科记录")
    
    # 学业信息
    comprehensive_test_score = db.Column(db.Float, default=0, comment="综合测评成绩")
    comprehensive_score = db.Column(db.Integer)                     # 综合评分（评分系统计算结果）
    english_level = db.Column(db.String(20))                        # 英语等级考试成绩(旧字段)
    cet4_score = db.Column(db.Integer)                              # CET4考试成绩
    cet6_score = db.Column(db.Integer)                              # CET6考试成绩
    scholarship = db.Column(db.Text)                                # 奖学金获得情况
    volunteer_hours = db.Column(db.Integer, default=0)              # 志愿服务时长
    
    # 成就经历信息
    awards = db.Column(db.Text)                                     # 获奖情况
    social_practice = db.Column(db.Text)                            # 社会实践经历
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 文件关联
    files = db.relationship('StudentFile', backref='student', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Student {self.name}>'
    
    def to_dict(self):
        return {
            'student_id': self.student_id,
            'name': self.name,
            'gender': self.gender,
            'ethnicity': self.ethnicity,
            'hometown': self.hometown,
            'birth_date': self.birth_date.strftime('%Y-%m-%d') if self.birth_date else None,
            'id_card': self.id_card,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'department': self.department,
            'major': self.major,
            'class_name': self.class_name,
            'enrollment_date': self.enrollment_date.strftime('%Y-%m-%d') if self.enrollment_date else None,
            'political_status': self.political_status,
            'league_member_id': self.league_member_id,
            'league_branch': self.league_branch,
            'league_join_date': self.league_join_date.strftime('%Y-%m') if self.league_join_date else None,
            'has_application': self.has_application,
            'application_date': self.application_date.strftime('%Y-%m') if self.application_date else None,
            'passed_exam': self.passed_exam,
            'class_approved': self.class_approved,
            'has_failed_course': self.has_failed_course,
            'comprehensive_test_score': self.comprehensive_test_score,
            'comprehensive_score': self.comprehensive_score,
            'english_level': self.english_level,
            'cet4_score': self.cet4_score,
            'cet6_score': self.cet6_score,
            'scholarship': self.scholarship,
            'volunteer_hours': self.volunteer_hours,
            'awards': self.awards,
            'social_practice': self.social_practice
        }

class StudentFile(db.Model):
    __tablename__ = 'student_files'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # 文件类型：个人信息文件、入党申请书文件、证书文件、其它文件
    description = db.Column(db.Text, nullable=False)      # 文件说明
    file_size = db.Column(db.Integer, default=0)          # 文件大小(字节)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f'<StudentFile {self.filename}>'