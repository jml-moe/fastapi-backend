"""recommendation.version_id boleh kosong

Revision ID: c4e1a7d92b35
Revises: 93d99ca52759
Create Date: 2026-10-29 09:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c4e1a7d92b35"
down_revision: Union[str, Sequence[str], None] = "93d99ca52759"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Riwayat tetap ada setelah versi profilnya dihapus (version_id menjadi NULL)."""
    with op.batch_alter_table("recommendation") as batch:
        batch.alter_column("version_id", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    """Baris yang versinya sudah dihapus tidak bisa lagi memenuhi NOT NULL, jadi dibuang."""
    op.execute("DELETE FROM recommendation WHERE version_id IS NULL")
    with op.batch_alter_table("recommendation") as batch:
        batch.alter_column("version_id", existing_type=sa.Integer(), nullable=False)
