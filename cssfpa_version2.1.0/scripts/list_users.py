from app import create_app, db
from app.models.user import User

def list_users():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        print('\n===== 用户列表 =====')
        for user in users:
            print(f'ID: {user.id}, 用户名: {user.username}, 角色: {user.role}')
            if user.role == 'student' and user.student:
                print(f'  关联学生: {user.student.name}, 学号: {user.student.student_id}')
        
        # 按角色统计用户数量
        admin_count = User.query.filter_by(role='admin').count()
        teacher_count = User.query.filter_by(role='teacher').count()
        student_count = User.query.filter_by(role='student').count()
        
        print('\n===== 用户统计 =====')
        print(f'管理员: {admin_count}人')
        print(f'教师: {teacher_count}人')
        print(f'学生: {student_count}人')
        print(f'总用户数: {len(users)}人')

if __name__ == '__main__':
    list_users() 