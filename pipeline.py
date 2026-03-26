from __future__ import annotations

import argparse
from pathlib import Path

from jobs.gold import run_gold_student_360
from jobs.silver import run_silver_dataset
from utils.spark import create_local_spark_session


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the local medallion pipeline from Bronze CSV source to Silver and Gold parquet outputs"
    )
    parser.add_argument(
        "--stage",
        choices=["all", "silver", "gold"],
        default="all",
        help="Which pipeline stage to run",
    )
    parser.add_argument(
        "--bronze-root",
        type=Path,
        default=None,
        help="Optional override for the Bronze CSV source directory",
    )
    parser.add_argument(
        "--silver-root",
        type=Path,
        default=None,
        help="Optional override for the Silver parquet output root directory",
    )
    parser.add_argument(
        "--gold-root",
        type=Path,
        default=None,
        help="Optional override for the Gold parquet output root directory",
    )
    return parser.parse_args()


def run_silver_stage(
    bronze_root: Path | None = None,
    silver_root: Path | None = None,
) -> None:
    spark = create_local_spark_session("learn-pipeline-silver")

    try:
        for dataset in ["leads", "learning", "sales"]:
            silver_df = run_silver_dataset(
                spark=spark,
                dataset=dataset,
                bronze_root=bronze_root,
                silver_root=silver_root,
                output_format="parquet",
            )
            print(f"silver/{dataset}: {silver_df.count()} rows written")
    finally:
        spark.stop()


def run_gold_stage(
    silver_root: Path | None = None,
    gold_root: Path | None = None,
) -> None:
    spark = create_local_spark_session("learn-pipeline-gold")

    try:
        gold_df = run_gold_student_360(
            spark=spark,
            silver_root=silver_root,
            gold_root=gold_root,
        )
        print(f"gold/student_360: {gold_df.count()} rows written")
    finally:
        spark.stop()


def main() -> None:
    args = parse_args()

    if args.stage in {"all", "silver"}:
        run_silver_stage(
            bronze_root=args.bronze_root,
            silver_root=args.silver_root,
        )

    if args.stage in {"all", "gold"}:
        run_gold_stage(
            silver_root=args.silver_root,
            gold_root=args.gold_root,
        )


if __name__ == "__main__":
    main()
