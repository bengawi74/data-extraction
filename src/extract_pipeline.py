import json
import os
import pathlib
import logging
from typing import Tuple

import pandas as pd
import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = pathlib.Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"
RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

# ----- logging -----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger("extract")

def session_with_retry(timeout: int) -> Tuple[requests.Session, int]:
    s = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True,
    )
    s.mount("http://", HTTPAdapter(max_retries=retry))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    return s, timeout

def make_demo_inputs():
    (BASE/"data"/"sales.csv").write_text(
        "order_id,amount,customer_id\n1,100,1\n2,150,2\n3,90,3\n"
    )
    (BASE/"data"/"customers.json").write_text(json.dumps({
        "customers":[
            {"id":1,"name":"Alice","city":"Toronto"},
            {"id":2,"name":"Bob","city":"Ottawa"},
            {"id":3,"name":"Cara","city":"Markham"}
        ]
    }, indent=2))

def fetch_json(s: requests.Session, url: str, timeout: int, filename: str) -> pathlib.Path:
    log.info("GET %s", url)
    r = s.get(url, timeout=timeout)
    r.raise_for_status()
    path = RAW/filename
    path.write_text(r.text)
    log.info("Saved raw -> %s", path)
    return path

def main():
    # env
    load_dotenv(BASE / ".env")
    api_base = os.getenv("API_BASE", "https://jsonplaceholder.typicode.com").rstrip("/")
    timeout = int(os.getenv("TIMEOUT", "20"))

    s, timeout = session_with_retry(timeout)

    make_demo_inputs()

    # 1) CSV
    orders = pd.read_csv(BASE/"data"/"sales.csv")

    # 2) JSON
    customers = pd.json_normalize(
        json.loads((BASE/"data"/"customers.json").read_text())["customers"]
    )

    # 3) API (users + todos)
    users_path = fetch_json(s, f"{api_base}/users", timeout, "users.json")
    todos_path = fetch_json(s, f"{api_base}/todos", timeout, "todos.json")

    users = pd.read_json(users_path)
    todos = pd.read_json(todos_path)

    users_small = users.loc[:, ["id", "username", "email"]].rename(columns={"id":"api_user_id"})
    todos_small = todos.loc[:, ["userId","id","title","completed"]].rename(
        columns={"userId":"api_user_id","id":"todo_id"}
    )

    df = orders.merge(customers, left_on="customer_id", right_on="id", how="left", suffixes=("","_cust"))
    df = df.drop(columns=["id"])
    df["api_user_id"] = (df.index % len(users_small)) + 1
    df = df.merge(users_small, on="api_user_id", how="left")

    todos_stats = todos_small.groupby("api_user_id", as_index=False).agg(
        total_todos=("todo_id","count"),
        completed_todos=("completed","sum")
    )
    df = df.merge(todos_stats, on="api_user_id", how="left")

    out_csv = OUT/"orders_customers_users.csv"
    out_parquet = OUT/"orders_customers_users.parquet"
    df.to_csv(out_csv, index=False)
    log.info("Saved csv -> %s", out_csv)
    try:
        df.to_parquet(out_parquet, index=False)
        log.info("Saved parquet -> %s", out_parquet)
    except Exception as e:
        log.warning("Parquet save skipped: %s", e)

    log.info("Rows: %s | Columns: %s", len(df), len(df.columns))
    print(df.head())

if __name__ == "__main__":
    main()
