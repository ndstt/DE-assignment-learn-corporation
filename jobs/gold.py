from __future__ import annotations

import argparse
from pathlib import Path

from pyspark.sql import SparkSession

from transform import transform_student_360_gold
from utils.paths import GOLD_DIR, SILVER_DIR, gold_dataset_path
from utils.spark import create_local_spark_session


def run_gold_student_360(
    spark: SparkSession,
    silver_root: Path | None = None,
    gold_root: Path | None = None,
) -> object:
    silver_root = silver_root or SILVER_DIR

    leads_silver_df = spark.read.parquet(str(silver_root / "leads"))
    learning_silver_df = spark.read.parquet(str(silver_root / "learning_activity"))
    sales_silver_df = spark.read.parquet(str(silver_root / "sales"))

    gold_df = transform_student_360_gold(
        leads_silver_df=leads_silver_df,
        learning_silver_df=learning_silver_df,
        sales_silver_df=sales_silver_df,
    )

    gold_path = gold_dataset_path("student_360")
    if gold_root is not None:
        gold_path = gold_root / gold_path.relative_to(GOLD_DIR)

    gold_df.write.mode("overwrite").parquet(str(gold_path))
    return gold_df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Gold student_360 from Silver parquet datasets")
    parser.add_argument(
        "--silver-root",
        type=Path,
        default=None,
        help="Optional override for the Silver input root directory",
    )
    parser.add_argument(
        "--gold-root",
        type=Path,
        default=None,
        help="Optional override for the Gold output root directory",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spark = create_local_spark_session("learn-gold-job")

    try:
        gold_df = run_gold_student_360(
            spark=spark,
            silver_root=args.silver_root,
            gold_root=args.gold_root,
        )
        print(f"student_360: {gold_df.count()} rows written")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
