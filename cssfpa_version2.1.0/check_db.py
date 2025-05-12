import os
import sqlite3

# 检查文件是否存在
db_path = "D:\\CURSORHOME\\cssfpa\\cssfpa_version2.1.0\\app.db"
if os.path.exists(db_path):
    print(f"数据库文件存在: {db_path}")
    # 尝试打开数据库连接
    try:
        conn = sqlite3.connect(db_path)
        print("成功连接到数据库")
        # 检查是否有表
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"数据库中的表: {tables}")
        conn.close()
    except Exception as e:
        print(f"无法连接到数据库: {e}")
else:
    print(f"数据库文件不存在: {db_path}")
    
# 检查当前目录
print(f"当前工作目录: {os.getcwd()}")
print(f"目录中的文件:")
for file in os.listdir('.'):
    if os.path.isfile(file):
        print(f" - {file} ({os.path.getsize(file)} 字节)") 