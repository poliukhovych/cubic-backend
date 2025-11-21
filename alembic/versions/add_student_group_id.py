"""Add group_id FK to students table

Revision ID: add_student_group_id
Revises: add_user_role
Create Date: 2025-11-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_student_group_id'
down_revision = 'add_user_role'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add group_id column to students table
    op.add_column('students', 
        sa.Column('group_id', 
                  postgresql.UUID(as_uuid=True),
                  nullable=True
        )
    )
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_students_group_id',
        'students', 'groups',
        ['group_id'], ['group_id'],
        onupdate='CASCADE',
        ondelete='SET NULL'
    )
    
    # Add index for better query performance
    op.create_index(
        'ix_students_group_id',
        'students',
        ['group_id']
    )


def downgrade() -> None:
    # Drop index
    op.drop_index('ix_students_group_id', table_name='students')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_students_group_id', 'students', type_='foreignkey')
    
    # Drop column
    op.drop_column('students', 'group_id')

