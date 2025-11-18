"""Add code field to courses table

Revision ID: add_course_code
Revises: add_group_type_and_course
Create Date: 2025-11-18

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_course_code'
down_revision = 'add_group_type_and_course'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add code column to courses table
    op.add_column('courses', 
        sa.Column('code', 
                  sa.String(50),
                  nullable=True,
                  unique=True
        )
    )
    
    # Add index for better query performance
    op.create_index(
        'ix_courses_code',
        'courses',
        ['code']
    )


def downgrade() -> None:
    # Drop index
    op.drop_index('ix_courses_code', table_name='courses')
    
    # Drop column
    op.drop_column('courses', 'code')

