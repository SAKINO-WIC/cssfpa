from app import create_app, db
from app.models.student import Student
import datetime

def check_dates():
    app = create_app()
    with app.app_context():
        print('\n========== 检查学生日期数据 ==========')
        
        # 获取全部学生记录
        students = Student.query.all()
        print(f'总学生数: {len(students)}')
        
        # 检查入团时间
        league_dates = {}
        for student in students:
            if student.league_join_date:
                date_str = student.league_join_date.strftime('%Y-%m-%d')
                # 统计各入团日期的学生人数
                if date_str not in league_dates:
                    league_dates[date_str] = 1
                else:
                    league_dates[date_str] += 1
        
        print('\n入团日期分布:')
        for date, count in sorted(league_dates.items()):
            # 检查是否为青年节(5月4日)或12月9日
            is_valid = (date[5:] == '05-04' or date[5:] == '12-09')
            print(f'  {date}: {count}人 {"✓" if is_valid else "❌"}')
        
        # 检查入团日期的年份范围
        years = set([date.split('-')[0] for date in league_dates.keys()])
        print(f'\n入团日期年份范围: {min(years)} 到 {max(years)}')
        
        # 检查申请书日期
        app_dates = {}
        app_count = 0
        no_app_count = 0
        invalid_status = 0
        
        for student in students:
            if student.has_application:
                app_count += 1
                if student.application_date:
                    date_str = student.application_date.strftime('%Y-%m-%d')
                    # 统计各申请日期的学生人数
                    if date_str not in app_dates:
                        app_dates[date_str] = 1
                    else:
                        app_dates[date_str] += 1
                else:
                    # 已申请但无日期
                    invalid_status += 1
                    print(f'  警告: 学生 {student.id} {student.name} 已递交申请但无申请日期')
            else:
                no_app_count += 1
                if student.application_date:
                    # 未申请但有日期
                    invalid_status += 1
                    print(f'  警告: 学生 {student.id} {student.name} 未递交申请但有申请日期: {student.application_date}')
        
        print(f'\n已递交申请书学生: {app_count}人')
        print(f'未递交申请书学生: {no_app_count}人')
        print(f'状态不一致记录: {invalid_status}人')
        
        if app_dates:
            print('\n申请书日期分布:')
            for date, count in sorted(app_dates.items()):
                # 检查是否在2023-2024年范围内
                is_valid = (date.startswith('2023') or date.startswith('2024'))
                print(f'  {date}: {count}人 {"✓" if is_valid else "❌"}')
        
        print('\n========== 检查完成 ==========')

if __name__ == '__main__':
    check_dates() 