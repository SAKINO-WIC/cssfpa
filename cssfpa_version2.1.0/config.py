import os
import sqlite3
from datetime import timedelta

# 确保实例目录存在
INSTANCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance'))
if not os.path.exists(INSTANCE_DIR):
    try:
        os.makedirs(INSTANCE_DIR)
        print(f"已创建实例目录: {INSTANCE_DIR}")
    except Exception as e:
        print(f"无法创建实例目录: {e}")

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    
    # 数据库配置 - 强制使用当前目录下的app.db
    DB_PATH = 'D:/CURSORHOME/cssfpa/cssfpa_version2.1.0/app.db'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'app', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
    
    # Session配置
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # 分页配置
    ITEMS_PER_PAGE = 10 
    
    # 国际化配置
    LANGUAGES = ['zh', 'en']
    BABEL_DEFAULT_LOCALE = 'zh'
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(BASEDIR, 'app/translations')
    
    # 测试数据库连接
    try:
        # 尝试打开数据库文件
        test_conn = sqlite3.connect(SQLALCHEMY_DATABASE_URI.split('///')[1])
        test_conn.close()
        print(f"成功连接数据库: {SQLALCHEMY_DATABASE_URI}")
    except Exception as e:
        print(f"警告: 无法连接数据库文件: {SQLALCHEMY_DATABASE_URI}")
        print(f"错误: {e}") 