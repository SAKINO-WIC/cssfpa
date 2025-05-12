import os
import sys
from app import create_app, db

# 确保工作目录设置正确
basedir = os.path.abspath(os.path.dirname(__file__))
os.chdir(basedir)

# 显示当前工作目录
print(f"当前工作目录: {os.getcwd()}")

try:
    app = create_app()
    
    # 显示已配置的数据库URI和实际使用的URI
    print(f"数据库URI配置: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"数据库引擎: {db.engine}")
    
    # 尝试连接数据库
    with app.app_context():
        try:
            # 测试连接并获取表列表
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"成功连接数据库，表列表: {tables}")
        except Exception as e:
            print(f"数据库连接失败: {e}")
            
except Exception as e:
    print(f"应用程序初始化失败: {e}")
    import traceback
    traceback.print_exc() 