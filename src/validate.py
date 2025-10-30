import sys
import pandas as pd

def expect_columns(df: pd.DataFrame, cols):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise AssertionError(f"Missing expected columns: {missing}")

def expect_not_null(df: pd.DataFrame, cols):
    bad = {c: int(df[c].isna().sum()) for c in cols if c in df and df[c].isna().any()}
    if bad:
        raise AssertionError(f"Nulls found: {bad}")

def expect_range(df: pd.DataFrame, col, min_val=None, max_val=None):
    if col not in df.columns:
        return
    s = df[col]
    if min_val is not None and (s < min_val).any():
        raise AssertionError(f"{col}: values below {min_val}")
    if max_val is not None and (s > max_val).any():
        raise AssertionError(f"{col}: values above {max_val}")

def run_validations(df: pd.DataFrame) -> None:
    # schema
    expected = [
        "order_id","amount","customer_id","name","city",
        "api_user_id","username","email","total_todos","completed_todos"
    ]
    expect_columns(df, expected)

    # basic null checks
    expect_not_null(df, ["order_id","amount","customer_id","name","city","api_user_id"])

    # ranges
    expect_range(df, "amount", min_val=0)
    expect_range(df, "completed_todos", min_val=0)
    expect_range(df, "total_todos", min_val=0)

def validate_path(path: str) -> None:
    df = pd.read_csv(path)
    run_validations(df)

if __name__ == "__main__":
    try:
        validate_path(sys.argv[1])
        print("Validation: OK")
    except Exception as e:
        print("Validation: FAIL ->", e)
        sys.exit(1)
