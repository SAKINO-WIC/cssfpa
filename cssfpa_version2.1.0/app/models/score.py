from app import db
from datetime import datetime
import json

# 从score_config模块导入StudentScore模型
from app.models.score_config import StudentScore

class Item(db.Model):
    """评分项目表"""
    __tablename__ = 'score_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 项目名称
    code = db.Column(db.String(50), nullable=False, unique=True)  # 项目代码，唯一标识
    category = db.Column(db.String(50))  # 项目分类，如学术、活动、奖励等
    description = db.Column(db.Text)  # 项目描述
    weight = db.Column(db.Float, default=1.0)  # 项目权重
    max_score = db.Column(db.Float)  # 最高分值
    
    # 关联的评分记录
    scores = db.relationship('Score', backref='item', lazy=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Item {self.name}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'category': self.category,
            'description': self.description,
            'weight': self.weight,
            'max_score': self.max_score
        }

class Score(db.Model):
    """学生具体评分记录表"""
    __tablename__ = 'scores'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))  # 学生ID
    item_id = db.Column(db.Integer, db.ForeignKey('score_items.id'))  # 评分项目ID
    score = db.Column(db.Float, default=0)  # 得分
    remarks = db.Column(db.Text)  # 评分备注
    
    # 评分人和时间
    scored_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    scored_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Score {self.student_id}-{self.item_id}: {self.score}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'item_id': self.item_id,
            'score': self.score,
            'remarks': self.remarks,
            'scored_by': self.scored_by,
            'scored_at': self.scored_at.strftime('%Y-%m-%d %H:%M:%S') if self.scored_at else None
        }
