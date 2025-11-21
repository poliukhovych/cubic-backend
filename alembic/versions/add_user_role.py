"""Add role field to users table

Revision ID: add_user_role
Revises: 
Create Date: 2025-10-16

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_user_role'
down_revision = None  # Change this to your last migration ID
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM type for user roles
    user_role_enum = postgresql.ENUM('student', 'teacher', 'admin', name='user_role_enum', create_type=True)
    user_role_enum.create(op.get_bind(), checkfirst=True)
    
    # Add role column to users table
    op.add_column('users', 
        sa.Column('role', 
                  sa.Enum('student', 'teacher', 'admin', name='user_role_enum'),
                  nullable=False,
                  server_default='student'
        )
    )


def downgrade() -> None:
    # Remove role column
    op.drop_column('users', 'role')
    
    # Drop ENUM type
    user_role_enum = postgresql.ENUM('student', 'teacher', 'admin', name='user_role_enum')
    user_role_enum.drop(op.get_bind(), checkfirst=True)
