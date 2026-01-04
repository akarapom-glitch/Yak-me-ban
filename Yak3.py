import streamlit as st
import pandas as pd
import psycopg2

# ------------------------
# 🔗 เชื่อมต่อ PostgreSQL
# ------------------------
def connect_db():
    return psycopg2.connect(
        host="localhost",
        database="postgres",  # เปลี่ยนชื่อ database ตามของคุณ
        user="postgres",      # เปลี่ยน user
        password="12935"      # เปลี่ยนรหัสผ่าน
    )

# ------------------------
# 🌐 UI สำหรับกรอกเงื่อนไข
# ------------------------
st.set_page_config(page_title="Yak Me Ban", layout="centered")

# แถบหัวเว็บ
st.markdown("""
    <div style="background-color:tomato;padding:15px;border-radius:8px;">
        <h1 style="color:white;text-align:center;">🏡 YAK ME BAN</h1>
    </div>
""", unsafe_allow_html=True)

st.markdown("## 📋 โปรแกรมค้นหาแบบบ้านตามความต้องการ")

col1, col2 = st.columns(2)
with col1:
    floor = st.radio("จำนวนชั้น", ["ทั้งหมด", "แบบบ้านชั้นเดียว", "แบบบ้านสองชั้น", "แบบบ้านสามชั้น"])
    bedrooms = st.slider("จำนวนห้องนอน", 1, 6, 2)
    area = st.slider("พื้นที่ใช้สอยขั้นต่ำ (ตร.ม.)", 50, 400, 100, step=10)

with col2:
    bathrooms = st.slider("จำนวนห้องน้ำ", 1, 6, 1)

search = st.button("🔍 ค้นหาแบบบ้าน")

# ------------------------
# 📦 Query จากฐานข้อมูล
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
        params = (
            floor, floor,
            bedrooms,
            bathrooms,
            area
        )
        df = pd.read_sql_query(query, conn, params=params)

    st.markdown(f"### 🔎 พบทั้งหมด {len(df)} แบบบ้าน")

    if len(df) == 0:
        st.warning("ไม่พบแบบบ้านที่ตรงกับความต้องการ ลองเปลี่ยนเงื่อนไขดูนะครับ")
    else:
        for i, row in df.iterrows():
            st.subheader(f"🏠 {row['name']}")
            st.write(f"- แบบบ้าน: {row['floor']}")
            st.write(f"- ห้องนอน: {row['bedroom']} ห้อง")
            st.write(f"- ห้องน้ำ: {row['bathroom']} ห้อง")
            st.write(f"- พื้นที่ใช้สอย: {row['area']} ตร.ม.")

            # 💰 ราคาหรือ PDF ราคาบ้าน
            price_value = row.get('price', "")
            if pd.notna(price_value) and str(price_value).startswith("http"):
                st.markdown(f"[💰 ดูรายละเอียดราคา (PDF)]({price_value})")
            else:
                price_display = price_value if pd.notna(price_value) and str(price_value).strip() != "" else "-"
                st.write(f"💰 ราคาโดยประมาณ: {price_display}")

            # 📝 ลิงก์ PDF แบบบ้าน
            if pd.notna(row.get('pdf_link')) and row['pdf_link'] != "":
                st.markdown(f"[📄 ดาวน์โหลดแบบบ้าน (PDF)]({row['pdf_link']})")

            # 🖼️ รูปภาพบ้าน (หากมี)
            #if pd.notna(row.get('image_link')) and row['image_link'] != "":
             #   st.image(row['image_link'], width=400)

            st.markdown("---")



            # streamlit run yak3.py เปิดเว็บ
