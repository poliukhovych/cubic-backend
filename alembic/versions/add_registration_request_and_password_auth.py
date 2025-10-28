"""
Add registration request and password auth

Revision ID: add_registration_request_and_password_auth
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from app.db.models.people.registration_request import RegistrationStatus
from app.db.models.people.user import UserRole


revision: str = 'add_registration_request_and_password_auth'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make google_sub nullable in users table and add hashed_password column
    op.alter_column('users', 'google_sub',
        existing_type=sa.String(length=255),
        nullable=True
    )
    op.add_column('users', 
        sa.Column('hashed_password', sa.String(length=255), nullable=True)
    )
    
    # Create RegistrationStatus enum type
    registration_status_enum = postgresql.ENUM(
        'pending', 'approved', 'rejected',
        name='registration_status_enum',
        create_type=True
    )
    registration_status_enum.create(op.get_bind())
    
    # Create registration_requests table
    op.create_table('registration_requests',
        sa.Column('request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('google_sub', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('patronymic', sa.String(length=100), nullable=True),
        sa.Column('requested_role', postgresql.ENUM(UserRole, name='user_role_enum'), nullable=False),
        sa.Column('status', postgresql.ENUM(name='registration_status_enum'), nullable=False),
        sa.Column('processed_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['processed_by_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('request_id')
    )


def downgrade() -> None:
    # Drop registration_requests table
    op.drop_table('registration_requests')
    
    # Drop RegistrationStatus enum type
    op.execute('DROP TYPE registration_status_enum')
    
    # Remove hashed_password column and make google_sub non-nullable again
    op.drop_column('users', 'hashed_password')
    op.alter_column('users', 'google_sub',
        existing_type=sa.String(length=255),
        nullable=False
    )