from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from transform.common import (
    format_then_cast_timestamp,
    normalized_student_code,
    valid_student_code,
)


def transform_leads_silver(df: DataFrame) -> DataFrame:
    phone_digits = F.regexp_replace(
        F.coalesce(F.col("mobile_phone"), F.lit("")),
        r"[^0-9]",
        "",
    )

    source_channel_raw = F.lower(F.trim(F.col("source_channel")))

    latest_lead_window = Window.partitionBy("student_code").orderBy(
        F.col("lead_created_at").desc_nulls_last()
    )

    return (
        df.withColumn("student_code", normalized_student_code())
        .withColumn("phone_digits", phone_digits)
        .withColumn(
            "mobile_phone",
            F.when(
                F.col("phone_digits").rlike(r"^66\d{9}$"),
                F.concat(F.lit("0"), F.substring(F.col("phone_digits"), 3, 9)),
            )
            .when(
                F.col("phone_digits").rlike(r"^0\d{9}$"),
                F.col("phone_digits"),
            )
            .otherwise(F.lit(None).cast("string")),
        )
        .drop("phone_digits")
        .withColumn(
            "source_channel",
            F.when(
                source_channel_raw.contains("facebook"),
                F.lit("facebook"),
            )
            .when(source_channel_raw.contains("google"), F.lit("google"))
            .when(source_channel_raw.contains("line"), F.lit("line"))
            .when(source_channel_raw.contains("webinar"), F.lit("webinar"))
            .when(source_channel_raw.contains("referral"), F.lit("referral"))
            .when(source_channel_raw.contains("tiktok"), F.lit("tiktok"))
            .when(source_channel_raw.contains("organic"), F.lit("organic"))
            .when(source_channel_raw.contains("school fair"), F.lit("school_fair")),
        )
        .filter(valid_student_code())
        .withColumn("lead_created_at", format_then_cast_timestamp("lead_created_at"))
        .withColumn("rn", F.row_number().over(latest_lead_window))
        .filter(F.col("rn") == 1)
        .drop("rn")
        .select(
            "student_code",
            "student_name",
            "mobile_phone",
            "school_name",
            "grade",
            "lead_created_at",
            "source_channel",
        )
    )
