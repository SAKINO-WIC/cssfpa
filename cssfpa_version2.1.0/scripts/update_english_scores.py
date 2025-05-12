#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models.student import Student
import random
import re
import sys

app = create_app()

def is_score_format(text):
    """判断是否已经是分数格式：CET-x xxx"""
    if not text:
        return False
    return bool(re.match(r'CET-[46]\s+\d{3,}', text))

def extract_score(text):
    """从CET-x xxx格式中提取分数"""
    if not text:
        return None
    match = re.search(r'(\d{3,})', text)
    if match:
        return int(match.group(1))
    return None

def generate_cet_score(level):
    """
    根据原有的英语等级生成合理的分数
    CET-4/6的分数范围通常是220-710分，425分为及格线
    """
    # 如果已经是分数格式，保留原有分数
    if is_score_format(level):
        return level
        
    if level == "四级":
        # 四级分数: 15%不及格(220-424), 75%及格(425-550), 10%优秀(551-710)
        score_range = random.choices(
            [random.randint(220, 424), random.randint(425, 550), random.randint(551, 710)],
            weights=[15, 75, 10]
        )[0]
        return f"CET-4 {score_range}"
    elif level == "六级":
        # 六级分数: 20%不及格(220-424), 70%及格(425-550), 10%优秀(551-710)
        score_range = random.choices(
            [random.randint(220, 424), random.randint(425, 550), random.randint(551, 710)],
            weights=[20, 70, 10]
        )[0]
        return f"CET-6 {score_range}"
    else:
        # 未参加英语等级考试的情况
        status = random.choices(
            ["未参加", "CET-4 考试中", "报名中"],
            weights=[70, 20, 10]
        )[0]
        return status

def update_english_levels():
    """更新所有学生的英语等级考试成绩"""
    try:
        with app.app_context():
            students = Student.query.all()
            print(f"开始更新 {len(students)} 名学生的英语等级考试成绩")
            
            # 统计原始数据分布
            original_stats = {"四级": 0, "六级": 0, "无": 0, "其他": 0}
            for student in students:
                level = student.english_level or "无"
                if level in original_stats:
                    original_stats[level] += 1
                else:
                    original_stats["其他"] += 1
            
            print("原始数据分布:")
            for level, count in original_stats.items():
                print(f"{level}: {count} 人")
            
            # 更新英语成绩
            updated_count = 0
            preserved_count = 0
            new_stats = {}
            
            try:
                for student in students:
                    original_level = student.english_level or "无"
                    
                    # 检查是否已经是分数格式
                    if is_score_format(original_level):
                        preserved_count += 1
                    else:
                        new_score = generate_cet_score(original_level)
                        student.english_level = new_score
                    
                    # 更新统计
                    current_level = student.english_level
                    if current_level in new_stats:
                        new_stats[current_level] += 1
                    else:
                        new_stats[current_level] = 1
                        
                    updated_count += 1
                    
                    if updated_count % 50 == 0:
                        print(f"已处理 {updated_count}/{len(students)} 名学生的英语成绩")
                
                # 保存更改
                db.session.commit()
                print(f"\n保留了 {preserved_count} 名学生的原有成绩格式")
                
                # CET-4/6 类别统计
                cet4_count = sum(count for score, count in new_stats.items() if "CET-4" in score)
                cet6_count = sum(count for score, count in new_stats.items() if "CET-6" in score)
                other_count = sum(count for score, count in new_stats.items() 
                                  if "CET-4" not in score and "CET-6" not in score)
                
                print("\n更新后的数据分布:")
                print(f"CET-4: {cet4_count} 人")
                print(f"CET-6: {cet6_count} 人")
                print(f"其他情况: {other_count} 人")
                
                # 统计及格情况
                try:
                    pass_count = sum(count for score, count in new_stats.items() 
                                    if extract_score(score) is not None and extract_score(score) >= 425)
                    fail_count = sum(count for score, count in new_stats.items() 
                                    if extract_score(score) is not None and extract_score(score) < 425)
                    excellent_count = sum(count for score, count in new_stats.items() 
                                        if extract_score(score) is not None and extract_score(score) >= 551)
                    
                    print(f"\n及格人数: {pass_count}")
                    print(f"不及格人数: {fail_count}")
                    print(f"优秀人数: {excellent_count}")
                except Exception as e:
                    print(f"统计及格情况时出错: {e}")
                
                print("\n英语等级考试成绩更新完成!")
                
            except Exception as e:
                db.session.rollback()
                print(f"更新过程中出错: {e}")
                return False
    
    except Exception as e:
        print(f"程序初始化出错: {e}")
        return False
        
    return True

if __name__ == "__main__":
    success = update_english_levels()
    sys.exit(0 if success else 1) 