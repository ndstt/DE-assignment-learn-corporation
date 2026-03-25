from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from utils.spark import create_local_spark_session

from pyspark.sql import DataFrame, SparkSession

from transform import (
    transform_leads_silver,
    transform_learning_silver,
    transform_sales_silver,
)
from utils.paths import SILVER_CSV_DIR, SILVER_DIR, silver_dataset_path
from utils.readers import read_bronze_dataset

TRANSFORMS = {
    "leads": transform_leads_silver,
    "learning": transform_learning_silver,
    "sales": transform_sales_silver,
}

CSV_FILE_NAMES = {
    "leads": "leads.csv",
    "learning": "learning_activity.csv",
    "sales": "sales.csv",
}


def remove_existing_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def write_single_csv(df: DataFrame, output_file: Path) -> None:
    temp_dir = output_file.parent / f".{output_file.stem}_tmp"
    remove_existing_path(temp_dir)
    remove_existing_path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    (
        df.coalesce(1)
        .write.mode("overwrite")
        .option("header", True)
        .csv(str(temp_dir))
    )

    part_files = list(temp_dir.glob("part-*.csv"))
    if not part_files:
        raise FileNotFoundError(f"No CSV part file was created in {temp_dir}")

    shutil.move(str(part_files[0]), str(output_file))
    remove_existing_path(temp_dir)


def run_silver_dataset(
    spark: SparkSession,
    dataset: str,
    bronze_root: Path | None = None,
    silver_root: Path | None = None,
    output_format: str = "parquet",
) -> DataFrame:
    df = read_bronze_dataset(
        spark=spark,
        dataset=dataset,
        bronze_root=bronze_root,
    )
    silver_df = TRANSFORMS[dataset](df)

    if output_format == "csv":
        output_root = silver_root or SILVER_CSV_DIR
        output_file = output_root / CSV_FILE_NAMES[dataset]
        write_single_csv(silver_df, output_file)
    else:
        silver_path = silver_dataset_path(dataset)
        if silver_root is not None:
            silver_path = silver_root / silver_path.relative_to(SILVER_DIR)
        silver_df.write.mode("overwrite").parquet(str(silver_path))

    return silver_df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Silver datasets from Bronze CSV source files")
    parser.add_argument(
        "--dataset",
        choices=["all", "leads", "learning", "sales"],
        default="all",
        help="Which Silver dataset to build",
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
        help="Optional override for the Silver output root directory",
    )
    parser.add_argument(
        "--output-format",
        choices=["parquet", "csv"],
        default="parquet",
        help="Write Silver as parquet directories or single CSV files",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spark = create_local_spark_session("learn-silver-job")
    datasets = ["leads", "learning", "sales"] if args.dataset == "all" else [args.dataset]

    try:
        for dataset in datasets:
            silver_df = run_silver_dataset(
                spark=spark,
                dataset=dataset,
                bronze_root=args.bronze_root,
                silver_root=args.silver_root,
                output_format=args.output_format,
            )
            print(f"{dataset}: {silver_df.count()} rows written")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
