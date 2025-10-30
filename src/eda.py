import pathlib

import matplotlib.pyplot as plt
import pandas as pd

BASE = pathlib.Path(__file__).resolve().parent.parent
INP = BASE / "data" / "processed" / "orders_customers_users.csv"
RPT = BASE / "reports"
FIGS = RPT / "figures"
RPT.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INP)

# ---- CLI-style textual summary ----
print("Rows:", len(df), "| Cols:", len(df.columns))
print("\nColumns:", ", ".join(df.columns))
print("\nHead:\n", df.head().to_string(index=False))

# handle describe() for older pandas
desc = df.describe(include="all")
print("\nDescribe (numeric):\n", desc.T.to_string())

# ---- Charts (saved as PNGs) ----
# 1) Amount by city (bar)
ax_data = df.groupby("city", as_index=False)["amount"].sum().sort_values("amount")
ax_data.plot(x="city", y="amount", kind="bar", legend=False, rot=45)
plt.title("Total Amount by City")
plt.tight_layout()
plt.savefig(FIGS / "amount_by_city.png")
plt.clf()

# 2) Completed vs total todos (scatter)
plt.plot(df["total_todos"], df["completed_todos"], marker="o", linestyle="")
plt.xlabel("Total Todos")
plt.ylabel("Completed Todos")
plt.title("Todos: Completed vs Total")
plt.tight_layout()
plt.savefig(FIGS / "todos_completed_vs_total.png")
plt.clf()

print("\nSaved figures to:", FIGS)
