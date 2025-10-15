from pyspark.sql import SparkSession # type: ignore
from pyspark.ml.recommendation import ALS # type: ignore
from pyspark.ml.evaluation import RegressionEvaluator# type: ignore
from utils import SCHEMA, normalize
from pyspark.sql import functions as F # type: ignore


HDFS_RAW = "hdfs://namenode:9000/data/raw/ecommerce.csv"


spark = (
    SparkSession.builder
    .appName("als_recommender_optimized")
    .config("spark.sql.shuffle.partitions", "200") # moderate parallelism
    .getOrCreate()  
    )


try:
    df = spark.read.csv(HDFS_RAW, header=True, schema=SCHEMA)
except Exception:
    df = spark.read.csv("/data/raw/ecommerce.csv", header=True, schema=SCHEMA)


clean = normalize(df)


# Aggregate implicit feedback (number of interactions per user-item)
ratings = (
clean.groupBy("user_id", "product_id")
.agg(F.count(F.lit(1)).alias("events"))
.withColumn("rating", F.col("events").cast("double"))
.select(F.col("user_id").cast("int"), F.col("product_id").cast("int"), F.col("rating"))
.na.drop()
)


train, test = ratings.randomSplit([0.9, 0.1], seed=42)


# ⚙️ Optimized ALS config for local / Docker Desktop (~5GB dataset)
als = ALS(
userCol="user_id",
itemCol="product_id",
ratingCol="rating",
implicitPrefs=True,
nonnegative=True,
coldStartStrategy="drop",
rank=32, # fewer latent factors
maxIter=6, # fewer training iterations
regParam=0.1, # stronger regularization
alpha=20.0 # lower confidence
)


model = als.fit(train)


# Optional evaluation (skip if large dataset)
try:
    pred = model.transform(test)
    rmse = RegressionEvaluator(metricName="rmse", labelCol="rating", predictionCol="prediction").evaluate(pred)
    print(f"RMSE: {rmse:.4f}")
except Exception:
    print("Skip RMSE evaluation on large dataset.")


# Save recommendations
model.recommendForAllUsers(10).write.mode("overwrite").json("/data/outputs/user_recommendations")


print("✅ ALS training completed (optimized version).")