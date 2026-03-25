from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from transform.common import (
    format_then_cast_timestamp,
    normalized_student_code,
    valid_student_code,
)


def transform_learning_silver(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("student_code", normalized_student_code())
        .filter(
            valid_student_code()
            & F.col("event_time").isNotNull()
            & (F.col("duration_minutes") >= 0)
        )
        .withColumn("duration_minutes", F.col("duration_minutes").cast("int"))
        .withColumn(
            "event_time",
            format_then_cast_timestamp(
                "event_time",
                slash_pattern="MM/dd/yyyy HH:mm",
            ),
        )
        .filter(F.col("event_time").isNotNull())
        .withColumn(
            "event_name",
            F.regexp_replace(
                F.lower(F.lower(F.col("event_name"))),
                r"\s+",
                "_",
            ),
        )
        .select(
            "student_code",
            "event_time",
            "event_name",
            "subject",
            "chapter",
            "duration_minutes",
            "platform",
        )
    )
