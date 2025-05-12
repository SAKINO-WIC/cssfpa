from app import create_app, db
from app.models.student import Student
from datetime import datetime, date
import random

def fix_dates():
    """修复所有学生的入团日期和申请书日期"""
    app = create_app()
    with app.app_context():
        students = Student.query.all()
        print(f"开始修复 {len(students)} 名学生的日期数据...")
        
        # 修复计数器
        league_fixed = 0
        app_fixed = 0
        
        for student in students:
            # 修复入团日期 - 所有学生都是团员
            if student.league_join_date is None:
                # 使用学号生成一个合理的入团日期
                year_enrolled = int("20" + student.student_id[:2])  # 从学号提取入学年份
                
                # 入团日期应在入学前1-2年，或入学当年
                join_year = random.choice([year_enrolled - 2, year_enrolled - 1, year_enrolled])
                join_month = random.randint(1, 12)
                join_day = random.randint(1, 28)  # 简化处理，避免月份天数问题
                
                # 确保日期合理 (不早于2017年，不晚于当前日期)
                if join_year < 2017:
                    join_year = 2017
                
                # 创建日期对象
                league_join_date = date(join_year, join_month, join_day)
                student.league_join_date = league_join_date
                league_fixed += 1
                print(f"学生 {student.name}(ID:{student.id}) 的入团日期被设置为 {league_join_date}")
            
            # 修复申请书日期
            if student.has_application and student.application_date is None:
                # 申请日期应在入学后，且合理范围内
                # 首先确定入学年份
                year_enrolled = int("20" + student.student_id[:2])  # 从学号提取入学年份
                
                # 申请日期在入学后1-2年
                app_year = random.choice([year_enrolled, year_enrolled + 1, year_enrolled + 2])
                app_month = random.randint(1, 12)
                app_day = random.randint(1, 28)  # 简化处理，避免月份天数问题
                
                # 确保日期不晚于当前日期
                current_year = datetime.now().year
                if app_year > current_year:
                    app_year = current_year
                
                # 创建日期对象
                application_date = date(app_year, app_month, app_day)
                student.application_date = application_date
                app_fixed += 1
                print(f"学生 {student.name}(ID:{student.id}) 的申请书日期被设置为 {application_date}")
        
        # 保存更改
        db.session.commit()
        print(f"日期修复完成！共修复 {league_fixed} 个入团日期和 {app_fixed} 个申请书日期。")

if __name__ == '__main__':
    fix_dates() 