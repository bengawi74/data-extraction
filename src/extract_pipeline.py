import json
import pathlib
import pandas as pd
import requests

BASE = pathlib.Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"
RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

def make_demo_inputs():
    (BASE/"data"/"sales.csv").write_text("order_id,amount,customer_id\n1,100,1\n2,150,2\n3,90,3\n")
    (BASE/"data"/"customers.json").write_text(json.dumps({
        "customers":[
            {"id":1,"name":"Alice","city":"Toronto"},
            {"id":2,"name":"Bob","city":"Ottawa"},
            {"id":3,"name":"Cara","city":"Markham"}
        ]
    }, indent=2))

def fetch_api(url, filename):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    path = RAW/filename
    path.write_text(r.text)
    return path

def main():
    make_demo_inputs()

    # 1) CSV
    orders = pd.read_csv(BASE/"data"/"sales.csv")

    # 2) JSON
    customers = pd.json_normalize(json.loads((BASE/"data"/"customers.json").read_text())["customers"])

    # 3) API (JSONPlaceholder: users + todos)
    users_path = fetch_api("https://jsonplaceholder.typicode.com/users", "users.json")
    todos_path = fetch_api("https://jsonplaceholder.typicode.com/todos", "todos.json")

    users = pd.read_json(users_path)
    todos = pd.read_json(todos_path)

    # Select & rename a couple of useful columns
    users_small = users.loc[:, ["id", "username", "email"]].rename(columns={"id":"api_user_id"})
    todos_small = todos.loc[:, ["userId","id","title","completed"]].rename(columns={"userId":"api_user_id","id":"todo_id"})

    # Example join: orders ↔ customers (our local demo) then annotate with API users
    df = orders.merge(customers, left_on="customer_id", right_on="id", how="left", suffixes=("","_cust"))
    df = df.drop(columns=["id"])  # from customers
    # attach an API user to each order (cycle through to show a join)
    df["api_user_id"] = (df.index % len(users_small)) + 1
    df = df.merge(users_small, on="api_user_id", how="left")

    # Aggregate todos per api_user_id and join
    todos_stats = todos_small.groupby("api_user_id", as_index=False).agg(
        total_todos=("todo_id","count"),
        completed_todos=("completed","sum")
    )
    df = df.merge(todos_stats, on="api_user_id", how="left")

    # Save outputs
    out_csv = OUT/"orders_customers_users.csv"
    out_parquet = OUT/"orders_customers_users.parquet"
    df.to_csv(out_csv, index=False)
    try:
        df.to_parquet(out_parquet, index=False)
    except Exception as e:
        print("Parquet save skipped:", e)

    print("Rows:", len(df))
    print("Preview:")
    print(df.head())
    print("Saved:", out_csv)
    if out_parquet.exists(): print("Saved:", out_parquet)

if __name__ == "__main__":
    main()
