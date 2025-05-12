import os
import sys
import subprocess
import platform

def setup_project():
    """
    初始化项目环境
    1. 创建虚拟环境
    2. 安装依赖
    3. 创建必要的目录
    """
    print("===== 入党积极分子综合评分系统 - 环境初始化 =====")
    
    # 检查Python版本
    py_version = platform.python_version()
    print(f"检测到Python版本: {py_version}")
    if int(py_version.split('.')[0]) < 3 or (int(py_version.split('.')[0]) == 3 and int(py_version.split('.')[1]) < 9):
        print("警告: 推荐使用Python 3.9或更高版本!")
    
    # 创建必要的目录
    os.makedirs('app/uploads', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    print("已创建必要的目录结构")
    
    # 检查是否已存在虚拟环境
    venv_dir = 'venv'
    if os.path.exists(venv_dir):
        print(f"检测到已存在的虚拟环境: {venv_dir}")
        proceed = input("是否重新创建虚拟环境? (y/n): ")
        if proceed.lower() != 'y':
            print("跳过虚拟环境创建")
        else:
            # 重新创建虚拟环境
            create_virtualenv(venv_dir)
    else:
        # 创建虚拟环境
        create_virtualenv(venv_dir)
    
    # 安装依赖
    install_dependencies()
    
    print("\n===== 环境初始化完成 =====")
    print("您现在可以运行以下命令开始使用系统:")
    
    if platform.system() == 'Windows':
        print("\n激活虚拟环境:")
        print("   venv\\Scripts\\activate")
    else:
        print("\n激活虚拟环境:")
        print("   source venv/bin/activate")
    
    print("\n初始化数据库:")
    print("   python scripts/init_db.py")
    
    print("\n启动应用:")
    print("   python run.py")
    
    print("\n系统初始账户:")
    print("   管理员: admin / admin666")
    print("   教师: 147258369 / teacher123")

def create_virtualenv(venv_dir):
    """创建Python虚拟环境"""
    print(f"\n创建虚拟环境: {venv_dir}")
    try:
        subprocess.run([sys.executable, '-m', 'venv', venv_dir], check=True)
        print("虚拟环境创建成功!")
    except subprocess.CalledProcessError as e:
        print(f"创建虚拟环境失败: {e}")
        sys.exit(1)

def install_dependencies():
    """安装项目依赖"""
    print("\n安装项目依赖")
    
    # 确定pip的路径
    if platform.system() == 'Windows':
        pip_path = os.path.join('venv', 'Scripts', 'pip')
    else:
        pip_path = os.path.join('venv', 'bin', 'pip')
    
    try:
        # 更新pip
        subprocess.run([pip_path, 'install', '--upgrade', 'pip'], check=True)
        
        # 安装依赖
        requirements_file = 'requirements.txt'
        subprocess.run([pip_path, 'install', '-r', requirements_file], check=True)
        print("依赖安装成功!")
    except subprocess.CalledProcessError as e:
        print(f"安装依赖失败: {e}")
        print("请尝试手动安装依赖: pip install -r requirements.txt")

if __name__ == '__main__':
    setup_project() 