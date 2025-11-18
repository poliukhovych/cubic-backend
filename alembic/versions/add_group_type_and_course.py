"""Add type and course fields to groups table

Revision ID: add_group_type_and_course
Revises: add_student_group_id
Create Date: 2025-11-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_group_type_and_course'
down_revision = 'add_student_group_id'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM type for group type
    group_type_enum = postgresql.ENUM('bachelor', 'master', name='group_type_enum', create_type=True)
    group_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Add type column to groups table
    op.add_column('groups', 
        sa.Column('type', 
                  sa.Enum('bachelor', 'master', name='group_type_enum'),
                  nullable=False,
                  server_default='bachelor'
        )
    )
    
    # Add course column to groups table (1-6 for bachelor/master years)
    op.add_column('groups', 
        sa.Column('course', 
                  sa.Integer(),
                  nullable=False,
                  server_default='1'
        )
    )
    
    # Add check constraint for course (1-6)
    op.create_check_constraint(
        'ck_groups_course',
        'groups',
        'course >= 1 AND course <= 6'
    )


def downgrade() -> None:
    # Drop check constraint
    op.drop_constraint('ck_groups_course', 'groups', type_='check')
    
    # Drop course column
    op.drop_column('groups', 'course')
    
    # Drop type column
    op.drop_column('groups', 'type')
    
    # Drop ENUM type
    group_type_enum = postgresql.ENUM('bachelor', 'master', name='group_type_enum')
    group_type_enum.drop(op.get_bind(), checkfirst=True)

