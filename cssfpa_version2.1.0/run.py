import os
import sys
import traceback
from app import create_app

# 确保工作目录设置正确
basedir = os.path.abspath(os.path.dirname(__file__))
os.chdir(basedir)

# 显示当前工作目录和实例文件夹路径
instance_path = os.path.join(basedir, 'instance')
print(f"当前工作目录: {os.getcwd()}")
print(f"实例文件夹路径: {instance_path}")
print(f"实例文件夹是否存在: {os.path.exists(instance_path)}")

try:
    app = create_app()
    
    # 强制更新数据库URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
    print(f"已强制更新数据库URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    if __name__ == '__main__':
        app.run(debug=True)
except Exception as e:
    print("应用程序启动出错:")
    print(str(e))
    traceback.print_exc()
    sys.exit(1) 