import pathlib
import pandas as pd
from sqlalchemy import create_engine, text

BASE = pathlib.Path(__file__).resolve().parent.parent
CLEAN = BASE / "data" / "cleaned" / "orders_cleaned.csv"
DBDIR = BASE / "data"
DBDIR.mkdir(parents=True, exist_ok=True)
DBPATH = DBDIR / "warehouse.db"

print("Reading:", CLEAN)
df = pd.read_csv(CLEAN)

engine = create_engine(f"sqlite:///{DBPATH}")
print("Writing table: orders")
with engine.begin() as conn:
    df.to_sql("orders", conn, if_exists="replace", index=False)
    # helpful indexes
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_orders_city ON orders(city);"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_orders_amount ON orders(amount);"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);"))

# quick sanity query
with engine.begin() as conn:
    rows = conn.execute(text("SELECT COUNT(*) FROM orders")).scalar()
    per_city = conn.execute(text("""
        SELECT city, COUNT(*) AS n, SUM(amount) AS total_amount
        FROM orders
        GROUP BY city
        ORDER BY total_amount DESC
    """)).fetchall()

print("Rows loaded:", rows)
print("Totals by city:")
for c, n, tot in per_city:
    print(f"  {c:10s} | {n:>2} | {tot:>6}")
print("DB at:", DBPATH)
