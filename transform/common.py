from pyspark.sql import Column
from pyspark.sql import functions as F

STUDENT_CODE_REGEX = r"^STU\d{6}$"
ORDER_ID_REGEX = r"^ORD\d{9}$"


def normalized_student_code(column_name: str = "student_code") -> Column:
    return F.trim(F.col(column_name))


def normalized_order_id(column_name: str = "order_id") -> Column:
    return F.trim(F.col(column_name))


def valid_student_code(column_name: str = "student_code") -> Column:
    return F.col(column_name).isNotNull() & F.col(column_name).rlike(STUDENT_CODE_REGEX)


def valid_order_id(column_name: str = "order_id") -> Column:
    return F.col(column_name).isNotNull() & F.col(column_name).rlike(ORDER_ID_REGEX)


def standardized_timestamp_string(
    column_name: str,
    slash_pattern: str = "dd/MM/yyyy HH:mm",
) -> Column:
    value = F.trim(F.col(column_name))
    standard_ts = F.try_to_timestamp(value, F.lit("yyyy-MM-dd HH:mm:ss"))
    slash_ts = F.try_to_timestamp(value, F.lit(slash_pattern))
    return (
        F.when(
            standard_ts.isNotNull(),
            F.date_format(standard_ts, "yyyy-MM-dd HH:mm:ss"),
        )
        .when(
            slash_ts.isNotNull(),
            F.date_format(slash_ts, "yyyy-MM-dd HH:mm:ss"),
        )
        .otherwise(F.lit(None).cast("string"))
    )


def format_then_cast_timestamp(
    column_name: str,
    slash_pattern: str = "dd/MM/yyyy HH:mm",
) -> Column:
    return standardized_timestamp_string(
        column_name,
        slash_pattern=slash_pattern,
    ).cast("timestamp")


def try_double(column_name: str) -> Column:
    return F.expr(f"try_cast(`{column_name}` as double)")


def try_int(column_name: str) -> Column:
    return F.expr(f"try_cast(`{column_name}` as int)")
