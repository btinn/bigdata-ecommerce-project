from pyspark.sql.types import StructType, StructField, StringType # type: ignore
from pyspark.sql import functions as F # type: ignore

SCHEMA = StructType([
    StructField("event_time", StringType(), True),
    StructField("event_type", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("category_id", StringType(), True),  # scientific notation → keep as string then cast
    StructField("category_code", StringType(), True),
    StructField("brand", StringType(), True),
    StructField("price", StringType(), True),
    StructField("user_id", StringType(), True),
    StructField("user_session", StringType(), True),
])

def normalize(df):
    # Trim & standardize empty brand to null
    df = df.withColumn("brand",
        F.when(F.length(F.trim(F.col("brand"))) == 0, None).otherwise(F.col("brand"))
    )
    # Parse timestamp (drop ' UTC')
    df = df.withColumn("event_ts",
        F.to_timestamp(F.regexp_replace("event_time", " UTC$", ""), "yyyy-MM-dd HH:mm:ss")
    )
    # Cast numeric fields safely
    df = (df
        .withColumn("price", F.col("price").cast("double"))
        .withColumn("product_id", F.col("product_id").cast("long"))
        .withColumn("user_id", F.col("user_id").cast("long"))
        # Keep original category_id + a long string representation, avoiding float rounding
        .withColumn("category_id_long", F.col("category_id").cast("decimal(38,0)").cast("string"))
        .withColumn("date", F.to_date("event_ts"))
        .withColumn("hour", F.hour("event_ts"))
    )
    # Split category levels
    for i in range(3):
        df = df.withColumn(f"cat_l{i+1}", F.split(F.col("category_code"), "\\.").getItem(i))
    cols = [
        "event_ts","event_type","product_id","category_id","category_id_long","category_code",
        "cat_l1","cat_l2","cat_l3","brand","price","user_id","user_session","date","hour"
    ]
    return df.select(*cols)
