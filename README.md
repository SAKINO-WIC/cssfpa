入党积极分子综合评分系统 (v2.1.0)
项目简介
本系统是一个基于Python Flask的Web应用，用于管理和评估入党积极分子的综合表现。系统支持学生信息管理、文件上传、教师评分、权限管理等功能，旨在数字化和规范化入党积极分子的考核评价流程。

该系统通过多维度评分机制，全面记录和评估入党积极分子在政治思想、学习表现、社会实践等方面的综合素质，为党组织发展新党员提供客观、科学的数据支持和决策参考。

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
技术支持与贡献
如发现Bug或有功能建议，请提交Issue
欢迎通过Pull Request贡献代码
技术支持联系方式：[添加联系方式]
许可证
本项目为内部使用软件，未开放商业许可，仅限组织内部使用。未经授权不得外传或用于商业目的。
