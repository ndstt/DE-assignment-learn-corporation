from __future__ import annotations

from pathlib import Path

from pyspark.sql import DataFrame, SparkSession

from utils.paths import BRONZE_SOURCE_DIR, bronze_dataset_path


def read_bronze_dataset(
    spark: SparkSession,
    dataset: str,
    bronze_root: Path | None = None,
) -> DataFrame:
    bronze_path = bronze_dataset_path(dataset)

    if bronze_root is not None:
        bronze_path = bronze_root / bronze_path.relative_to(BRONZE_SOURCE_DIR)

    return (
        spark.read.option("header", True)
        .option("inferSchema", False)
        .csv(str(bronze_path))
    )
