# 定义简单的翻译字典
translations = {
    'en': {
        # 基础UI
        '入党积极分子综合评分系统': 'Party Applicant Evaluation System',
        '欢迎，': 'Welcome, ',
        '退出': 'Logout',
        
        # 登录页面
        '登录': 'Login',
        '用户登录': 'User Login',
        '欢迎使用入党积极分子综合评分系统': 'Welcome to Party Applicant Evaluation System',
        '角色': 'Role',
        '请输入角色': 'Select a role',
        '用户名': 'Username',
        '请输入用户名': 'Enter username',
        '密码': 'Password',
        '请输入密码': 'Enter password',
        '记住我': 'Remember Me',
        '忘记密码？': 'Forgot Password?',
        '版本': 'Version',
        
        # 角色提示
        '请输入学号': 'Enter Student ID',
        '请输入密码 (初始为身份证后6位)': 'Enter Password (Default: Last 6 digits of ID)',
        '请输入教师工号': 'Enter Teacher ID',
        '请输入管理员账号': 'Enter Admin Account',
        '请输入管理员密码': 'Enter Admin Password',
        '请先选择角色': 'Select Role First',
        
        # 新增表单相关字符串
        '请选择登录角色': 'Please select a role',
        '学生': 'Student',
        '教师': 'Teacher',
        '管理员': 'Administrator',
        '用户名不能为空': 'Username cannot be empty',
        '用户名长度必须在4-20位之间': 'Username must be 4-20 characters',
        '密码不能为空': 'Password cannot be empty',
        '密码长度必须在6-20位之间': 'Password must be 6-20 characters'
    }
}

def translate_text(text, locale):
    """将文本翻译为指定语言"""
    if locale == 'zh':
        return text
    
    if locale in translations and text in translations[locale]:
        return translations[locale][text]
    
    # 如果没有找到翻译，返回原文本
    return text 