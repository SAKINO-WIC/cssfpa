"""添加无挂科记录字段

Revision ID: 4f8d95ad1234
Revises: 你的上一个版本号
Create Date: 2023-05-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f8d95ad1234'
down_revision = None  # 替换为你的上一个迁移版本
branch_labels = None
depends_on = None


def upgrade():
    # 添加无挂科记录字段
    op.add_column('students', sa.Column('no_failed_course', sa.Boolean(), nullable=True, server_default='1'))
    
    # 执行数据迁移：根据has_failed_course字段设置no_failed_course
    op.execute("""
    UPDATE students 
    SET no_failed_course = NOT has_failed_course
    WHERE has_failed_course IS NOT NULL;
    """)
    
    # 设置默认值
    op.execute("""
    UPDATE students 
    SET no_failed_course = 1
    WHERE no_failed_course IS NULL;
    """)


def downgrade():
    # 删除无挂科记录字段
    op.drop_column('students', 'no_failed_course') 