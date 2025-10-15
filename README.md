# 🧠 BigData E-commerce Project
## 📝 Giới thiệu
Dự án BigData E-commerce là một hệ thống phân tích và gợi ý sản phẩm dựa trên dữ liệu lớn, được xây dựng bằng các công nghệ trong hệ sinh thái Big Data.
Mục tiêu của dự án là khai thác hành vi người dùng thương mại điện tử để:
  -  Phân tích xu hướng mua sắm (theo danh mục, thương hiệu, loại sự kiện).
  -  Huấn luyện mô hình ALS (Alternating Least Squares) để gợi ý sản phẩm cá nhân hóa cho từng người dùng.
  -  Cung cấp giao diện trực quan bằng Streamlit Dashboard, giúp dễ dàng theo dõi, trình bày và đánh giá kết quả.


## 🏗️ Công nghệ sử dụng
| Thành phần                           | Công nghệ                     |
| ------------------------------------ | ----------------------------- |
| **Xử lý dữ liệu & Machine Learning** | Apache Spark (PySpark, MLlib) |
| **Lưu trữ & Quản lý dữ liệu**        | Hadoop HDFS                   |
| **Dashboard trực quan**              | Streamlit + Plotly            |
| **Ngôn ngữ lập trình**               | Python 3                      |
| **Triển khai & Môi trường**          | Docker, Docker Compose        |


## ⚙️ Quy trình hoạt động
### 1.Ingest & làm sạch dữ liệu:
Dữ liệu e-commerce (từ file ecommerce.csv) được nạp lên HDFS và xử lý bởi Spark.

### 2.Tổng hợp & phân tích (Aggregation):
Tạo các bảng thống kê như:
**    agg_by_cat — Tổng hợp theo danh mục.
    agg_by_brand — Tổng hợp theo thương hiệu.
    agg_by_type — Tổng hợp theo loại sự kiện.**

### 3.Huấn luyện mô hình ALS:
Sử dụng Spark MLlib để xây dựng hệ thống gợi ý sản phẩm cá nhân hóa cho từng user_id.

### 4.Hiển thị kết quả:
Kết quả Spark job được lưu tại data/outputs/.
Streamlit Dashboard đọc dữ liệu này để hiển thị biểu đồ, bảng và gợi ý.

## 🧰 Cấu trúc chính
bigdata-ecommerce-project/
├── dashboard/           # Ứng dụng Streamlit
├── data/                # Dữ liệu thô + đầu ra
├── spark_jobs/          # Mã xử lý Spark (ingest, train ALS, utils)
├── scripts/             # Script tiện ích (put_to_hdfs.sh, spark_submit.sh)
├── Dockerfile.spark     # Cấu hình image Spark Worker + numpy
├── docker-compose.yml   # Khởi chạy cluster Hadoop + Spark
├── requirements.txt     # Thư viện Python cho dashboard
└── README.md            # Tài liệu hướng dẫn


## 🚀 HƯỚNG DẪN CHẠY CỤM BIG DATA (HADOOP + SPARK + STREAMLIT)

### 1) Bring up the cluster
```bash
docker compose build spark-worker-1 spark-worker-2

docker compose up -d
```

### 2) Add sample CSV
Mẫu dữ liệu đã có sẵn tại:
 `data/raw/ecommerce_sample.csv`.

 Nếu muốn đẩy lên HDFS, chạy:
```bash
bash scripts/put_to_hdfs.sh
```

### 3) Run Spark jobs
```bash
bash scripts/spark_submit.sh ingest   # ingest + clean + parquet + aggregates
bash scripts/spark_submit.sh als      # train ALS model (recommendation)
```

Kết quả đầu ra sẽ xuất hiện tại: `data/outputs/` và trong HDFS: `hdfs:///warehouse/ecommerce/events_parquet`.

### 4) Run the dashboard
Cài thư viện cần thiết:
```bash
pip install -r requirements.txt
```
Sau đó khởi động dashboard:
```bash
streamlit run dashboard/app.py
```

