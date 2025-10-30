source .venv/bin/activate && python -m src.eda
Rows: 3 | Cols: 10

Columns: order_id, amount, customer_id, name, city, api_user_id, username, email, total_todos, completed_todos

Head:
  order_id  amount  customer_id  name    city  api_user_id  username              email  total_todos  completed_todos
        1     100            1 Alice Toronto            1      Bret  Sincere@april.biz           20               11
        2     150            2   Bob  Ottawa            2 Antonette  Shanna@melissa.tv           20                8
        3      90            3  Cara Markham            3  Samantha Nathan@yesenia.net           20                7

Describe (numeric):
                 count unique                top freq        mean        std   min   25%    50%    75%    max
order_id          3.0    NaN                NaN  NaN         2.0        1.0   1.0   1.5    2.0    2.5    3.0
amount            3.0    NaN                NaN  NaN  113.333333  32.145503  90.0  95.0  100.0  125.0  150.0
customer_id       3.0    NaN                NaN  NaN         2.0        1.0   1.0   1.5    2.0    2.5    3.0
name                3      3              Alice    1         NaN        NaN   NaN   NaN    NaN    NaN    NaN
city                3      3            Toronto    1         NaN        NaN   NaN   NaN    NaN    NaN    NaN
api_user_id       3.0    NaN                NaN  NaN         2.0        1.0   1.0   1.5    2.0    2.5    3.0
username            3      3               Bret    1         NaN        NaN   NaN   NaN    NaN    NaN    NaN
email               3      3  Sincere@april.biz    1         NaN        NaN   NaN   NaN    NaN    NaN    NaN
total_todos       3.0    NaN                NaN  NaN        20.0        0.0  20.0  20.0   20.0   20.0   20.0
completed_todos   3.0    NaN                NaN  NaN    8.666667   2.081666   7.0   7.5    8.0    9.5   11.0

Saved figures to: /Users/bengawi/dev/data-extraction/reports/figures
