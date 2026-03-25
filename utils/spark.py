import os

for env_name in ("SPARK_HOME", "HADOOP_CONF_DIR", "SPARK_CONF_DIR"):
    os.environ.pop(env_name, None)

from pyspark.sql import SparkSession


def create_local_spark_session(app_name: str) -> SparkSession:
    return (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.hadoop.fs.defaultFS", "file:///")
        .getOrCreate()
    )
