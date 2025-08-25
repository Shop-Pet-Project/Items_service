"""0002 - Create 'companies' table

Revision ID: 855bdde3d2b0
Revises: 400acf185c6f
Create Date: 2025-08-25 18:30:51.237163

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '855bdde3d2b0'
down_revision: Union[str, Sequence[str], None] = '400acf185c6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('companies',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_companies_id'), 'companies', ['id'], unique=False)
    op.add_column('items', sa.Column('company_id', sa.UUID(), nullable=False))
    op.create_foreign_key(None, 'items', 'companies', ['company_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, 'items', type_='foreignkey')
    op.drop_column('items', 'company_id')
    op.drop_index(op.f('ix_companies_id'), table_name='companies')
    op.drop_table('companies')
