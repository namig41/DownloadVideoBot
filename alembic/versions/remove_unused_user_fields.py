"""remove_unused_user_fields

Revision ID: remove_unused_fields
Revises: f2ea99ea49a5
Create Date: 2025-12-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'remove_unused_fields'
down_revision: Union[str, None] = 'f2ea99ea49a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Удаляем неиспользуемые поля из таблицы users
    op.drop_column('users', 'is_premium')
    op.drop_column('users', 'is_bot')
    op.drop_column('users', 'daily_attempts')
    op.drop_column('users', 'last_attempt_date')
    op.drop_column('users', 'total_photos_processed')


def downgrade() -> None:
    """Downgrade schema."""
    # Восстанавливаем удаленные поля
    op.add_column('users', sa.Column('is_premium', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('is_bot', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('daily_attempts', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('last_attempt_date', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('total_photos_processed', sa.Integer(), nullable=True))

