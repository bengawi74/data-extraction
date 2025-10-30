.PHONY: install extract validate all clean

install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt || true

extract:
	source .venv/bin/activate && python src/extract_pipeline.py

validate:
	source .venv/bin/activate && python -c "from src.validate import validate_path; validate_path('data/processed/orders_customers_users.csv')"

all: extract validate

clean:
	rm -rf data/processed/*.csv data/processed/*.parquet
