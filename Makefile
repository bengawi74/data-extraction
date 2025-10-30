.PHONY: install extract clean

install:
\tpython -m pip install --upgrade pip
\tpython -m pip install -r requirements.txt || true

extract:
\tsource .venv/bin/activate && python src/extract_pipeline.py

clean:
\trm -rf data/processed/*.csv data/processed/*.parquet
