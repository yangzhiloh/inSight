"""Command-line entry point for the insight tool."""

import argparse
import logging
import time

from insight.db import connect, init_schema
from insight.ingest import ingest


def build_parser() -> argparse.ArgumentParser:
    """Define the insight command and its subcommands."""
    parser = argparse.ArgumentParser(
        prog="insight", description="Offline semantic search over your photos."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    ingest_cmd = sub.add_parser("ingest", help="Scan a folder into the catalog.")
    ingest_cmd.add_argument("folder", help="Folder of photos to scan (searched recursively).")
    ingest_cmd.add_argument(
        "--db", default="catalog.db", help="Catalog database file (default: %(default)s)."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the insight CLI and return a process exit code."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)

    if args.command == "ingest":
        start = time.perf_counter()
        conn = connect(args.db)
        try:
            init_schema(conn)
            stats = ingest(conn, args.folder)
        except NotADirectoryError as e:
            print(f"error: {e}")
            return 2
        finally:
            conn.close()
        elapsed = time.perf_counter() - start
        print(
            f"added={stats.added} updated={stats.updated} "
            f"unchanged={stats.unchanged} skipped={stats.skipped} in {elapsed:.1f}s"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())