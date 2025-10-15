#!/usr/bin/env bash
set -euo pipefail
# Copy local sample to HDFS path /data/raw/
docker exec -i namenode bash -lc "hdfs dfs -mkdir -p /data/raw && hdfs dfs -put -f /data/raw/ecommerce.csv /data/raw/"
echo "Pushed /data/raw/ecommerce_sample.csv to hdfs:///data/raw/"
