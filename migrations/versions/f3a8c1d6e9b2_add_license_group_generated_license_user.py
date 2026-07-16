"""add license_group, generated_license, user tables

Revision ID: f3a8c1d6e9b2
Revises: d74739dc082b
Create Date: 2026-07-16 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3a8c1d6e9b2'
down_revision: Union[str, Sequence[str], None] = 'd74739dc082b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('license_group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('single', 'lab', name='license_type'), nullable=False),
    sa.Column('org_name', sa.String(length=255), nullable=False),
    sa.Column('max_seats', sa.Integer(), server_default='1', nullable=False),
    sa.Column('bought_at', sa.Date(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("(type = 'single' AND max_seats = 1) OR (type = 'lab' AND max_seats >= 1)", name='chk_seat_cap'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('generated_license',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('license_group_id', sa.Integer(), nullable=False),
    sa.Column('license_key', sa.Text(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('validity_days', sa.Integer(), nullable=False),
    sa.Column('machine_fingerprint_hash', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('unused', 'activated', 'expired', name='license_key_status'), server_default='unused', nullable=False),
    sa.Column('activated_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('expired_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['license_group_id'], ['license_group.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('license_key')
    )
    op.create_index('uq_license_group_machine', 'generated_license', ['license_group_id', 'machine_fingerprint_hash'], unique=True, postgresql_where=sa.text('machine_fingerprint_hash IS NOT NULL'))
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('generated_license_id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.Text(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['generated_license_id'], ['generated_license.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('generated_license_id'),
    sa.UniqueConstraint('email')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('users')
    op.drop_index('uq_license_group_machine', table_name='generated_license', postgresql_where=sa.text('machine_fingerprint_hash IS NOT NULL'))
    op.drop_table('generated_license')
    sa.Enum(name='license_key_status').drop(op.get_bind(), checkfirst=True)
    op.drop_table('license_group')
    sa.Enum(name='license_type').drop(op.get_bind(), checkfirst=True)
