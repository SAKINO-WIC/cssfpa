# 脚本工具集

本目录包含系统维护和数据管理相关的脚本工具。这些脚本可用于数据库初始化、数据修复、调试等任务。

## 脚本列表

### 数据库初始化
- `init_db.py` - 初始化数据库，创建表结构和初始数据
  ```bash
  python scripts/init_db.py
  ```

### 数据库检查与修复
- `check_db.py` - 检查数据库一致性
  ```bash
  python scripts/check_db.py
  ```
- `check_and_update_columns.py` - 检查并更新数据库表的列定义
  ```bash
  python scripts/check_and_update_columns.py
  ```
- `check_dates.py` - 检查数据库中日期数据的格式
  ```bash
  python scripts/check_dates.py
  ```
- `fix_dates.py` - 修复数据库中日期格式错误
  ```bash
  python scripts/fix_dates.py
  ```

### 用户管理
- `list_users.py` - 列出系统中的所有用户
  ```bash
  python scripts/list_users.py
  ```
- `debug_users.py` - 调试用户相关问题
  ```bash
  python scripts/debug_users.py
  ```

### 数据更新
- `update_english_scores.py` - 更新英语成绩数据（旧版本）
  ```bash
  python scripts/update_english_scores.py
  ```
- `update_english_scores_v2.py` - 更新英语成绩数据（新版本）
  ```bash
  python scripts/update_english_scores_v2.py
  ```

## 使用注意事项

1. 在运行修改数据的脚本前，建议先备份数据库
   ```bash
   cp app.db app.db.bak
   ```

2. 脚本执行后检查日志信息，确认操作是否成功
   
3. 对于生产环境，建议在测试环境中先测试脚本功能

4. 部分脚本可能需要管理员权限才能执行

5. 如果脚本执行过程中出现错误，请查看错误信息并根据情况修复 