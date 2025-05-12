"""create_files_table_manually

Revision ID: 0c1d2e3f4g5h
Revises: rename_comprehensive_score
Create Date: 2025-04-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0c1d2e3f4g5h'
down_revision = '0b2a5f1d7c23'  # 确保这是最新的迁移版本的ID
branch_labels = None
depends_on = None

def upgrade():
    # 创建新的files表
    op.create_table('files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('upload_date', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('file_path', sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    # 删除新创建的files表
    op.drop_table('files') 