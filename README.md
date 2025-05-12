入党积极分子综合评分系统 (v2.1.0)
项目简介
本系统是一个基于Python Flask的Web应用，用于管理和评估入党积极分子的综合表现。系统支持学生信息管理、文件上传、教师评分、权限管理等功能，旨在数字化和规范化入党积极分子的考核评价流程。

该系统通过多维度评分机制，全面记录和评估入党积极分子在政治思想、学习表现、社会实践等方面的综合素质，为党组织发展新党员提供客观、科学的数据支持和决策参考。

系统角色与权限
学生
功能权限：
个人信息管理：填写、更新和查看个人基本信息
文件管理：上传思想汇报、学习心得等文档材料
成绩查询：查看各项评分和总体评价结果
消息通知：接收来自教师和系统的通知信息
教师
功能权限：
学生管理：查看和编辑所负责班级/组织的学生信息
评分管理：根据评分标准对学生进行多维度评分
文件审核：审核学生上传的各类文件
统计分析：查看评分数据统计和分析报告
消息发送：向学生发送通知和反馈信息
管理员
功能权限：
用户管理：创建、修改和删除系统用户账户
系统配置：设置评分规则、学期信息、组织结构等
数据管理：备份、恢复和维护系统数据
权限控制：分配和调整用户的系统权限
系统监控：查看系统日志和运行状态
功能详细说明
学生信息管理
基本信息维护：姓名、学号、性别、联系方式等个人基础信息
政治信息记录：政治面貌、申请入党时间、培训经历等
学习成绩记录：课程成绩、获奖情况、学术表现等
实践活动记录：社会实践、志愿服务、组织活动参与情况
文件上传与管理
多格式支持：支持PDF、Word文档、图片等多种格式
分类存储：按文件类型和用途进行分类整理
版本控制：支持文件更新和历史记录查看
审核流程：教师对上传文件进行在线审核和反馈
评分系统
多维度评价：包含思想政治、学习表现、实践能力等多个维度
动态权重：可根据不同阶段和要求调整各维度的评分权重
评分记录：详细记录每次评分过程和结果
综合分析：自动计算总评分并生成综合评价报告
权限管理
基于角色的访问控制：根据用户角色分配相应的系统权限
操作审计：记录重要操作的执行者和时间
数据隔离：确保用户只能访问授权范围内的数据
密码安全：强制密码复杂度要求和定期更换机制
数据分析与报表
学生进度跟踪：可视化展示学生各阶段的发展情况
统计分析：生成班级/组织层面的统计数据和图表
评分对比：支持不同时间段、不同班级的评分对比
报表导出：支持将分析结果导出为Excel、PDF等格式
技术栈详情
后端框架：Python Flask 3.0.0
ORM框架：SQLAlchemy 2.0.23
数据库：SQLite（可扩展支持MySQL、PostgreSQL）
用户认证：Flask-Login 0.6.3
表单处理：Flask-WTF 1.2.1, WTForms 3.1.1
前端框架：HTML5, CSS3, JavaScript
UI组件库：Bootstrap 5
国际化支持：Flask-Babel 3.1.0
数据可视化：Chart.js
数据处理：pandas 2.1.1, openpyxl 3.1.2
邮件通知：Flask-Mail 0.9.1
数据迁移：Flask-Migrate 4.0.5, Alembic 1.12.1
安装说明
系统要求
Python 3.10或更高版本
操作系统：Windows/Linux/MacOS
建议内存：至少4GB RAM
磁盘空间：至少500MB可用空间
方法一：使用自动安装脚本（推荐）
python setup.py
此脚本将自动创建虚拟环境、安装依赖、初始化必要的目录结构，并引导您完成必要的初始配置。

方法二：手动安装
创建虚拟环境：
python -m venv venv
激活虚拟环境：
Windows:
.\venv\Scripts\activate
Linux/Mac:
source venv/bin/activate
安装依赖：
pip install -r requirements.txt
设置环境变量（可选）：
创建.env文件，添加如下内容：
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///D:/CURSORHOME/cssfpa/cssfpa_version2.1.0/app.db
初始化数据库：
python scripts/init_db.py
创建上传目录：
mkdir -p app/uploads
运行应用：
python run.py
配置选项
系统配置主要在config.py文件中定义，包括以下主要选项：

