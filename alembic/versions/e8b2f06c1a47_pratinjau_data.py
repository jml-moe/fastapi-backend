"""pratinjau data pada versi profil

Revision ID: e8b2f06c1a47
Revises: c4e1a7d92b35
Create Date: 2026-10-29 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8b2f06c1a47'
down_revision: Union[str, Sequence[str], None] = 'c4e1a7d92b35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Versi lama tidak punya pratinjau (NULL) sampai datasetnya diunggah ulang."""
    with op.batch_alter_table('profileversion') as batch:
        batch.add_column(sa.Column('pratinjau', sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('profileversion') as batch:
        batch.drop_column('pratinjau')
