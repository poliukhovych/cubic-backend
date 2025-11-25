"""Add attendance and homework_submission tables

Revision ID: add_attendance_and_homework_submission
Revises: add_schedule_is_active
Create Date: 2025-01-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_attendance_and_homework_submission'
down_revision = 'add_schedule_is_active'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create attendance_status_enum
    op.execute("""
        CREATE TYPE attendance_status_enum AS ENUM ('present', 'absent', 'late', 'excused')
    """)
    
    # Create attendance table
    op.create_table(
        'attendance',
        sa.Column('attendance_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('assignment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('status', sa.Enum('present', 'absent', 'late', 'excused', name='attendance_status_enum', create_type=True), nullable=False),
        sa.Column('note', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_foreign_key(
        'fk_attendance_assignment_id',
        'attendance', 'assignments',
        ['assignment_id'], ['assignment_id'],
        onupdate='CASCADE', ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_attendance_student_id',
        'attendance', 'students',
        ['student_id'], ['student_id'],
        onupdate='CASCADE', ondelete='CASCADE'
    )
    op.create_unique_constraint('uq_attendance_assignment_student_date', 'attendance', ['assignment_id', 'student_id', 'date'])
    op.create_index('ix_attendance_student', 'attendance', ['student_id', 'date'])
    op.create_index('ix_attendance_assignment', 'attendance', ['assignment_id', 'date'])
    
    # Create homework_submissions table
    op.create_table(
        'homework_submissions',
        sa.Column('submission_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('homework_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.String(5000), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('grade', sa.Numeric(5, 2), nullable=True),
        sa.Column('feedback', sa.String(1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_foreign_key(
        'fk_homework_submissions_homework_id',
        'homework_submissions', 'homework',
        ['homework_id'], ['homework_id'],
        onupdate='CASCADE', ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_homework_submissions_student_id',
        'homework_submissions', 'students',
        ['student_id'], ['student_id'],
        onupdate='CASCADE', ondelete='CASCADE'
    )
    op.create_unique_constraint('uq_homework_submission_student', 'homework_submissions', ['homework_id', 'student_id'])
    op.create_index('ix_homework_submission_student', 'homework_submissions', ['student_id', 'submitted_at'])
    op.create_index('ix_homework_submission_homework', 'homework_submissions', ['homework_id', 'submitted_at'])
    
    # Create homework_submission_files table
    op.create_table(
        'homework_submission_files',
        sa.Column('file_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('submission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_foreign_key(
        'fk_homework_submission_files_submission_id',
        'homework_submission_files', 'homework_submissions',
        ['submission_id'], ['submission_id'],
        onupdate='CASCADE', ondelete='CASCADE'
    )
    op.create_index('ix_homework_submission_files_submission', 'homework_submission_files', ['submission_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_homework_submission_files_submission', table_name='homework_submission_files')
    op.drop_index('ix_homework_submission_homework', table_name='homework_submissions')
    op.drop_index('ix_homework_submission_student', table_name='homework_submissions')
    op.drop_index('ix_attendance_assignment', table_name='attendance')
    op.drop_index('ix_attendance_student', table_name='attendance')
    
    # Drop tables in reverse order
    op.drop_table('homework_submission_files')
    op.drop_table('homework_submissions')
    op.drop_table('attendance')
    
    # Drop enum
    op.execute('DROP TYPE IF EXISTS attendance_status_enum')

