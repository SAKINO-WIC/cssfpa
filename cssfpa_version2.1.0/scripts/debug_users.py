#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
调试脚本：查看用户和权限
"""

from app import create_app, db
from app.models.user import User
from app.models.student import Student

app = create_app()

with app.app_context():
    print("=== 用户数据 ===")
    users = User.query.all()
    print(f"总用户数：{len(users)}")
    
    for user in users:
        print(f"ID: {user.id}, 用户名: {user.username}, 角色: {user.role}")
        
        # 如果是学生角色，查找关联的学生记录
        if user.role == 'student':
            student = Student.query.filter_by(student_id=user.username).first()
            if student:
                print(f"  关联学生: {student.name}, 学院: {student.department}, 专业: {student.major}")
            else:
                print(f"  警告：找不到关联的学生记录")
    
    print("\n=== 角色统计 ===")
    roles = {}
    for user in users:
        if user.role in roles:
            roles[user.role] += 1
        else:
            roles[user.role] = 1
    
    for role, count in roles.items():
        print(f"{role}: {count}人")
    
    print("\n=== 检查数据一致性 ===")
    # 检查是否有学生记录但没有对应用户
    students = Student.query.all()
    students_no_user = []
    for student in students:
        user = User.query.filter_by(username=student.student_id).first()
        if not user:
            students_no_user.append(student)
    
    if students_no_user:
        print(f"有 {len(students_no_user)} 个学生没有关联用户:")
        for student in students_no_user:
            print(f"  学号: {student.student_id}, 姓名: {student.name}")
    else:
        print("所有学生都有关联用户")
    
    # 检查是否有用户没有对应角色数据
    student_users_no_record = []
    for user in users:
        if user.role == 'student':
            student = Student.query.filter_by(student_id=user.username).first()
            if not student:
                student_users_no_record.append(user)
    
    if student_users_no_record:
        print(f"有 {len(student_users_no_record)} 个学生用户没有关联学生记录:")
        for user in student_users_no_record:
            print(f"  用户名: {user.username}")
    else:
        print("所有学生用户都有关联学生记录") 