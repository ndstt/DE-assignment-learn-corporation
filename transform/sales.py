from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from transform.common import (
    normalized_order_id,
    normalized_student_code,
    valid_order_id,
    valid_student_code,
)


def transform_sales_silver(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("student_code", normalized_student_code())
        .withColumn("order_id", normalized_order_id())
        .filter(
            valid_student_code()
            & valid_order_id()
        )
        .withColumn("amount", F.col("amount").cast("decimal(12,2)"))
        .withColumn("order_date", F.to_timestamp(F.col("order_date")))
        .withColumn(
            "amount",
            F.when(
                F.col("product_type") == F.lit("trial_course"),
                F.lit(0),
            ).otherwise(F.col("amount")),
        )
        .withColumn("lower", F.lower(F.col("payment_status")))
        .filter(F.col("payment_status").isin("success", "completed", "paid", "complete"))
        .withColumn(
            "payment_status",
            F.lit("success"),
        )
        .drop("lower")
        .select(
            "student_code",
            "order_id",
            "order_date",
            "product_name",
            "product_type",
            "amount",
            "payment_status",
        )
    )
