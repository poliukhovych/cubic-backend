"""Add is_active field to schedules table

Revision ID: add_schedule_is_active
Revises: replace_confirmed_with_status
Create Date: 2025-01-27

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_schedule_is_active'
down_revision = 'replace_confirmed_with_status'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_active column to schedules table
    op.add_column('schedules', 
        sa.Column('is_active', 
                  sa.Boolean(),
                  nullable=False,
                  server_default='false'
        )
    )


def downgrade() -> None:
    # Remove is_active column
    op.drop_column('schedules', 'is_active')

