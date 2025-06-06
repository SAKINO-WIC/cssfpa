from app import db
from datetime import datetime

class Achievement(db.Model):
    """学生获奖成就表"""
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))  # 关联学生ID
    name = db.Column(db.String(100), nullable=False)  # 奖项名称
    level = db.Column(db.String(50))  # 获奖等级，例如校级、省级、国家级
    organization = db.Column(db.String(100))  # 颁发组织/单位
    award_date = db.Column(db.Date)  # 获奖日期
    description = db.Column(db.Text)  # 详细描述
    certificate_path = db.Column(db.String(255))  # 证书文件路径
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Achievement {self.name} - {self.student_id}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'level': self.level,
            'organization': self.organization,
            'award_date': self.award_date.strftime('%Y-%m-%d') if self.award_date else None,
            'description': self.description,
            'certificate_path': self.certificate_path
        }
