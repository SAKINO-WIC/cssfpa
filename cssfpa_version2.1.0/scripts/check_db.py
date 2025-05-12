from app import create_app, db
from app.models.student import Student

def check_db():
    app = create_app()
    with app.app_context():
        print('\n学生记录:')
        students = Student.query.limit(10).all()  # 只获取前10个记录
        for s in students:
            print(f'ID: {s.id}, 姓名: {s.name}, 入团时间: {s.league_join_date}, 递交申请书: {s.has_application}, 申请时间: {s.application_date}')
        
        # 检查是否有入团时间为空的记录
        null_dates = Student.query.filter(Student.league_join_date == None).count()
        print(f'\n入团时间为空的记录数: {null_dates}')
        
        # 检查有申请但申请时间为空的记录
        missing_app_dates = Student.query.filter(Student.has_application == True, 
                                               Student.application_date == None).count()
        print(f'有申请但申请时间为空的记录数: {missing_app_dates}')

if __name__ == '__main__':
    check_db() 