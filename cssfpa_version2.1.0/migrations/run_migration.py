#!/usr/bin/env python3
"""
运行数据库迁移脚本，更新学生无挂科记录字段
"""
from flask_migrate import Migrate, upgrade
from app import create_app, db

app = create_app()
migrate = Migrate(app, db)

with app.app_context():
    print("开始执行数据库迁移...")
    upgrade()
    print("数据库迁移完成！")
    
    # 验证迁移结果
    from app.models.student import Student
    students = Student.query.all()
    for student in students:
        print(f"学生 {student.student_id}: {student.name}")
        print(f" - 无挂科记录: {student.no_failed_course}")
    
    print(f"总共更新了 {len(students)} 名学生的记录") 