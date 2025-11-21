"""Add group_id to registration_requests table

Revision ID: add_registration_group_id
Revises: add_course_code
Create Date: 2025-11-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_registration_group_id'
down_revision = 'add_course_code'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add group_id column to registration_requests table
    op.add_column('registration_requests', 
        sa.Column('group_id', 
                  postgresql.UUID(as_uuid=True),
                  nullable=True
        )
    )
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_registration_requests_group_id',
        'registration_requests', 'groups',
        ['group_id'], ['group_id'],
        onupdate='CASCADE',
        ondelete='SET NULL'
    )
    
    # Add index for better query performance
    op.create_index(
        'ix_registration_requests_group_id',
        'registration_requests',
        ['group_id']
    )


def downgrade() -> None:
    # Drop index
    op.drop_index('ix_registration_requests_group_id', table_name='registration_requests')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_registration_requests_group_id', 'registration_requests', type_='foreignkey')
    
    # Drop column
    op.drop_column('registration_requests', 'group_id')

