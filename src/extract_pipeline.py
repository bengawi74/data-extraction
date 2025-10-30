import json
import os
import argparse
import pathlib
import logging

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

def setup_logging(level: str):
    lvl = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(level=lvl, format="%(asctime)s %(levelname)s %(message)s")
    return logging.getLogger("extract")

def session_with_retry(timeout: int) -> requests.Session:
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
    s.request_timeout = timeout  # attach for convenience
    return s

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

def fetch_json(s: requests.Session, url: str, filename: str, log: logging.Logger) -> pathlib.Path:
    log.info("GET %s", url)
    r = s.get(url, timeout=getattr(s, "request_timeout", 20))
    r.raise_for_status()
    path = RAW/filename
    path.write_text(r.text)
    log.info("Saved raw -> %s", path)
    return path

def build_dataset(api_base: str, timeout: int, log: logging.Logger) -> pd.DataFrame:
    s = session_with_retry(timeout)
    make_demo_inputs()

    # 1) CSV + 2) JSON (local demo files)
    orders = pd.read_csv(BASE/"data"/"sales.csv")
    customers = pd.json_normalize(
        json.loads((BASE/"data"/"customers.json").read_text())["customers"]
    )

    # 3) API
    users_path = fetch_json(s, f"{api_base}/users", "users.json", log)
    todos_path = fetch_json(s, f"{api_base}/todos", "todos.json", log)
    users = pd.read_json(users_path)
    todos = pd.read_json(todos_path)

    users_small = users.loc[:, ["id","username","email"]].rename(columns={"id":"api_user_id"})
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
    return df

def save_outputs(df: pd.DataFrame, out_dir: pathlib.Path, write_parquet: bool, log: logging.Logger):
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir/"orders_customers_users.csv"
    out_parquet = out_dir/"orders_customers_users.parquet"

    df.to_csv(out_csv, index=False)
    log.info("Saved csv -> %s", out_csv)

    if write_parquet:
        try:
            df.to_parquet(out_parquet, index=False)
            log.info("Saved parquet -> %s", out_parquet)
        except Exception as e:
            log.warning("Parquet save skipped: %s", e)

def run_validation(df: pd.DataFrame, log: logging.Logger):
    try:
        from src.validate import run_validations
        run_validations(df)
        log.info("Validation: OK")
    except Exception as e:
        log.error("Validation: FAIL -> %s", e)
        raise SystemExit(1)

def parse_args():
    parser = argparse.ArgumentParser(description="Week3 Data Extraction Pipeline")
    parser.add_argument("--api-base", default=None, help="API base URL (overrides .env)")
    parser.add_argument("--timeout", type=int, default=None, help="HTTP timeout seconds (overrides .env)")
    parser.add_argument("--out-dir", default=str(OUT), help="Output directory (default: data/processed)")
    parser.add_argument("--no-parquet", action="store_true", help="Skip Parquet output")
    parser.add_argument("--log-level", default="INFO", help="Logging level (DEBUG/INFO/WARN/ERROR)")
    return parser.parse_args()

def main():
    # env
    load_dotenv(BASE/".env")
    # CLI
    args = parse_args()
    log = setup_logging(args.log_level)

    api_base = (args.api_base or os.getenv("API_BASE", "https://jsonplaceholder.typicode.com")).rstrip("/")
    timeout = int(args.timeout or os.getenv("TIMEOUT", "20"))
    out_dir = pathlib.Path(args.out_dir)

    df = build_dataset(api_base, timeout, log)
    log.info("Rows: %s | Columns: %s", len(df), len(df.columns))
    print(df.head())

    save_outputs(df, out_dir, write_parquet=not args.no_parquet, log=log)
    run_validation(df, log)

if __name__ == "__main__":
    main()
