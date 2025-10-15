#!/usr/bin/env bash
set -euo pipefail

case ${1:-} in
  ingest)
    docker exec -it spark-master /spark/bin/spark-submit \
      --master spark://spark-master:7077 \
      --driver-memory 2G \
      --executor-memory 2G \
      --executor-cores 2 \
      /opt/spark_jobs/ingest_clean.py
    ;;
  als)
    docker exec -it spark-master /spark/bin/spark-submit \
      --master spark://spark-master:7077 \
      --driver-memory 2G \
      --executor-memory 2G \
      --executor-cores 2 \
      /opt/spark_jobs/train_als.py
    ;;
  *)
    echo "Usage: scripts/spark_submit.sh [ingest|als]"; exit 1 ;;
 esac
