import streamlit as st
import pandas as pd
import psycopg2

# ------------------------
# 🔗 เชื่อมต่อ PostgreSQL
# ------------------------
def connect_db():
    return psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="12935"
    )

# ------------------------
# 🎨 ตั้งค่า UI
# ------------------------
st.set_page_config(page_title="Yak Me Ban", layout="wide")

# ------------------------
# 🔝 แถบบนสุดแบบ DDproperty style
# ------------------------
st.markdown(
    """
    <style>
        .top-bar {
            background-color: white;
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .top-left {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 22px;
            font-weight: bold;
            color: #e63946;
        }
        .top-menu {
            display: flex;
            gap: 40px;
            font-size: 16px;
        }
        .top-menu a {
            text-decoration: none;
            color: black;
        }
        .login-btn {
            background-color: #e63946;
            border: none;
            padding: 6px 18px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }
    </style>

    <div class="top-bar">
        <div class="top-left">
            <span>🏠</span><span>Yak Me Ban</span>
        </div>
        <div class="top-menu">
            <a href="#">หน้าแรก</a>
            <a href="#">ค้นหาแบบบ้าน</a>
            <a href="#">คู่มือสร้างบ้าน</a>
            <a href="#">ติดต่อเรา</a>
            <button class="login-btn">Login</button>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ------------------------
# 📋 ชื่อโปรแกรมหลัก
# ------------------------
st.markdown("## 📝 โปรแกรมค้นหาแบบบ้านตามความต้องการ")

# ------------------------
# 🌐 เงื่อนไขการค้นหา
# ------------------------
col1, col2 = st.columns(2)

with col1:
    floor = st.radio("จำนวนชั้น", ["ทั้งหมด", "แบบบ้านชั้นเดียว", "แบบบ้านสองชั้น", "แบบบ้านสามชั้น"])
    bedrooms = st.number_input("จำนวนห้องนอน ", min_value=1, max_value=10, step=1, value=2)
    area = st.number_input("พื้นที่ใช้สอยขั้นต่ำ (ตร.ม.)", min_value=20, max_value=400, step=10, value=100)

with col2:
    bathrooms = st.number_input("จำนวนห้องน้ำ ", min_value=1, max_value=12, step=1, value=1)

search = st.button("🔍 ค้นหาแบบบ้าน")

# ------------------------
# 🧠 Query ข้อมูลจากฐาน
# ------------------------
if search:
    with connect_db() as conn:
        query = """
            SELECT * FROM home_plans
            WHERE (%s = 'ทั้งหมด' OR floor = %s)
            AND bedroom = %s
            AND bathroom = %s
            AND area >= %s
            ORDER BY bedroom DESC, area ASC
        """
        params = (floor, floor, bedrooms, bathrooms, area)
        df = pd.read_sql_query(query, conn, params=params)

    st.markdown(f"### 📋 พบทั้งหมด {len(df)} แบบบ้าน")

    if len(df) == 0:
        st.warning("ไม่พบแบบบ้านที่ตรงกับความต้องการ ลองเปลี่ยนเงื่อนไขดูนะครับ")
    else:
        for i, row in df.iterrows():
            st.subheader(f"🏡 {row['name']}")
            st.write(f"- ชั้น: {row['floor']}")
            st.write(f"- ห้องนอน: {row['bedroom']} ห้อง")
            st.write(f"- ห้องน้ำ: {row['bathroom']} ห้อง")
            st.write(f"- พื้นที่ใช้สอย: {row['area']} ตร.ม.")
            st.write(f"💰 ราคาโดยประมาณ: {row['price'] if pd.notna(row['price']) else '-'}")
            
            # ลิงก์ PDF แบบบ้าน
            if pd.notna(row.get('pdf_link')) and row['pdf_link'].strip() != "":
                st.markdown(f"[📄 ดาวน์โหลดแบบบ้าน (PDF)]({row['pdf_link']})")

            

            st.markdown("---")



# streamlit run yak4.py เปิดเว็บ