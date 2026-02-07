import streamlit as st
import pandas as pd
import psycopg2



# ------------------------
# 🔗 เชื่อมต่อ PostgreSQL
# ------------------------
def connect_db():
    return psycopg2.connect(
        host="localhost",
        database="postgres",    # แก้ตามจริง
        user="postgres",        # แก้ตามจริง
        password="12935"        # แก้ตามจริง
    )

# ------------------------
# 🎨 ส่วนหัวเว็บแบบ Navbar (ใหม่)
# ------------------------
st.markdown("""
    <style>
    .navbar {
        background-color: #ffffff;
        padding: 12px 40px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        position: relative;
        top: 0;
        z-index: 1000;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .navbar-left {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .navbar-left h1 {
        color: #E63946;
        margin: 0;
        font-size: 24px;
        font-weight: 800;
    }
    .navbar-right {
        display: flex;
        align-items: center;
        gap: 30px;
        font-size: 16px;
        font-weight: 500;
    }
    .navbar-right a {
        color: black;
        text-decoration: none;
    }
    .navbar-right a:hover {
        color: #E63946;
    }
    .login-btn {
        background-color: #E63946;
        padding: 6px 16px;
        border-radius: 20px;
        color: white;
        text-decoration: none;
        font-weight: bold;
    }
    .login-btn:hover {
        background-color: #D62828;
    }

    /* ปรับความกว้างเนื้อหา */
    .block-container {
        padding-top: 0rem;
    }

    /* ปรับ h1 หน้าหลักให้แถวเดียว */
    h1.main-title {
        font-size: 30px;
        text-align: center;
        font-weight: 800;
        margin-top: 1rem;
        margin-bottom: 2rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    </style>

    <div class="navbar">
        <div class="navbar-left">
            <span style="font-size:28px;">🏡</span>
            <h1>Yak Me Ban</h1>
        </div>
        <div class="navbar-right">
            <a href="#">หน้าแรก</a>
            <a href="#">ค้นหาแบบบ้าน</a>
            <a href="#">คู่มือสร้างบ้าน</a>
            <a href="#">ติดต่อเรา</a>
            <a class="login-btn" href="#">Login</a>
        </div>
    </div>
""", unsafe_allow_html=True)

# ------------------------
# 🧠 ส่วนเลือกเงื่อนไข
# ------------------------
st.markdown('<h1 class="main-title">📋 โปรแกรมค้นหาแบบบ้านตามความต้องการ</h1>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    floor = st.radio("จำนวนชั้น", ["ทั้งหมด", "แบบบ้านชั้นเดียว", "แบบบ้านสองชั้น", "แบบบ้านสามชั้น"])
    bedrooms = st.slider("จำนวนห้องนอนขั้นต่ำ", 1, 6, 2)
    area = st.slider("พื้นที่ใช้สอยขั้นต่ำ (ตร.ม.)", 50, 400, 100, step=10)

with col2:
    bathrooms = st.slider("จำนวนห้องน้ำขั้นต่ำ", 1, 6, 1)

search = st.button("🔍 ค้นหาแบบบ้าน")

# ------------------------
# 📦 ดึงข้อมูลจากฐานข้อมูล
# ------------------------
if search:
    with connect_db() as conn:
        query = """
            SELECT * FROM home_plans
            WHERE (%s = 'ทั้งหมด' OR floor = %s)
            AND bedroom = %s
            AND bathroom = %s
            AND area >= %s
            ORDER BY area ASC
        """
        params = (floor, floor, bedrooms, bathrooms, area)
        df = pd.read_sql_query(query, conn, params=params)

    st.markdown(f"### 🏘️ พบแบบบ้านทั้งหมด {len(df)} แบบ")

    if len(df) == 0:
        st.warning("ไม่พบแบบบ้านที่ตรงกับความต้องการ ลองเปลี่ยนเงื่อนไขดูนะครับ")
    else:
        for i, row in df.iterrows():
            st.subheader(f"🏠 {row['name']}")
            st.write(f"- จำนวนชั้น: {row['floor']}")
            st.write(f"- ห้องนอน: {row['bedroom']} ห้อง")
            st.write(f"- ห้องน้ำ: {row['bathroom']} ห้อง")
            st.write(f"- พื้นที่ใช้สอย: {row['area']} ตร.ม.")

            # 💰 ราคา
            if pd.notna(row.get('price')) and row['price'] != "":
                st.write(f"💰 ราคาโดยประมาณ: {row['price']}")
            else:
                st.write("💰 ราคาโดยประมาณ: -")

            

            # 📄 ลิงก์ PDF แบบบ้าน
            if pd.notna(row.get('pdf_link')) and row['pdf_link'] != "":
                st.markdown(f"[📄 ดาวน์โหลดแบบบ้าน (PDF)]({row['pdf_link']})")

            st.markdown("---")

# streamlit run yak9.py