.PHONY: install extract validate eda transform all clean

install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt || true

extract:
	source .venv/bin/activate && python -m src.extract_pipeline

validate:
	source .venv/bin/activate && python -c "from src.validate import validate_path; validate_path('data/processed/orders_customers_users.csv')"

eda:
	source .venv/bin/activate && python -m src.eda

transform:
	source .venv/bin/activate && python -m src.transform

all: extract validate eda transform

clean:
	rm -rf data/processed/*.csv data/processed/*.parquet reports/ data/cleaned/