SECRET_KEY：应用密钥，用于会话安全
SQLALCHEMY_DATABASE_URI：数据库连接URI，默认为sqlite:///D:/CURSORHOME/cssfpa/cssfpa_version2.1.0/app.db
UPLOAD_FOLDER：文件上传存储路径
MAX_CONTENT_LENGTH：上传文件大小限制（默认16MB）
ALLOWED_EXTENSIONS：允许的文件扩展名
PERMANENT_SESSION_LIFETIME：会话持续时间（默认30分钟）
ITEMS_PER_PAGE：分页每页显示条目数
LANGUAGES：支持的语言列表
目录结构详解
.
├── app/                   # 应用主目录
│   ├── static/            # 静态文件（JS, CSS, 图片等）
│   ├── templates/         # HTML模板
│   ├── models/            # 数据模型
│   ├── controllers/       # 控制器（路由和视图函数）
│   ├── forms/             # 表单定义
│   ├── services/          # 业务逻辑服务
│   ├── utils/             # 工具函数
│   ├── uploads/           # 文件上传目录
│   ├── translations/      # 国际化翻译文件
│   ├── auth/              # 认证相关功能
│   ├── student/           # 学生功能模块
│   ├── routes/            # 路由定义
│   ├── views/             # 视图函数
│   └── __init__.py        # 应用初始化
├── scripts/               # 脚本工具
│   ├── init_db.py         # 数据库初始化脚本
│   ├── update_english_scores.py  # 英语成绩更新脚本
│   ├── update_english_scores_v2.py  # 英语成绩更新脚本v2
│   ├── check_and_update_columns.py  # 列检查与更新脚本
│   ├── fix_dates.py       # 日期修复脚本
│   ├── debug_users.py     # 用户调试脚本
│   ├── list_users.py      # 用户列表脚本
│   ├── check_dates.py     # 日期检查脚本
│   └── check_db.py        # 数据库检查脚本
├── logs/                  # 日志文件
├── data/                  # 数据文件
├── migrations/            # 数据库迁移文件
├── instance/              # Flask实例文件夹
├── venv/                  # Python虚拟环境
├── __pycache__/           # Python缓存文件
├── .env                   # 环境变量配置
├── config.py              # 应用配置
├── requirements.txt       # 项目依赖
├── run.py                 # 应用启动入口
├── check_app.py           # 应用检查工具
├── check_db.py            # 数据库检查工具
├── babel.cfg              # Babel配置文件
├── CHANGELOG.md           # 版本更新日志
├── setup.py               # 安装脚本
├── app.db                 # SQLite数据库文件
├── .gitignore             # Git忽略文件配置
└── README.md              # 项目说明
使用说明
初次登录与账户设置
管理员账户初始设置：用户名 admin，密码 admin666
首次登录后请立即在"个人资料"页面修改默认密码
管理员需要先创建教师账户，然后由教师创建学生账户或批量导入学生信息
常用功能流程
管理员：

系统初始化：设置评分规则、学期信息
用户管理：创建教师账户和组织结构
系统维护：定期数据备份和权限检查
教师：

学生管理：导入或手动添加学生信息
文件审核：查看和批阅学生上传的文件
学生评分：按照设定的标准进行评分
数据分析：生成评分统计和分析报告
学生：

个人信息：完善个人基本信息
材料上传：按要求上传思想汇报等文件
成绩查询：查看评分结果和反馈
消息通知：查阅系统和教师发送的通知
数据导出与备份
系统支持将评分数据导出为Excel表格
管理员可以使用系统提供的备份功能保存数据
建议每学期定期备份数据到data/backups/目录
开发者指南
开发环境设置
克隆项目到本地后，按照安装说明设置开发环境
推荐使用Visual Studio Code或PyCharm进行开发
安装pylint、flake8等工具进行代码质量检查
代码规范
遵循PEP 8 Python编码规范
使用类型注解增强代码可读性
编写单元测试确保功能正确性
遵循项目现有的架构和设计模式
功能扩展指南
添加新功能请在对应的控制器和模型中进行开发
新增页面应放在相应的模板目录下
添加新的数据模型后需要进行数据库迁移：
flask db migrate -m "添加新功能的描述"
flask db upgrade
前端修改请遵循现有的样式和结构，优先使用Bootstrap组件
国际化开发
在代码中使用_('文本')标记需要翻译的字符串
提取待翻译的字符串：
pybabel extract -F babel.cfg -o messages.pot .
更新翻译文件：
pybabel update -i messages.pot -d app/translations
编辑app/translations/en/LC_MESSAGES/messages.po添加翻译
编译翻译文件：
pybabel compile -d app/translations
常见问题与解决方案
数据库问题
问题：数据库迁移失败 解决：删除migrations文件夹，重新初始化：

flask db init
flask db migrate
flask db upgrade
问题：数据库锁定 解决：使用scripts/fix_db_lock.py脚本解锁数据库

问题：数据库路径错误 解决：检查.env文件和config.py中的数据库路径是否正确指向D:/CURSORHOME/cssfpa/cssfpa_version2.1.0/app.db

文件上传问题
问题：无法上传文件 解决：检查app/uploads目录权限，确保web服务器有写入权限

问题：上传文件大小限制 解决：修改config.py中的MAX_CONTENT_LENGTH参数，默认为16MB

用户权限问题
问题：用户无法访问某些功能 解决：检查用户角色设置，确保权限分配正确

问题：管理员密码遗失 解决：使用scripts/reset_admin.py脚本重置管理员密码

系统更新与升级
查看CHANGELOG.md了解各版本更新内容
升级前备份数据库和重要文件
按照更新文档进行升级操作
升级后检查系统功能和数据完整性
从v2.0.0升级到v2.1.0
备份原有数据库：cp app.db app.db.backup
更新代码库到v2.1.0版本
更新.env文件中的数据库路径为新路径
运行数据库迁移：flask db upgrade
重启应用：python run.py
技术支持与贡献
如发现Bug或有功能建议，请提交Issue
欢迎通过Pull Request贡献代码
技术支持联系方式：[添加联系方式]
许可证
本项目为内部使用软件，未开放商业许可，仅限组织内部使用。未经授权不得外传或用于商业目的。
