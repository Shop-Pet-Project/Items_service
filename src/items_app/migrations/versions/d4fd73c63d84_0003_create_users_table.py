"""0003 - Create 'users' table

Revision ID: d4fd73c63d84
Revises: 855bdde3d2b0
Create Date: 2025-09-13 23:14:10.570455

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "d4fd73c63d84"
down_revision: Union[str, Sequence[str], None] = "855bdde3d2b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")

    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("username", sa.String(length=32), nullable=False),
        sa.Column("email", postgresql.CITEXT(), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.add_column("companies", sa.Column("user_id", sa.UUID(), nullable=False))
    op.create_unique_constraint(None, "companies", ["name"])
    op.create_foreign_key(None, "companies", "users", ["user_id"], ["id"])
    op.alter_column(
        "items",
        "price",
        existing_type=sa.DOUBLE_PRECISION(precision=53),
        type_=sa.Numeric(precision=10, scale=2),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "items",
        "price",
        existing_type=sa.Numeric(precision=10, scale=2),
        type_=sa.DOUBLE_PRECISION(precision=53),
        existing_nullable=False,
    )
    op.drop_constraint(None, "companies", type_="foreignkey")
    op.drop_constraint(None, "companies", type_="unique")
    op.drop_column("companies", "user_id")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
