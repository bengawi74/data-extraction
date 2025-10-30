import pathlib
import re

import pandas as pd

BASE = pathlib.Path(__file__).resolve().parent.parent
INP = BASE / "data" / "processed" / "orders_customers_users.csv"
OUTD = BASE / "data" / "cleaned"
OUTD.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INP)

# --- basic cleaning ---
df["city"] = df["city"].astype(str).str.strip().str.title()
df["email"] = df["email"].astype(str).str.strip().str.lower()

# email validity (very light check)
email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
df["valid_email"] = df["email"].apply(lambda x: bool(email_re.match(x)))

# completion rate
df["completion_rate"] = (
    df["completed_todos"].astype(float) / df["total_todos"].replace(0, pd.NA)
).astype(float)

# amount buckets
bins = [-1, 99, 149, float("inf")]
labels = ["low", "mid", "high"]
df["amount_bucket"] = pd.cut(df["amount"], bins=bins, labels=labels)

# reorder columns (nice to read)
cols = [
    "order_id",
    "customer_id",
    "name",
    "city",
    "email",
    "valid_email",
    "amount",
    "amount_bucket",
    "total_todos",
    "completed_todos",
    "completion_rate",
    "api_user_id",
    "username",
]
df = df[[c for c in cols if c in df.columns]]

# write
csv_path = OUTD / "orders_cleaned.csv"
parq_path = OUTD / "orders_cleaned.parquet"
df.to_csv(csv_path, index=False)
df.to_parquet(parq_path, index=False)

print("Cleaned rows:", len(df), "| cols:", len(df.columns))
print("Saved ->", csv_path)
print("Saved ->", parq_path)
print("\nPreview:\n", df.head().to_string(index=False))
