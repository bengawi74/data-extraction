import argparse
import runpy
import sys


def _run_module(mod: str, argv=None):
    """
    Execute `mod` like `python -m mod`, but with a clean argv so the
    inner argparse doesn't see 'extract'/'report'/etc.
    """
    old_argv = sys.argv[:]
    try:
        sys.argv = [mod.split(".")[-1]] + (argv or [])
        runpy.run_module(mod, run_name="__main__")
    finally:
        sys.argv = old_argv


def main():
    parser = argparse.ArgumentParser(prog="datax", description="Data extraction toolkit")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("extract", help="Run extract pipeline")
    sub.add_parser("transform", help="Run cleaning transform")
    sub.add_parser("report", help="Generate weekly report")
    sub.add_parser("all", help="Run all stages: extract, transform, report")

    args = parser.parse_args()

    if args.cmd == "extract":
        _run_module("src.extract_pipeline", argv=[])
    elif args.cmd == "transform":
        _run_module("src.transform", argv=[])
    elif args.cmd == "report":
        _run_module("src.report", argv=[])
    elif args.cmd == "all":
        _run_module("src.extract_pipeline", argv=[])
        _run_module("src.transform", argv=[])
        _run_module("src.report", argv=[])


if __name__ == "__main__":
    main()
