"""Replace confirmed boolean with status enum for students and teachers

Revision ID: replace_confirmed_with_status
Revises: add_student_group_id
Create Date: 2025-11-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'replace_confirmed_with_status'
down_revision = 'add_student_group_id'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types for student and teacher status
    student_status_enum = postgresql.ENUM('pending', 'active', 'inactive', name='student_status_enum', create_type=True)
    teacher_status_enum = postgresql.ENUM('pending', 'active', 'inactive', name='teacher_status_enum', create_type=True)
    
    student_status_enum.create(op.get_bind())
    teacher_status_enum.create(op.get_bind())
    
    # Add status column to students table with default 'pending'
    op.add_column('students', 
        sa.Column('status', 
                  student_status_enum,
                  nullable=False,
                  server_default='pending'
        )
    )
    
    # Add status column to teachers table with default 'pending'
    op.add_column('teachers', 
        sa.Column('status', 
                  teacher_status_enum,
                  nullable=False,
                  server_default='pending'
        )
    )
    
    # Migrate data: confirmed = TRUE → status = 'active', confirmed = FALSE → status = 'pending'
    op.execute("UPDATE students SET status = 'active' WHERE confirmed = TRUE")
    op.execute("UPDATE students SET status = 'pending' WHERE confirmed = FALSE")
    
    op.execute("UPDATE teachers SET status = 'active' WHERE confirmed = TRUE")
    op.execute("UPDATE teachers SET status = 'pending' WHERE confirmed = FALSE")
    
    # Drop the old confirmed column from students
    op.drop_column('students', 'confirmed')
    
    # Drop the old confirmed column from teachers
    op.drop_column('teachers', 'confirmed')


def downgrade() -> None:
    # Add back confirmed boolean columns
    op.add_column('students',
        sa.Column('confirmed', sa.Boolean(), nullable=False, server_default='false')
    )
    
    op.add_column('teachers',
        sa.Column('confirmed', sa.Boolean(), nullable=False, server_default='false')
    )
    
    # Migrate data back: status = 'active' → confirmed = TRUE, otherwise → confirmed = FALSE
    op.execute("UPDATE students SET confirmed = TRUE WHERE status = 'active'")
    op.execute("UPDATE students SET confirmed = FALSE WHERE status != 'active'")
    
    op.execute("UPDATE teachers SET confirmed = TRUE WHERE status = 'active'")
    op.execute("UPDATE teachers SET confirmed = FALSE WHERE status != 'active'")
    
    # Drop status columns
    op.drop_column('students', 'status')
    op.drop_column('teachers', 'status')
    
    # Drop enum types
    sa.Enum(name='student_status_enum').drop(op.get_bind())
    sa.Enum(name='teacher_status_enum').drop(op.get_bind())

