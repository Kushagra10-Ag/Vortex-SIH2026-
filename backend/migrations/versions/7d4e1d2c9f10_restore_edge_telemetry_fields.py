"""Restore fields required by edge telemetry payloads.

Revision ID: 7d4e1d2c9f10
Revises: 13083c76a3b5
"""

from alembic import op
import sqlalchemy as sa


revision = "7d4e1d2c9f10"
down_revision = "13083c76a3b5"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("sensor_readings") as batch_op:
        batch_op.add_column(sa.Column("sensor_id", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("is_anomaly", sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column("threshold_min", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("threshold_max", sa.Float(), nullable=True))
        batch_op.create_index("ix_sensor_readings_sensor_id", ["sensor_id"], unique=False)

    op.execute("UPDATE sensor_readings SET sensor_id = 'legacy-' || id WHERE sensor_id IS NULL")

    with op.batch_alter_table("sensor_readings") as batch_op:
        batch_op.alter_column("sensor_id", existing_type=sa.String(length=100), nullable=False)

    with op.batch_alter_table("footfalls") as batch_op:
        batch_op.add_column(sa.Column("current_occupancy", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("dwell_time_avg", sa.Float(), nullable=True))


def downgrade():
    with op.batch_alter_table("footfalls") as batch_op:
        batch_op.drop_column("dwell_time_avg")
        batch_op.drop_column("current_occupancy")

    with op.batch_alter_table("sensor_readings") as batch_op:
        batch_op.drop_index("ix_sensor_readings_sensor_id")
        batch_op.drop_column("threshold_max")
        batch_op.drop_column("threshold_min")
        batch_op.drop_column("is_anomaly")
        batch_op.drop_column("sensor_id")