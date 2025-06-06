from app import db
from datetime import datetime

class Practice(db.Model):
    """学生社会实践经历表"""
    __tablename__ = 'practices'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))  # 关联学生ID
    title = db.Column(db.String(100), nullable=False)  # 实践活动名称
    organization = db.Column(db.String(100))  # 组织/单位名称
    start_date = db.Column(db.Date)  # 开始日期
    end_date = db.Column(db.Date)  # 结束日期
    hours = db.Column(db.Integer)  # 服务/实践时长(小时)
    description = db.Column(db.Text)  # 详细描述
    certificate_path = db.Column(db.String(255))  # 证明文件路径
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Practice {self.title} - {self.student_id}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'title': self.title,
            'organization': self.organization,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'hours': self.hours,
            'description': self.description,
            'certificate_path': self.certificate_path
        }
