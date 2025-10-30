import pathlib

import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine, text

BASE = pathlib.Path(__file__).resolve().parent.parent
DB = BASE / "data" / "warehouse.db"
REPORTS = BASE / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB}")

query = """
SELECT
  city,
  COUNT(*) AS orders_count,
  SUM(amount) AS total_amount,
  ROUND(AVG(completion_rate), 3) AS avg_completion_rate
FROM orders
GROUP BY city
ORDER BY total_amount DESC;
"""

df = pd.read_sql_query(text(query), engine)

# --- Markdown summary ---
summary = REPORTS / "weekly_report.md"
with open(summary, "w") as f:
    f.write("# Weekly Data Report\n\n")
    f.write(f"Total rows in orders: {df['orders_count'].sum()}\n\n")
    f.write("## Totals by City\n\n")
    f.write(df.to_markdown(index=False))
print("Saved:", summary)

# --- Chart ---
fig = plt.figure(figsize=(6, 4))
plt.bar(df["city"], df["total_amount"])
plt.title("Total Amount by City")
plt.xlabel("City")
plt.ylabel("Total Amount")
plt.tight_layout()
plt.savefig(REPORTS / "total_amount_by_city.png")
print("Chart saved ->", REPORTS / "total_amount_by_city.png")
