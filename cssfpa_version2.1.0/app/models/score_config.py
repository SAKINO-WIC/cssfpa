from app import db
import json
from datetime import datetime

class ScoreConfig(db.Model):
    """评分配置表，用于存储评分标准配置"""
    __tablename__ = 'score_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default='默认评分配置')  # 配置名称
    is_default = db.Column(db.Boolean, default=False)  # 是否是默认配置
    is_active = db.Column(db.Boolean, default=False)   # 是否当前使用的配置
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 创建人
    active = db.Column(db.Boolean, default=True)  # 是否激活
    
    # 评分配置JSON，使用JSON存储复杂的评分规则
    config_json = db.Column(db.Text, nullable=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def config(self):
        """将JSON字符串转换为Python字典"""
        try:
            return json.loads(self.config_json)
        except Exception:
            return {}
    
    @config.setter
    def config(self, value):
        """将Python字典转换为JSON字符串存储"""
        self.config_json = json.dumps(value, ensure_ascii=False)
    
    @classmethod
    def get_default_config(cls):
        """获取默认配置"""
        default_config = cls.query.filter_by(is_default=True, active=True).first()
        if not default_config:
            default_config = cls.create_default_config()
        return default_config
    
    @classmethod
    def get_active_config(cls):
        """获取当前活跃的配置"""
        active_config = cls.query.filter_by(is_active=True, active=True).first()
        if not active_config:
            # 如果没有活跃配置，使用默认配置
            active_config = cls.get_default_config()
            active_config.is_active = True
            db.session.commit()
        return active_config
    
    @classmethod
    def create_default_config(cls):
        """创建默认配置"""
        default_config = cls(
            name="默认评分配置",
            is_default=True,
            is_active=True,
            config=cls.get_default_config_dict()
        )
        db.session.add(default_config)
        db.session.commit()
        return default_config
    
    @staticmethod
    def get_default_config_dict():
        """获取默认配置字典"""
        return {
            'base_score': 60,  # 基础条件满足后得分
            'academic_weight': 0.15,  # 综测成绩权重
            'scholarship_settings': {
                'national_first': 10,
                'national_second': 8,
                'national_third': 6,
                'school_first': 5,
                'school_second': 3,
                'school_third': 2
            },
            'volunteer_settings': {
                'base_score': 5,
                'per_hour': 0.5,
                'min_hours': 10,
                'max_hours': 30
            },
            'english_settings': {
                'cet4_pass_score': 425,
                'cet4_pass_points': 5,
                'cet4_excellent_score': 550,
                'cet4_excellent_points': 8,
                'cet6_pass_score': 425,
                'cet6_pass_points': 8,
                'cet6_excellent_score': 550,
                'cet6_excellent_points': 10
            }
        }
    
    def __repr__(self):
        return f'<ScoreConfig {self.name}>'

class StudentScore(db.Model):
    """学生评分记录表，用于存储学生的评分历史"""
    __tablename__ = 'student_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), db.ForeignKey('students.student_id'))  # 学生ID
    score_config_id = db.Column(db.Integer, db.ForeignKey('score_configs.id'))  # 使用的评分配置
    
    # 各项评分明细
    base_score = db.Column(db.Float, default=0)  # 基础分
    academic_score = db.Column(db.Float, default=0)  # 学业分
    scholarship_score = db.Column(db.Float, default=0)  # 奖学金分
    volunteer_score = db.Column(db.Float, default=0)  # 志愿服务分
    english_score = db.Column(db.Float, default=0)  # 英语分
    
    total_score = db.Column(db.Float, default=0)  # 总分
    passed_base_conditions = db.Column(db.Boolean, default=False)  # 是否满足基础条件
    
    # 评分备注
    remark = db.Column(db.Text)
    
    # 评分详情JSON，存储详细的评分过程和数据
    score_detail_json = db.Column(db.Text)
    
    # 评分人和时间
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def score_detail(self):
        """将JSON字符串转换为Python字典"""
        try:
            return json.loads(self.score_detail_json)
        except Exception:
            return {}
    
    @score_detail.setter
    def score_detail(self, value):
        """将Python字典转换为JSON字符串存储"""
        self.score_detail_json = json.dumps(value, ensure_ascii=False)
    
    def __repr__(self):
        return f'<StudentScore {self.student_id} {self.total_score}分>' 