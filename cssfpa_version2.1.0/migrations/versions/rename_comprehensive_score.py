"""Rename comprehensive_score to comprehensive_test_score

Revision ID: 0b2a5f1d7c23
Revises: a4de38a992c5
Create Date: 2025-04-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b2a5f1d7c23'
down_revision = 'a4de38a992c5'
branch_labels = None
depends_on = None


def upgrade():
    # 创建新列
    op.add_column('students', sa.Column('comprehensive_test_score', sa.Integer(), nullable=True))
    
    # 复制数据
    op.execute('UPDATE students SET comprehensive_test_score = comprehensive_score')
    
    # 如果不希望数据重复，可以将comprehensive_score清空
    # op.execute('UPDATE students SET comprehensive_score = NULL')


def downgrade():
    # 删除新列，但先确保将数据复制回原列
    op.execute('UPDATE students SET comprehensive_score = comprehensive_test_score')
    
    # 删除新列
    op.drop_column('students', 'comprehensive_test_score') 