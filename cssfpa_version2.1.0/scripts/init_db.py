import pandas as pd
from datetime import datetime
from app import create_app, db
from app.models.user import User
from app.models.student import Student

def convert_date(date_str):
    """转换日期字符串为date对象"""
    try:
        if pd.isna(date_str):
            return None
        # 如果是数字格式的日期（Excel序列号）
        if isinstance(date_str, (int, float)):
            try:
                return pd.Timestamp.fromordinal(datetime(1900, 1, 1).toordinal() + int(date_str) - 2).date()
            except:
                return None
        # 尝试多种日期格式
        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y年%m月%d日']:
            try:
                return datetime.strptime(str(date_str).strip(), fmt).date()
            except ValueError:
                continue
        return None
    except:
        return None

def convert_boolean(value):
    """转换是/否字符串为布尔值"""
    if pd.isna(value):
        return False
    return str(value).strip() in ['是', '1', 'True', 'true', 'YES', 'yes']

def clean_string(value):
    """清理字符串数据"""
    if pd.isna(value):
        return None
    return str(value).strip()

def clean_number(value, default=0):
    """清理数字数据"""
    try:
        if pd.isna(value):
            return default
        return int(float(value))
    except:
        return default

def init_db():
    app = create_app()
    with app.app_context():
        # 删除所有现有表
        db.drop_all()
        # 创建新表
        db.create_all()
        
        print("开始初始化数据库...")
        
        # 创建管理员账户
        admin = User(username='admin', role='admin')
        admin.set_password('admin666')  # 设置管理员密码
        db.session.add(admin)
        print("已创建管理员账户")
        
        # 创建测试教师账户
        teacher = User(username='147258369', role='teacher')
        teacher.set_password('teacher123')  # 设置教师密码
        db.session.add(teacher)
        print("已创建测试教师账户")
        
        try:
            # 读取Excel文件
            print("正在读取Excel文件...")
            df = pd.read_excel('../data/mcssfpatestdata1.xlsx')
            print(f"成功读取 {len(df)} 条数据记录")
            
            # 导入学生数据
            success_count = 0
            error_count = 0
            
            for index, row in df.iterrows():
                try:
                    # 创建学生用户账户
                    student_id = str(clean_number(row['学号']))
                    student_user = User(username=student_id, role='student')
                    db.session.add(student_user)
                    db.session.flush()  # 确保student_user有ID
                    
                    # 创建学生信息记录
                    student = Student(
                        user_id=student_user.id,  # 设置user_id外键关联
                        student_id=student_id,
                        id_card=str(clean_number(row['身份证号'])),
                        name=clean_string(row['姓名']),
                        gender=clean_string(row['性别']),
                        ethnicity=clean_string(row['民族']),
                        hometown=clean_string(row['籍贯']),
                        birth_date=convert_date(row['出生日期']),
                        phone=str(clean_number(row['手机号码'])),
                        department=clean_string(row['学院']),  # 注意：这里改为department
                        major=clean_string(row['专业']),
                        class_name=clean_string(row['班级']),
                        political_status=clean_string(row['政治面貌']),
                        league_member_id=str(clean_number(row['团员编号'])),
                        league_branch=clean_string(row['团支部']),
                        league_join_date=convert_date(row['入团时间']),
                        has_application=convert_boolean(row['是否递交入党申请书']),
                        application_date=convert_date(row['递交入党申请书时间']),
                        passed_exam=convert_boolean(row['是否通过初党考试']),
                        class_approved=convert_boolean(row['是否通过班级推优']),
                        has_failed_course=convert_boolean(row['是否挂科']),
                        comprehensive_score=clean_number(row['综测成绩']),
                        english_level=clean_string(row['英语等级考试成绩']),
                        scholarship=clean_string(row['奖学金获得情况']),
                        volunteer_hours=clean_number(row['志愿服务时长(上限100小时)']),
                        awards=clean_string(row['获奖情况']),
                        social_practice=clean_string(row['社会实践经历'])
                    )
                    db.session.add(student)
                    success_count += 1
                    
                    # 每100条数据提交一次，避免内存占用过大
                    if success_count % 100 == 0:
                        db.session.commit()
                        print(f"已成功导入 {success_count} 条数据")
                        
                except Exception as e:
                    error_count += 1
                    print(f"导入第 {index + 1} 条数据时出错：{str(e)}")
                    continue
            
            # 提交所有更改
            try:
                db.session.commit()
                print("\n数据库初始化完成！")
                print(f"成功导入 {success_count} 条学生记录")
                if error_count > 0:
                    print(f"导入失败 {error_count} 条记录")
            except Exception as e:
                db.session.rollback()
                print("数据库提交时出错！")
                print(f"错误信息：{str(e)}")
                
        except Exception as e:
            print("读取Excel文件或处理数据时出错！")
            print(f"错误信息：{str(e)}")

if __name__ == '__main__':
    init_db()