from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0001_phase1_foundation"; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
    op.create_table("projects",sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("name",sa.String(200),nullable=False),sa.Column("description",sa.Text()),sa.Column("status",sa.String(32),nullable=False),sa.Column("metadata",postgresql.JSONB(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False))
    op.create_table("tasks",sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("project_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("projects.id",ondelete="CASCADE"),nullable=False),sa.Column("title",sa.String(240),nullable=False),sa.Column("description",sa.Text()),sa.Column("status",sa.String(32),nullable=False),sa.Column("priority",sa.Integer(),nullable=False),sa.Column("metadata",postgresql.JSONB(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False))
    op.create_index("ix_tasks_project_id","tasks",["project_id"])
    op.create_table("events",sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("event_type",sa.String(100),nullable=False),sa.Column("project_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("projects.id",ondelete="SET NULL")),sa.Column("task_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("tasks.id",ondelete="SET NULL")),sa.Column("payload",postgresql.JSONB(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False))
    op.create_index("ix_events_event_type","events",["event_type"])
    op.create_table("approval_requests",sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("action",sa.String(240),nullable=False),sa.Column("target",sa.String(500),nullable=False),sa.Column("reason",sa.Text(),nullable=False),sa.Column("risk_level",sa.String(40),nullable=False),sa.Column("status",sa.String(32),nullable=False),sa.Column("proposed_changes",postgresql.JSONB(),nullable=False),sa.Column("estimated_cost",sa.Float()),sa.Column("preview",postgresql.JSONB(),nullable=False),sa.Column("metadata",postgresql.JSONB(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),sa.Column("resolved_at",sa.DateTime(timezone=True)))
    op.create_index("ix_approval_requests_status","approval_requests",["status"])
def downgrade():
    op.drop_index("ix_approval_requests_status",table_name="approval_requests"); op.drop_table("approval_requests")
    op.drop_index("ix_events_event_type",table_name="events"); op.drop_table("events")
    op.drop_index("ix_tasks_project_id",table_name="tasks"); op.drop_table("tasks"); op.drop_table("projects")
