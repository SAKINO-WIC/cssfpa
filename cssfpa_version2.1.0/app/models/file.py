from app import db
from datetime import datetime

class File(db.Model):
    """用户文件模型，与用户直接关联"""
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # 文件类型：如证书文件、资格证书、社会实践证明等
    description = db.Column(db.Text, nullable=False)      # 文件说明
    file_size = db.Column(db.Integer, default=0)          # 文件大小(字节)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(db.String(255), nullable=False)
    
    # 用户关联
    user = db.relationship('User', backref=db.backref('files', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<File {self.filename} - User {self.user_id}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'description': self.description,
            'file_size': self.file_size,
            'upload_date': self.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
            'file_path': self.file_path
        } 