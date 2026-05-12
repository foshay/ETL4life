# pyright: reportMissingImports=false

import csv
import json
import platform
import sqlite3
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

try:
    from models.locations2 import Location

    HAS_PYDANTIC = True
except ModuleNotFoundError:
    HAS_PYDANTIC = False
    Location = None

ORM_CTX = None


def get_orm_ctx():
    global ORM_CTX
    if ORM_CTX is not None:
        return ORM_CTX

    try:
        from sqlalchemy import Integer, Text, create_engine
        from sqlalchemy.orm import Session, declarative_base, mapped_column
        from sqlalchemy.pool import StaticPool
    except ModuleNotFoundError:
        return None

    Base = declarative_base()

    class LocationORM(Base):
        __tablename__ = "locations"

        id = mapped_column(Integer, primary_key=True, autoincrement=True)
        location_id = mapped_column(Integer)
        name = mapped_column(Text)
        street = mapped_column(Text)
        city = mapped_column(Text)
        state = mapped_column(Text)
        zip_code = mapped_column(Text)
        open_date = mapped_column(Text)
        close_date = mapped_column(Text, nullable=True)

    ORM_CTX = {
        "Base": Base,
        "LocationORM": LocationORM,
        "Session": Session,
        "create_engine": create_engine,
        "StaticPool": StaticPool,
    }
    return ORM_CTX


def has_sqlalchemy() -> bool:
    return get_orm_ctx() is not None


def load_rows() -> tuple[list[dict], list]:
    data_path = Path("json/locations_2.json")
    with data_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    dict_rows = list(raw)
    model_rows = [Location.model_validate(row) for row in raw] if HAS_PYDANTIC else []
    return dict_rows, model_rows


def make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA journal_mode = OFF")
    conn.execute("PRAGMA synchronous = OFF")
    conn.execute("PRAGMA temp_store = MEMORY")
    return conn


def reset_table(conn: sqlite3.Connection) -> None:
    conn.execute("DROP TABLE IF EXISTS locations")
    conn.execute(
        """
        CREATE TABLE locations (
            location_id INTEGER,
            name TEXT,
            street TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT,
            open_date TEXT,
            close_date TEXT
        )
        """
    )


def to_tuples_from_dicts(rows: Sequence[dict]) -> list[tuple]:
    return [
        (
            row["location_id"],
            row["name"],
            row["address"]["street"],
            row["address"]["city"],
            row["address"]["state"],
            row["address"]["zip_code"],
            row["operating_dates"]["open_date"],
            row["operating_dates"].get("close_date"),
        )
        for row in rows
    ]


def to_tuples_from_models_attr(rows: Sequence) -> list[tuple]:
    return [
        (
            row.location_id,
            row.name,
            row.address.street,
            row.address.city,
            row.address.state,
            row.address.zip_code,
            row.operating_dates.open_date,
            row.operating_dates.close_date,
        )
        for row in rows
    ]


def to_tuples_from_models_dump(rows: Sequence) -> list[tuple]:
    dumped = [row.model_dump(mode="python") for row in rows]
    return to_tuples_from_dicts(dumped)


def to_mappings_from_dicts(rows: Sequence[dict]) -> list[dict]:
    return [
        {
            "location_id": row["location_id"],
            "name": row["name"],
            "street": row["address"]["street"],
            "city": row["address"]["city"],
            "state": row["address"]["state"],
            "zip_code": row["address"]["zip_code"],
            "open_date": row["operating_dates"]["open_date"],
            "close_date": row["operating_dates"].get("close_date"),
        }
        for row in rows
    ]


def to_mappings_from_models_attr(rows: Sequence) -> list[dict]:
    return [
        {
            "location_id": row.location_id,
            "name": row.name,
            "street": row.address.street,
            "city": row.address.city,
            "state": row.address.state,
            "zip_code": row.address.zip_code,
            "open_date": row.operating_dates.open_date,
            "close_date": row.operating_dates.close_date,
        }
        for row in rows
    ]


def to_mappings_from_models_dump(rows: Sequence) -> list[dict]:
    dumped = [row.model_dump(mode="python") for row in rows]
    return to_mappings_from_dicts(dumped)


