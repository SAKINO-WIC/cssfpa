#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models.student import Student
from sqlalchemy import Column, Integer, text
import random
import re
import sys

app = create_app()

def add_cet_columns():
    """添加CET4和CET6成绩字段"""
    with app.app_context():
        # 检查是否已经存在这些列
        inspector = db.inspect(db.engine)
        columns = [c['name'] for c in inspector.get_columns('students')]
        
        if 'cet4_score' not in columns or 'cet6_score' not in columns:
            print("添加CET4和CET6成绩字段...")
            
            # 使用ALTER TABLE语句添加新列
            db.session.execute(text('ALTER TABLE students ADD COLUMN cet4_score INTEGER'))
            db.session.execute(text('ALTER TABLE students ADD COLUMN cet6_score INTEGER'))
            db.session.commit()
            print("成功添加新字段")
        else:
            print("CET4和CET6字段已存在")

def extract_score_from_text(text):
    """从原有格式中提取分数"""
    if not text:
        return None
    
    # 尝试从 "CET-4 450" 或 "四级450" 等格式提取分数
    match = re.search(r'(\d{3,})', text)
    if match:
        return int(match.group(1))
    return None

def generate_random_score(is_pass=True):
    """生成随机CET分数"""
    if is_pass:
        # 及格分数 (425-710)
        return random.randint(425, 710)
    else:
        # 不及格分数 (220-424)
        return random.randint(220, 424)

def migrate_english_scores():
    """将原有的英语等级数据迁移到新的字段"""
    with app.app_context():
        students = Student.query.all()
        print(f"开始迁移 {len(students)} 名学生的英语成绩数据")
        
        # 统计
        stats = {
            "总学生数": len(students),
            "CET4有成绩": 0,
            "CET6有成绩": 0,
            "CET4及格": 0,
            "CET6及格": 0,
            "CET4不及格": 0,
            "CET6不及格": 0,
            "无成绩": 0
        }
        
        for student in students:
            original = student.english_level or ""
            
            # 提取可能已有的分数
            score = extract_score_from_text(original)
            
            # 根据原始数据决定填充哪个字段
            if "四级" in original or "CET-4" in original or "CET4" in original:
                # 分配到CET4
                if score:
                    student.cet4_score = score
                else:
                    # 随机生成分数
                    student.cet4_score = generate_random_score(random.random() < 0.8)  # 80%概率及格
                
                stats["CET4有成绩"] += 1
                if student.cet4_score >= 425:
                    stats["CET4及格"] += 1
                else:
                    stats["CET4不及格"] += 1
                    
            elif "六级" in original or "CET-6" in original or "CET6" in original:
                # 分配到CET6
                if score:
                    student.cet6_score = score
                else:
                    # 随机生成分数，六级及格率略低
                    student.cet6_score = generate_random_score(random.random() < 0.7)  # 70%概率及格
                
                stats["CET6有成绩"] += 1
                if student.cet6_score >= 425:
                    stats["CET6及格"] += 1
                else:
                    stats["CET6不及格"] += 1
                
                # 通常有CET6成绩的也应该有CET4成绩
                if not student.cet4_score:
                    student.cet4_score = generate_random_score(True)  # 肯定及格
                    stats["CET4有成绩"] += 1
                    stats["CET4及格"] += 1
            
            else:
                # 无考试记录
                stats["无成绩"] += 1
        
        # 为部分无成绩的学生随机分配CET4成绩
        no_score_students = [s for s in students if not s.cet4_score and not s.cet6_score]
        for student in no_score_students:
            # 50%概率参加过CET4
            if random.random() < 0.5:
                student.cet4_score = generate_random_score(random.random() < 0.75)  # 75%概率及格
                stats["CET4有成绩"] += 1
                stats["无成绩"] -= 1
                if student.cet4_score >= 425:
                    stats["CET4及格"] += 1
                else:
                    stats["CET4不及格"] += 1
        
        # 保存更改
        db.session.commit()
        
        # 输出统计
        print("\n--- 成绩迁移统计 ---")
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        # 计算及格率
        cet4_pass_rate = stats["CET4及格"] / stats["CET4有成绩"] * 100 if stats["CET4有成绩"] > 0 else 0
        cet6_pass_rate = stats["CET6及格"] / stats["CET6有成绩"] * 100 if stats["CET6有成绩"] > 0 else 0
        
        print(f"\nCET4及格率: {cet4_pass_rate:.2f}%")
        print(f"CET6及格率: {cet6_pass_rate:.2f}%")
        print(f"无成绩学生比例: {stats['无成绩'] / stats['总学生数'] * 100:.2f}%")

def remove_english_level_field():
    """移除原有的英语等级字段(暂不实际删除，防止出错)"""
    print("注意: 新字段已创建并填充数据，但原有english_level字段暂未删除")
    print("可以在确认数据正确后，手动执行以下SQL语句删除该字段:")
    print("ALTER TABLE students DROP COLUMN english_level;")

def main():
    """主函数"""
    try:
        print("=== 开始更新英语成绩数据 ===")
        
        # 步骤1: 添加新列
        add_cet_columns()
        
        # 步骤2: 数据迁移
        migrate_english_scores()
        
        # 步骤3: 移除旧列(展示说明)
        remove_english_level_field()
        
        print("=== 英语成绩数据更新完成 ===")
        return True
        
    except Exception as e:
        print(f"更新过程中出错: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 