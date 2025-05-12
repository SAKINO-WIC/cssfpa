#!/usr/bin/env python3
"""
用于修复学生挂科状态的数据库工具

使用方法：
1. 导入到Flask shell中：
   from app.utils.db_fix import update_student_failed_status
2. 设置某个学生的挂科状态：
   update_student_failed_status('学号', has_failed=True) 或 False
3. 批量设置所有学生为没有挂科：
   update_all_students_no_failed()
"""
from app import db
from app.models.student import Student
import logging

logger = logging.getLogger(__name__)

def update_student_failed_status(student_id, has_failed=False):
    """
    更新指定学生的挂科状态
    
    Args:
        student_id (str): 学生学号
        has_failed (bool): True表示有挂科，False表示无挂科
    
    Returns:
        bool: 更新成功返回True，否则返回False
    """
    try:
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            logger.error(f"找不到学号为 {student_id} 的学生")
            return False
        
        student.has_failed_course = has_failed
        db.session.commit()
        
        # 验证更新成功
        student = Student.query.filter_by(student_id=student_id).first()
        logger.info(f"学生 {student.name}({student_id}) 的挂科状态已更新为: {'有挂科' if has_failed else '无挂科'}")
        return True
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新学生挂科状态时出错: {str(e)}")
        return False

def update_all_students_no_failed():
    """将所有学生的挂科状态设置为无挂科（has_failed_course=False）"""
    try:
        students = Student.query.all()
        count = 0
        
        for student in students:
            student.has_failed_course = False
            count += 1
        
        db.session.commit()
        logger.info(f"已将 {count} 名学生的挂科状态设置为无挂科")
        return True
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"批量更新学生挂科状态时出错: {str(e)}")
        return False

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    
    with app.app_context():
        print("此脚本用于修复学生挂科状态")
        print("1. 将所有学生设置为无挂科")
        print("2. 为指定学生设置挂科状态")
        
        choice = input("请选择操作 (1/2): ")
        
        if choice == "1":
            success = update_all_students_no_failed()
            print("操作" + ("成功" if success else "失败"))
        
        elif choice == "2":
            student_id = input("请输入学生学号: ")
            has_failed = input("该学生是否有挂科 (y/n): ").lower() == "y"
            
            success = update_student_failed_status(student_id, has_failed)
            print("操作" + ("成功" if success else "失败")) 