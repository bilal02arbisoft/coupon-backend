"""convert_coupon_expiry_to_datetime

Revision ID: d52d76b2d978
Revises: 0b37ba28a71c
Create Date: 2025-10-10 12:55:12.046270

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd52d76b2d978'
down_revision = '0b37ba28a71c'
branch_labels = None
depends_on = None


def upgrade():
    # SQLite can't alter types easily. Strategy:
    # 1) Add a temp column expiry_date_dt
    # 2) Best-effort parse old strings into datetime and store in new column
    # 3) Drop old column and rename new
    bind = op.get_bind()
    op.add_column('coupons', sa.Column('expiry_date_dt', sa.DateTime(), nullable=True))

    try:
        # Backfill using SQL; SQLite doesn't have robust datetime parsing.
        # We'll attempt to handle common formats that were used (YYYY-MM-DD and ISO strings).
        # Fetch rows and parse in Python.
        res = bind.execute(sa.text('SELECT id, expiry_date FROM coupons'))
        rows = res.fetchall()
        from datetime import datetime
        for row in rows:
            cid = row[0]
            val = row[1]
            parsed = None
            if val:
                for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S'):
                    try:
                        parsed = datetime.strptime(val, fmt)
                        break
                    except Exception:
                        continue
            if parsed:
                bind.execute(sa.text('UPDATE coupons SET expiry_date_dt = :dt WHERE id = :cid'),
                             {"dt": parsed, "cid": cid})
    except Exception:
        pass

    with op.batch_alter_table('coupons') as batch_op:
        batch_op.drop_column('expiry_date')
        batch_op.alter_column('expiry_date_dt', new_column_name='expiry_date')


def downgrade():
    bind = op.get_bind()
    op.add_column('coupons', sa.Column('expiry_date_txt', sa.VARCHAR(length=20), nullable=True))

    try:
        res = bind.execute(sa.text('SELECT id, expiry_date FROM coupons'))
        rows = res.fetchall()
        for row in rows:
            cid = row[0]
            dt = row[1]
            txt = None
            if dt:
                try:
                    txt = dt.strftime('%Y-%m-%d')
                except Exception:
                    txt = None
            bind.execute(sa.text('UPDATE coupons SET expiry_date_txt = :txt WHERE id = :cid'),
                         {"txt": txt, "cid": cid})
    except Exception:
        pass

    with op.batch_alter_table('coupons') as batch_op:
        batch_op.drop_column('expiry_date')
        batch_op.alter_column('expiry_date_txt', new_column_name='expiry_date')