def insert_many(conn: sqlite3.Connection, payload: Iterable[tuple]) -> None:
    conn.executemany(
        """
        INSERT INTO locations (
            location_id, name, street, city, state, zip_code, open_date, close_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        payload,
    )


def bench_case(name: str, rows, converter, runs: int = 200, warmups: int = 10) -> dict:
    conn = make_conn()
    timings_us: list[float] = []

    total_iters = warmups + runs
    for i in range(total_iters):
        reset_table(conn)
        start_ns = time.perf_counter_ns()
        payload = converter(rows)
        insert_many(conn, payload)
        conn.commit()
        elapsed_us = (time.perf_counter_ns() - start_ns) / 1000
        if i >= warmups:
            timings_us.append(elapsed_us)

    conn.close()
    return {
        "name": name,
        "mean_us": statistics.mean(timings_us),
        "median_us": statistics.median(timings_us),
        "p95_us": statistics.quantiles(timings_us, n=100)[94],
        "min_us": min(timings_us),
        "max_us": max(timings_us),
        "runs": runs,
    }


def bench_insert_only_case(name: str, payload: Sequence[tuple], runs: int = 200, warmups: int = 10) -> dict:
    conn = make_conn()
    timings_us: list[float] = []

    total_iters = warmups + runs
    for i in range(total_iters):
        reset_table(conn)
        start_ns = time.perf_counter_ns()
        insert_many(conn, payload)
        conn.commit()
        elapsed_us = (time.perf_counter_ns() - start_ns) / 1000
        if i >= warmups:
            timings_us.append(elapsed_us)

    conn.close()
    return {
        "name": name,
        "mean_us": statistics.mean(timings_us),
        "median_us": statistics.median(timings_us),
        "p95_us": statistics.quantiles(timings_us, n=100)[94],
        "min_us": min(timings_us),
        "max_us": max(timings_us),
        "runs": runs,
    }


def make_orm_engine():
    orm_ctx = get_orm_ctx()
    if orm_ctx is None:
        raise RuntimeError("SQLAlchemy is not installed")

    engine = orm_ctx["create_engine"](
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=orm_ctx["StaticPool"],
    )
    with engine.connect() as conn:
        conn.exec_driver_sql("PRAGMA journal_mode = OFF")
        conn.exec_driver_sql("PRAGMA synchronous = OFF")
        conn.exec_driver_sql("PRAGMA temp_store = MEMORY")
    return engine


def reset_table_orm(engine) -> None:
    orm_ctx = get_orm_ctx()
    if orm_ctx is None:
        raise RuntimeError("SQLAlchemy is not installed")
    orm_ctx["Base"].metadata.drop_all(engine)
    orm_ctx["Base"].metadata.create_all(engine)


def bench_orm_bulk_case(name: str, rows, converter, runs: int = 200, warmups: int = 10) -> dict:
    orm_ctx = get_orm_ctx()
    if orm_ctx is None:
        raise RuntimeError("SQLAlchemy is not installed")

    Session = orm_ctx["Session"]
    LocationORM = orm_ctx["LocationORM"]

    engine = make_orm_engine()
    timings_us: list[float] = []

    total_iters = warmups + runs
    for i in range(total_iters):
        reset_table_orm(engine)
        start_ns = time.perf_counter_ns()
        mappings = converter(rows)
        with Session(engine) as session:
            session.bulk_insert_mappings(LocationORM, mappings)
            session.commit()
        elapsed_us = (time.perf_counter_ns() - start_ns) / 1000
        if i >= warmups:
            timings_us.append(elapsed_us)

    engine.dispose()
    return {
        "name": name,
        "mean_us": statistics.mean(timings_us),
        "median_us": statistics.median(timings_us),
        "p95_us": statistics.quantiles(timings_us, n=100)[94],
        "min_us": min(timings_us),
        "max_us": max(timings_us),
        "runs": runs,
    }


def bench_orm_bulk_insert_only_case(name: str, mappings: Sequence[dict], runs: int = 200, warmups: int = 10) -> dict:
    orm_ctx = get_orm_ctx()
    if orm_ctx is None:
        raise RuntimeError("SQLAlchemy is not installed")

    Session = orm_ctx["Session"]
    LocationORM = orm_ctx["LocationORM"]

    engine = make_orm_engine()
    timings_us: list[float] = []

    total_iters = warmups + runs
    for i in range(total_iters):
        reset_table_orm(engine)
        start_ns = time.perf_counter_ns()
        with Session(engine) as session:
            session.bulk_insert_mappings(LocationORM, mappings)
            session.commit()
        elapsed_us = (time.perf_counter_ns() - start_ns) / 1000
        if i >= warmups:
            timings_us.append(elapsed_us)

    engine.dispose()
    return {
        "name": name,
        "mean_us": statistics.mean(timings_us),
        "median_us": statistics.median(timings_us),
        "p95_us": statistics.quantiles(timings_us, n=100)[94],
        "min_us": min(timings_us),
        "max_us": max(timings_us),
        "runs": runs,
    }


def bench_orm_add_all_case(name: str, mappings: Sequence[dict], runs: int = 200, warmups: int = 10) -> dict:
    orm_ctx = get_orm_ctx()
    if orm_ctx is None:
        raise RuntimeError("SQLAlchemy is not installed")

    Session = orm_ctx["Session"]
    LocationORM = orm_ctx["LocationORM"]

    engine = make_orm_engine()
    timings_us: list[float] = []

    total_iters = warmups + runs
    for i in range(total_iters):
        reset_table_orm(engine)
        start_ns = time.perf_counter_ns()
        with Session(engine) as session:
            objs = [LocationORM(**row) for row in mappings]
            session.add_all(objs)
            session.commit()
        elapsed_us = (time.perf_counter_ns() - start_ns) / 1000
        if i >= warmups:
            timings_us.append(elapsed_us)

    engine.dispose()
    return {
        "name": name,
        "mean_us": statistics.mean(timings_us),
        "median_us": statistics.median(timings_us),
        "p95_us": statistics.quantiles(timings_us, n=100)[94],
        "min_us": min(timings_us),
        "max_us": max(timings_us),
        "runs": runs,
    }


def print_report(results: Sequence[dict]) -> None:
    baseline = next(r for r in results if r["name"] == "dict_rows")
    print("\nSQL insert benchmark (lower is better)\n")
    for r in results:
        slowdown = r["mean_us"] / baseline["mean_us"]
        print(
            f"{r['name']:<18} "
            f"mean={r['mean_us']:.1f}us "
            f"median={r['median_us']:.1f}us "
            f"p95={r['p95_us']:.1f}us "
            f"min={r['min_us']:.1f}us "
            f"max={r['max_us']:.1f}us "
            f"x{slowdown:.2f}"
        )


def get_git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def append_csv_results(
    csv_path: Path,
    sections: dict[str, Sequence[dict]],
    *,
    rows_per_run: int,
    runs: int,
    warmups: int,
    pydantic_enabled: bool,
    sqlalchemy_enabled: bool,
) -> None:
    fieldnames = [
        "timestamp_utc",
        "git_commit",
        "python_version",
        "platform",
        "rows_per_run",
        "runs",
        "warmups",
        "pydantic_enabled",
        "sqlalchemy_enabled",
        "section",
        "case",
        "mean_us",
        "median_us",
        "p95_us",
        "min_us",
        "max_us",
        "slowdown_vs_dict_mean",
    ]

    timestamp_utc = datetime.now(timezone.utc).isoformat()
    git_commit = get_git_commit()
    py_version = platform.python_version()
    plat = platform.platform()

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        for section_name, results in sections.items():
            baseline = next(r for r in results if r["name"] == "dict_rows")
            baseline_mean = baseline["mean_us"]
            for r in results:
                writer.writerow(
                    {
                        "timestamp_utc": timestamp_utc,
                        "git_commit": git_commit,
                        "python_version": py_version,
                        "platform": plat,
                        "rows_per_run": rows_per_run,
                        "runs": runs,
                        "warmups": warmups,
                        "pydantic_enabled": pydantic_enabled,
                        "sqlalchemy_enabled": sqlalchemy_enabled,
                        "section": section_name,
                        "case": r["name"],
                        "mean_us": f"{r['mean_us']:.6f}",
                        "median_us": f"{r['median_us']:.6f}",
                        "p95_us": f"{r['p95_us']:.6f}",
                        "min_us": f"{r['min_us']:.6f}",
                        "max_us": f"{r['max_us']:.6f}",
                        "slowdown_vs_dict_mean": f"{(r['mean_us'] / baseline_mean):.6f}",
                    }
                )


if __name__ == "__main__":
    RUNS = 200
    WARMUPS = 10
    CSV_PATH = Path("benchmarks/sql_insert_benchmark_history.csv")

    dict_rows, model_rows = load_rows()

    end_to_end_results = [bench_case("dict_rows", dict_rows, to_tuples_from_dicts, runs=RUNS, warmups=WARMUPS)]
    if HAS_PYDANTIC:
        end_to_end_results.extend(
            [
                bench_case("model_attr", model_rows, to_tuples_from_models_attr, runs=RUNS, warmups=WARMUPS),
                bench_case("model_dump", model_rows, to_tuples_from_models_dump, runs=RUNS, warmups=WARMUPS),
            ]
        )

    payload_dict = to_tuples_from_dicts(dict_rows)

    insert_only_results = [bench_insert_only_case("dict_rows", payload_dict, runs=RUNS, warmups=WARMUPS)]
    if HAS_PYDANTIC:
        payload_model_attr = to_tuples_from_models_attr(model_rows)
        payload_model_dump = to_tuples_from_models_dump(model_rows)
        insert_only_results.extend(
            [
                bench_insert_only_case("model_attr", payload_model_attr, runs=RUNS, warmups=WARMUPS),
                bench_insert_only_case("model_dump", payload_model_dump, runs=RUNS, warmups=WARMUPS),
            ]
        )

    print(f"rows_per_run={len(dict_rows)}")
    if not HAS_PYDANTIC:
        print("pydantic not installed: model_attr/model_dump cases skipped")
    print("\n=== End-to-end (convert + insert) ===")
    print_report(end_to_end_results)
    print("\n=== Insert-only (payload precomputed) ===")
    print_report(insert_only_results)

    sections_for_csv: dict[str, Sequence[dict]] = {
        "raw_end_to_end": end_to_end_results,
        "raw_insert_only": insert_only_results,
    }

    if not has_sqlalchemy():
        print("\nSQLAlchemy is not installed; skipping ORM comparison.")
        print("Install it with: python -m pip install sqlalchemy")
        append_csv_results(
            CSV_PATH,
            sections_for_csv,
            rows_per_run=len(dict_rows),
            runs=RUNS,
            warmups=WARMUPS,
            pydantic_enabled=HAS_PYDANTIC,
            sqlalchemy_enabled=False,
        )
        print(f"\nCSV tracker updated: {CSV_PATH}")
        raise SystemExit(0)

    orm_end_to_end_results = [
        bench_orm_bulk_case("dict_rows", dict_rows, to_mappings_from_dicts, runs=RUNS, warmups=WARMUPS)
    ]
    if HAS_PYDANTIC:
        orm_end_to_end_results.extend(
            [
                bench_orm_bulk_case(
                    "model_attr", model_rows, to_mappings_from_models_attr, runs=RUNS, warmups=WARMUPS
                ),
                bench_orm_bulk_case(
                    "model_dump", model_rows, to_mappings_from_models_dump, runs=RUNS, warmups=WARMUPS
                ),
            ]
        )

    mappings_dict = to_mappings_from_dicts(dict_rows)

    orm_insert_only_results = [
        bench_orm_bulk_insert_only_case("dict_rows", mappings_dict, runs=RUNS, warmups=WARMUPS)
    ]
    if HAS_PYDANTIC:
        mappings_model_attr = to_mappings_from_models_attr(model_rows)
        mappings_model_dump = to_mappings_from_models_dump(model_rows)
        orm_insert_only_results.extend(
            [
                bench_orm_bulk_insert_only_case("model_attr", mappings_model_attr, runs=RUNS, warmups=WARMUPS),
                bench_orm_bulk_insert_only_case("model_dump", mappings_model_dump, runs=RUNS, warmups=WARMUPS),
            ]
        )

    orm_tracked_results = [bench_orm_add_all_case("dict_rows", mappings_dict, runs=RUNS, warmups=WARMUPS)]
    if HAS_PYDANTIC:
        orm_tracked_results.extend(
            [
                bench_orm_add_all_case("model_attr", mappings_model_attr, runs=RUNS, warmups=WARMUPS),
                bench_orm_add_all_case("model_dump", mappings_model_dump, runs=RUNS, warmups=WARMUPS),
            ]
        )

    print("\n=== ORM bulk_insert_mappings (convert + insert) ===")
    print_report(orm_end_to_end_results)
    print("\n=== ORM bulk_insert_mappings (insert-only) ===")
    print_report(orm_insert_only_results)
    print("\n=== ORM add_all tracked objects (insert path) ===")
    print_report(orm_tracked_results)

    sections_for_csv["orm_bulk_end_to_end"] = orm_end_to_end_results
    sections_for_csv["orm_bulk_insert_only"] = orm_insert_only_results
    sections_for_csv["orm_add_all_insert_path"] = orm_tracked_results

    append_csv_results(
        CSV_PATH,
        sections_for_csv,
        rows_per_run=len(dict_rows),
        runs=RUNS,
        warmups=WARMUPS,
        pydantic_enabled=HAS_PYDANTIC,
        sqlalchemy_enabled=True,
    )
    print(f"\nCSV tracker updated: {CSV_PATH}")
