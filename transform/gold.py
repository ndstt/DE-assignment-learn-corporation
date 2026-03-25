from __future__ import annotations

from datetime import timedelta

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def build_engagement_gold(learning_silver_df: DataFrame) -> tuple[DataFrame, object]:
    reference_ts = learning_silver_df.select(F.max("event_time")).first()[0]
    before_7d = reference_ts - timedelta(days=7)
    before_30d = reference_ts - timedelta(days=30)

    engagement_df = learning_silver_df.groupBy("student_code").agg(
        F.count("*").alias("total_learning_events"),
        F.sum("duration_minutes").alias("total_learning_minutes"),
        F.sum(
            F.when(
                (F.col("event_time") <= F.lit(reference_ts))
                & (F.col("event_time") > F.lit(before_7d)),
                1,
            ).otherwise(0)
        ).alias("events_last_7d"),
        F.sum(
            F.when(
                (F.col("event_time") <= F.lit(reference_ts))
                & (F.col("event_time") > F.lit(before_30d)),
                1,
            ).otherwise(0)
        ).alias("events_last_30d"),
        F.sum(
            F.when(F.col("event_name") == "quiz_submit", 1).otherwise(0)
        ).alias("quiz_submit_events"),
    )

    return engagement_df, reference_ts


def build_revenue_gold(sales_silver_df: DataFrame) -> DataFrame:
    return (
        sales_silver_df.filter(F.col("product_type") != F.lit("trial_course"))
        .groupBy("student_code")
        .agg(
            F.count("*").alias("total_paid_orders"),
            F.sum(F.col("amount")).alias("total_revenue"),
            F.min(F.col("order_date")).alias("first_purchase_at"),
            F.max(F.col("order_date")).alias("last_purchase_at"),
        )
    )


def transform_student_360_gold(
    leads_silver_df: DataFrame,
    learning_silver_df: DataFrame,
    sales_silver_df: DataFrame,
) -> DataFrame:
    engagement_df, reference_ts = build_engagement_gold(learning_silver_df)
    revenue_df = build_revenue_gold(sales_silver_df)

    return (
        leads_silver_df.alias("l")
        .join(engagement_df, on="student_code", how="left")
        .join(revenue_df, on="student_code", how="left")
        .fillna(
            {
                "total_learning_events": 0,
                "total_learning_minutes": 0,
                "events_last_7d": 0,
                "events_last_30d": 0,
                "quiz_submit_events": 0,
                "total_paid_orders": 0,
                "total_revenue": 0,
            }
        )
        .withColumn(
            "engagement_segment",
            F.when(
                (F.col("events_last_7d") >= F.lit(5))
                & (F.col("events_last_30d") >= F.lit(12)),
                F.lit("high"),
            )
            .when(
                (F.col("events_last_7d") >= F.lit(2))
                & (F.col("events_last_30d") >= F.lit(5)),
                F.lit("medium"),
            )
            .when(
                (F.col("events_last_7d") >= F.lit(0))
                & (F.col("events_last_30d") > F.lit(0)),
                F.lit("low"),
            )
            .when(F.col("events_last_30d") == F.lit(0), F.lit("inactive"))
        )
        .withColumn(
            "is_paying_student",
            F.when(F.col("total_paid_orders") > 0, F.lit(True)).otherwise(
                F.lit(False)
            ),
        )
        .withColumn(
            "lead_age_days",
            F.datediff(F.lit(reference_ts), F.col("lead_created_at")),
        )
        .withColumn(
            "risk_flag",
            F.when(
                (F.col("engagement_segment") == F.lit("inactive"))
                & (F.col("lead_age_days") >= F.lit(30)),
                F.lit(True),
            )
            .when(
                (F.col("engagement_segment") == F.lit("low"))
                & (F.col("lead_age_days") >= F.lit(60)),
                F.lit(True),
            )
            .otherwise(F.lit(False)),
        )
        .withColumn(
            "lead_priority_score",
            F.lit(0)
            + F.when(F.col("engagement_segment") == "high", 30)
            .when(F.col("engagement_segment") == "medium", 20)
            .when(F.col("engagement_segment") == "low", 10)
            .otherwise(0)
            + F.when(F.col("events_last_7d") >= 3, 10)
            .when(F.col("events_last_7d") >= 1, 5)
            .otherwise(0)
            + F.when(F.col("total_learning_minutes") >= 180, 10)
            .when(F.col("total_learning_minutes") >= 60, 5)
            .otherwise(0)
            + F.when(F.col("quiz_submit_events") >= 3, 10)
            .when(F.col("quiz_submit_events") >= 1, 5)
            .otherwise(0)
            + F.when(F.col("risk_flag") == True, 20).otherwise(0)
            + F.when(F.col("is_paying_student") == False, 10).otherwise(0)
            + F.when(F.col("total_revenue") >= 3000, 10)
            .when(F.col("total_revenue") >= 1000, 5)
            .otherwise(0)
            + F.when(F.col("lead_age_days") <= 30, 5).otherwise(0),
        )
        .withColumn(
            "lead_priority_band",
            F.when(
                F.col("lead_priority_score") >= 70,
                F.lit("immediate_action"),
            )
            .when(F.col("lead_priority_score") >= 45, F.lit("follow_up"))
            .when(F.col("lead_priority_score") >= 20, F.lit("monitor"))
            .otherwise(F.lit("low_priority")),
        )
    )
