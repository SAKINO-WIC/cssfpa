"""创建 File 表

创建一个新的文件表，用于存储用户上传的文件
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# 修订ID
revision = 'create_file_table'
down_revision = None  # 如果这是第一个迁移，则为 None
branch_labels = None
depends_on = None

def upgrade():
    # 创建 files 表
    op.create_table(
        'files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('file_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True, default=0),
        sa.Column('upload_date', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('file_path', sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    # 创建索引
    op.create_index(op.f('ix_files_user_id'), 'files', ['user_id'], unique=False)

def downgrade():
    # 删除表
    op.drop_index(op.f('ix_files_user_id'), table_name='files')
    op.drop_table('files')