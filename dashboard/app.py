import streamlit as st
import pandas as pd
import glob, json, os
import plotly.express as px

# --- CONFIG ---
st.set_page_config(page_title="E-commerce BigData Dashboard", layout="wide")
st.title("📊 E-commerce Big Data Dashboard")

# --- Utility functions ---
@st.cache_data
def read_any_csv(path_pattern):
    files = glob.glob(path_pattern)
    if not files:
        return pd.DataFrame()
    for f in files:
        if f.endswith('.csv') or ("part-" in f):
            try:
                return pd.read_csv(f)
            except Exception as e:
                st.error(f"Lỗi đọc file {f}: {e}")
                return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data
def read_recommendations(path_pattern):
    files = glob.glob(path_pattern)
    recs = {}
    for f in files:
        if f.endswith('.json'):
            with open(f, 'r', encoding='utf-8') as jf:
                for line in jf:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        uid = str(obj["user_id"])
                        items = [(r["product_id"], r["rating"]) for r in obj["recommendations"]]
                        recs[uid] = items
                    except Exception as e:
                        st.warning(f"Lỗi đọc dòng trong {os.path.basename(f)}: {e}")
    return recs



# --- Base directory ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Paths ---
path_cat = os.path.join(BASE_DIR, "data/outputs/agg_by_cat/*.csv")
path_brand = os.path.join(BASE_DIR, "data/outputs/agg_by_brand/*.csv")
path_type = os.path.join(BASE_DIR, "data/outputs/agg_by_type/*.csv")
path_recs = os.path.join(BASE_DIR, "data/outputs/user_recommendations/*.json")

# --- Buttons ---
if st.button("🔁 Reload Data"):
    st.cache_data.clear()
    st.experimental_rerun()

# --- Load data ---
by_cat = read_any_csv(path_cat)
by_brand = read_any_csv(path_brand)
by_type = read_any_csv(path_type)
user_recs = read_recommendations(path_recs)

# --- Show summary tables ---
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("📦 Events by Category")
    if not by_cat.empty:
        st.dataframe(by_cat.head(10))
    else:
        st.warning("Không có dữ liệu danh mục.")

with c2:
    st.subheader("🏷️ Events by Brand")
    if not by_brand.empty:
        st.dataframe(by_brand.head(10))
    else:
        st.warning("Không có dữ liệu thương hiệu.")

with c3:
    st.subheader("⚙️ Events by Type")
    if not by_type.empty:
        st.dataframe(by_type.head(10))
    else:
        st.warning("Không có dữ liệu loại sự kiện.")

st.markdown("---")

# --- Charts ---
st.header("📊 Phân tích xu hướng mua sắm")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    if not by_cat.empty:
        cat_col = "cat_l1"  # tên cột thật
        fig1 = px.bar(by_cat, x=cat_col, y=by_cat.columns[-1], title="Top danh mục mua sắm")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.warning("Không có dữ liệu danh mục để hiển thị.")

with chart_col2:
    if not by_brand.empty and 'brand' in by_brand.columns:
        fig2 = px.bar(by_brand.head(10), x='brand', y=by_brand.columns[-1], title="Top thương hiệu phổ biến")
        st.plotly_chart(fig2, use_container_width=True)
    elif not by_brand.empty:
        st.info("Không tìm thấy cột 'brand' trong dữ liệu thương hiệu.")

if not by_type.empty and 'event_type' in by_type.columns:
    fig3 = px.pie(by_type, names='event_type', values=by_type.columns[-1], title="Tỷ lệ loại sự kiện")
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# --- Product Recommendation Section ---
st.header("🧠 Gợi ý sản phẩm cá nhân hóa")

if not user_recs:
    st.warning("⚠️ Chưa có file gợi ý người dùng. Hãy chạy Spark job train_als.py trước.")
else:
    # --- Chọn hoặc nhập user ID ---
    st.subheader("Chọn hoặc nhập User ID")
    st.info("Chọn nhanh một user có sẵn hoặc nhập User ID khác để xem gợi ý sản phẩm.")
    # Lấy danh sách user có trong file JSON (chỉ lấy 10 user đầu để demo)
    user_ids = list(user_recs.keys())
    user_samples = user_ids[:10] if len(user_ids) > 10 else user_ids

    col1, col2 = st.columns([1, 1.5])
    with col1:
        selected_user = st.selectbox("🔽 User ID mẫu (chọn để xem nhanh):", user_samples)
    with col2:
        manual_user = st.text_input("✍️ Hoặc nhập User ID thủ công:")

    # Ưu tiên user nhập tay (nếu có)
    user_id = manual_user.strip() if manual_user else selected_user
    if user_id:
        # Hỗ trợ cả key dạng string hoặc int
        recs = user_recs.get(user_id) or user_recs.get(int(user_id)) if user_id.isdigit() else None

    if recs:
        # Làm sạch dữ liệu
        clean_recs = []
        for item in recs:
            if isinstance(item, dict):
                clean_recs.append((str(item.get("product_id")), float(item.get("rating", 0))))
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                clean_recs.append((str(item[0]), float(item[1])))
        df_recs = pd.DataFrame(clean_recs, columns=["product_id", "score"])

        # Ép kiểu rõ ràng
        df_recs["product_id"] = df_recs["product_id"].astype(str)  # 🔥 ép sang chuỗi để Plotly hiểu là CATEGORICAL
        df_recs["score"] = df_recs["score"].astype(float)

        # Tạo thêm cột tên sản phẩm hiển thị đẹp hơn
        df_recs["product_label"] = "Product " + df_recs["product_id"]

        st.success(f"🎯 Gợi ý sản phẩm cho User `{user_id}`")
        st.dataframe(df_recs)

        # Vẽ biểu đồ
        if df_recs["score"].notnull().any():
            st.subheader(f"Top gợi ý cho User {user_id}")
            fig = px.bar(
                df_recs.head(10),
                x="product_label",  # 👉 dùng label chuỗi, không dùng số
                y="score",
                text="score",
                title=f"Top sản phẩm được gợi ý cho User {user_id}",
            )
            fig.update_traces(
                texttemplate="%{text:.3f}",
                textposition="outside",
                marker_color="skyblue"
            )
            fig.update_layout(
                xaxis_title="Mã sản phẩm",
                yaxis_title="Điểm gợi ý (score)",
                height=500,
                bargap=0.3,
                margin=dict(t=80, b=100),
                xaxis=dict(type="category")  # 🔥 ép trục X thành dạng phân loại
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Không có giá trị hợp lệ để vẽ biểu đồ.")


    else:
        st.info("Nhập user_id để xem gợi ý.")

st.markdown("---")
st.caption("© 2025 - E-commerce Big Data Project | Spark + Streamlit + Docker")
