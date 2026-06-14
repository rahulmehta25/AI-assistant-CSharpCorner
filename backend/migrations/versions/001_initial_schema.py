"""Initial database schema

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable required extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('username', sa.String(100), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255)),
        sa.Column('full_name', sa.String(255)),
        sa.Column('avatar_url', sa.Text),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('auth_provider', sa.String(50), default='local'),
        sa.Column('auth_provider_id', sa.String(255)),
        sa.Column('last_login_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])

    # Create career_profiles table
    op.create_table(
        'career_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('current_role', sa.String(255)),
        sa.Column('target_role', sa.String(255)),
        sa.Column('experience_years', sa.Integer, default=0),
        sa.Column('education_level', sa.String(100)),
        sa.Column('location', sa.String(255)),
        sa.Column('remote_preference', sa.String(50), default='hybrid'),
        sa.Column('salary_expectation_min', sa.Integer),
        sa.Column('salary_expectation_max', sa.Integer),
        sa.Column('bio', sa.Text),
        sa.Column('linkedin_url', sa.Text),
        sa.Column('github_url', sa.Text),
        sa.Column('portfolio_url', sa.Text),
        sa.Column('resume_url', sa.Text),
        sa.Column('skills', postgresql.JSONB, default=[]),
        sa.Column('interests', postgresql.JSONB, default=[]),
        sa.Column('career_goals', postgresql.JSONB, default=[]),
        sa.Column('work_preferences', postgresql.JSONB, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_career_profiles_user', 'career_profiles', ['user_id'])

    # Create roadmaps table
    op.create_table(
        'roadmaps',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('target_role', sa.String(255)),
        sa.Column('target_timeline', sa.String(50)),
        sa.Column('status', sa.String(50), default='active'),
        sa.Column('progress_percentage', sa.Integer, default=0),
        sa.Column('current_phase', sa.Integer, default=1),
        sa.Column('total_phases', sa.Integer, default=1),
        sa.Column('learning_path', postgresql.JSONB, default=[]),
        sa.Column('milestones', postgresql.JSONB, default=[]),
        sa.Column('gap_analysis', postgresql.JSONB, default={}),
        sa.Column('ai_recommendations', postgresql.JSONB, default=[]),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('target_completion_date', sa.Date),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_roadmaps_user', 'roadmaps', ['user_id'])
    op.create_index('idx_roadmaps_status', 'roadmaps', ['status'])

    # Create roadmap_milestones table
    op.create_table(
        'roadmap_milestones',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('roadmap_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('roadmaps.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('phase', sa.Integer, nullable=False),
        sa.Column('order_index', sa.Integer, nullable=False),
        sa.Column('milestone_type', sa.String(50)),
        sa.Column('target_date', sa.Date),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('skills_required', postgresql.JSONB, default=[]),
        sa.Column('resources', postgresql.JSONB, default=[]),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_roadmap_milestones_roadmap', 'roadmap_milestones', ['roadmap_id'])

    # Create saved_jobs table
    op.create_table(
        'saved_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('external_job_id', sa.String(255)),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('company', sa.String(255), nullable=False),
        sa.Column('location', sa.String(255)),
        sa.Column('job_url', sa.Text),
        sa.Column('salary_min', sa.Integer),
        sa.Column('salary_max', sa.Integer),
        sa.Column('job_type', sa.String(50)),
        sa.Column('experience_level', sa.String(50)),
        sa.Column('description', sa.Text),
        sa.Column('requirements', postgresql.JSONB, default=[]),
        sa.Column('skills_required', postgresql.JSONB, default=[]),
        sa.Column('match_score', sa.Numeric(5, 2)),
        sa.Column('match_details', postgresql.JSONB, default={}),
        sa.Column('source', sa.String(100)),
        sa.Column('is_remote', sa.Boolean, default=False),
        sa.Column('posted_at', sa.DateTime(timezone=True)),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('notes', sa.Text),
        sa.Column('tags', postgresql.JSONB, default=[]),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_saved_jobs_user', 'saved_jobs', ['user_id'])

    # Create applications table
    op.create_table(
        'applications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('saved_job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('saved_jobs.id', ondelete='SET NULL')),
        sa.Column('job_title', sa.String(255), nullable=False),
        sa.Column('company', sa.String(255), nullable=False),
        sa.Column('job_url', sa.Text),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('applied_at', sa.DateTime(timezone=True)),
        sa.Column('response_at', sa.DateTime(timezone=True)),
        sa.Column('interview_date', sa.DateTime(timezone=True)),
        sa.Column('offer_amount', sa.Integer),
        sa.Column('resume_version', sa.Text),
        sa.Column('cover_letter', sa.Text),
        sa.Column('custom_responses', postgresql.JSONB, default={}),
        sa.Column('interview_notes', sa.Text),
        sa.Column('feedback', sa.Text),
        sa.Column('rejection_reason', sa.Text),
        sa.Column('follow_up_dates', postgresql.JSONB, default=[]),
        sa.Column('contacts', postgresql.JSONB, default=[]),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_applications_user', 'applications', ['user_id'])
    op.create_index('idx_applications_status', 'applications', ['status'])

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255)),
        sa.Column('conversation_type', sa.String(50), default='general'),
        sa.Column('context', postgresql.JSONB, default={}),
        sa.Column('summary', sa.Text),
        sa.Column('is_archived', sa.Boolean, default=False),
        sa.Column('message_count', sa.Integer, default=0),
        sa.Column('last_message_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_conversations_user', 'conversations', ['user_id'])
    op.create_index('idx_conversations_type', 'conversations', ['conversation_type'])

    # Create conversation_messages table
    op.create_table(
        'conversation_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('tokens_used', sa.Integer),
        sa.Column('model_used', sa.String(100)),
        sa.Column('metadata', postgresql.JSONB, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_conversation_messages_conversation', 'conversation_messages', ['conversation_id'])

    # Create skill_assessments table
    op.create_table(
        'skill_assessments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assessment_type', sa.String(50), nullable=False),
        sa.Column('skill_category', sa.String(100)),
        sa.Column('target_role', sa.String(255)),
        sa.Column('overall_score', sa.Numeric(5, 2)),
        sa.Column('skill_scores', postgresql.JSONB, default={}),
        sa.Column('strengths', postgresql.JSONB, default=[]),
        sa.Column('weaknesses', postgresql.JSONB, default=[]),
        sa.Column('recommendations', postgresql.JSONB, default=[]),
        sa.Column('gap_analysis', postgresql.JSONB, default={}),
        sa.Column('ai_feedback', sa.Text),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_skill_assessments_user', 'skill_assessments', ['user_id'])
    op.create_index('idx_skill_assessments_type', 'skill_assessments', ['assessment_type'])

    # Create skill_assessment_questions table
    op.create_table(
        'skill_assessment_questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('skill_assessments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_text', sa.Text, nullable=False),
        sa.Column('question_type', sa.String(50)),
        sa.Column('skill_tested', sa.String(100)),
        sa.Column('difficulty_level', sa.String(20)),
        sa.Column('options', postgresql.JSONB, default=[]),
        sa.Column('correct_answer', sa.Text),
        sa.Column('user_answer', sa.Text),
        sa.Column('is_correct', sa.Boolean),
        sa.Column('points_earned', sa.Numeric(5, 2), default=0),
        sa.Column('time_taken_seconds', sa.Integer),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_assessment_questions_assessment', 'skill_assessment_questions', ['assessment_id'])

    # Create achievements table
    op.create_table(
        'achievements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('category', sa.String(50)),
        sa.Column('icon_url', sa.Text),
        sa.Column('points', sa.Integer, default=0),
        sa.Column('rarity', sa.String(20), default='common'),
        sa.Column('criteria', postgresql.JSONB, default={}),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create user_achievements table
    op.create_table(
        'user_achievements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('achievement_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('achievements.id', ondelete='CASCADE'), nullable=False),
        sa.Column('progress', sa.Numeric(5, 2), default=0),
        sa.Column('unlocked_at', sa.DateTime(timezone=True)),
        sa.Column('metadata', postgresql.JSONB, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),
    )
    op.create_index('idx_user_achievements_user', 'user_achievements', ['user_id'])

    # Create careers table
    op.create_table(
        'careers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('soc_code', sa.String(20), unique=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('category', sa.String(100)),
        sa.Column('cluster', sa.String(100)),
        sa.Column('median_salary', sa.Integer),
        sa.Column('salary_range_min', sa.Integer),
        sa.Column('salary_range_max', sa.Integer),
        sa.Column('growth_rate', sa.String(50)),
        sa.Column('employment_outlook', sa.String(100)),
        sa.Column('education_level', sa.String(100)),
        sa.Column('experience_level', sa.String(100)),
        sa.Column('skills', postgresql.JSONB, default=[]),
        sa.Column('tasks', postgresql.JSONB, default=[]),
        sa.Column('knowledge', postgresql.JSONB, default=[]),
        sa.Column('abilities', postgresql.JSONB, default=[]),
        sa.Column('interests', postgresql.JSONB, default=[]),
        sa.Column('work_styles', postgresql.JSONB, default=[]),
        sa.Column('work_environment', postgresql.JSONB, default=[]),
        sa.Column('related_occupations', postgresql.JSONB, default=[]),
        sa.Column('certifications', postgresql.JSONB, default=[]),
        sa.Column('tools_technology', postgresql.JSONB, default=[]),
        sa.Column('is_remote_friendly', sa.Boolean, default=False),
        sa.Column('automation_risk', sa.String(20)),
        sa.Column('bright_outlook', sa.Boolean, default=False),
        sa.Column('green_economy', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_careers_soc_code', 'careers', ['soc_code'])
    op.create_index('idx_careers_category', 'careers', ['category'])

    # Create skills_taxonomy table
    op.create_table(
        'skills_taxonomy',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(100)),
        sa.Column('subcategory', sa.String(100)),
        sa.Column('description', sa.Text),
        sa.Column('related_skills', postgresql.JSONB, default=[]),
        sa.Column('demand_level', sa.String(20)),
        sa.Column('learning_resources', postgresql.JSONB, default=[]),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_skills_taxonomy_name', 'skills_taxonomy', ['name'])
    op.create_index('idx_skills_taxonomy_category', 'skills_taxonomy', ['category'])

    # Create job_queue table
    op.create_table(
        'job_queue',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('job_type', sa.String(100), nullable=False),
        sa.Column('payload', postgresql.JSONB, nullable=False),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('priority', sa.Integer, default=5),
        sa.Column('attempts', sa.Integer, default=0),
        sa.Column('max_attempts', sa.Integer, default=3),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('failed_at', sa.DateTime(timezone=True)),
        sa.Column('error_message', sa.Text),
        sa.Column('result', postgresql.JSONB),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_job_queue_status', 'job_queue', ['status'])
    op.create_index('idx_job_queue_type', 'job_queue', ['job_type'])
    op.create_index('idx_job_queue_user', 'job_queue', ['user_id'])

    # Create ai_response_cache table
    op.create_table(
        'ai_response_cache',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('cache_key', sa.String(255), unique=True, nullable=False),
        sa.Column('cache_type', sa.String(50), nullable=False),
        sa.Column('request_hash', sa.String(64), nullable=False),
        sa.Column('response_data', postgresql.JSONB, nullable=False),
        sa.Column('model_used', sa.String(100)),
        sa.Column('tokens_used', sa.Integer),
        sa.Column('hit_count', sa.Integer, default=0),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_ai_cache_key', 'ai_response_cache', ['cache_key'])
    op.create_index('idx_ai_cache_type', 'ai_response_cache', ['cache_type'])

    # Create audit_log table
    op.create_table(
        'audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(100)),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True)),
        sa.Column('old_values', postgresql.JSONB),
        sa.Column('new_values', postgresql.JSONB),
        sa.Column('ip_address', postgresql.INET),
        sa.Column('user_agent', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_audit_log_user', 'audit_log', ['user_id'])
    op.create_index('idx_audit_log_action', 'audit_log', ['action'])
    op.create_index('idx_audit_log_created', 'audit_log', ['created_at'])


def downgrade() -> None:
    op.drop_table('audit_log')
    op.drop_table('ai_response_cache')
    op.drop_table('job_queue')
    op.drop_table('skills_taxonomy')
    op.drop_table('careers')
    op.drop_table('user_achievements')
    op.drop_table('achievements')
    op.drop_table('skill_assessment_questions')
    op.drop_table('skill_assessments')
    op.drop_table('conversation_messages')
    op.drop_table('conversations')
    op.drop_table('applications')
    op.drop_table('saved_jobs')
    op.drop_table('roadmap_milestones')
    op.drop_table('roadmaps')
    op.drop_table('career_profiles')
    op.drop_table('users')
