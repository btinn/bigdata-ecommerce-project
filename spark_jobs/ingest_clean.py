from pyspark.sql import SparkSession # type: ignore
from pyspark.sql import functions as F # type: ignore
from utils import SCHEMA, normalize 

INPUT_LOCAL = "/data/raw/ecommerce.csv"
HDFS_RAW = "hdfs://namenode:9000/data/raw/ecommerce.csv"
HDFS_PARQUET = "hdfs://namenode:9000/warehouse/ecommerce/events_parquet"
LOCAL_OUT = "/data/outputs"

spark = (
    SparkSession.builder
        .appName("ingest_clean_ecommerce")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
)

# Prefer HDFS if available
try:
    df = spark.read.csv(HDFS_RAW, header=True, schema=SCHEMA)
except Exception:
    df = spark.read.csv(INPUT_LOCAL, header=True, schema=SCHEMA)

clean = normalize(df)

# Write partitioned parquet
(clean.write.mode("overwrite")
      .partitionBy("date")
      .parquet(HDFS_PARQUET))

# Simple aggregations for quick dashboard
agg_by_cat = (clean.groupBy("cat_l1").agg(F.count(F.lit(1)).alias("events"))
                     .orderBy(F.desc("events")))
agg_by_brand = (clean.groupBy("brand").agg(F.count(F.lit(1)).alias("events"))
                       .orderBy(F.desc("events")))
agg_by_type = (clean.groupBy("event_type").agg(F.count(F.lit(1)).alias("events")))

agg_by_cat.coalesce(1).write.mode("overwrite").option("header", True).csv(f"{LOCAL_OUT}/agg_by_cat")
agg_by_brand.coalesce(1).write.mode("overwrite").option("header", True).csv(f"{LOCAL_OUT}/agg_by_brand")
agg_by_type.coalesce(1).write.mode("overwrite").option("header", True).csv(f"{LOCAL_OUT}/agg_by_type")

print("Ingest + clean completed.")
