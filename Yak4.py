import streamlit as st
import pandas as pd
import psycopg2


# ------------------------
# 🔗 เชื่อมต่อ Supabase PostgreSQL
# ------------------------
def connect_db():
    return psycopg2.connect(
        "postgresql://postgres.nxevtwnbbeeacrypmpnx:akarapom24899@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
    )

# ------------------------
# 🎨 ตั้งค่า UI
# ------------------------
st.set_page_config(
    page_title="Yak Me Ban",
    layout="wide"
)

# ------------------------
# 🔝 แถบบน (Header)
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
            gap: 30px;
            font-size: 16px;
        }
        .top-menu a {
            text-decoration: none;
            color: black;
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
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("## 📝 โปรแกรมค้นหาแบบบ้านตามความต้องการ")

# ------------------------
# 🌐 เงื่อนไขการค้นหา
# ------------------------
col1, col2 = st.columns(2)

with col1:
    floor = st.radio(
        "จำนวนชั้น",
        ["ทั้งหมด", "แบบบ้านชั้นเดียว", "แบบบ้านสองชั้น", "แบบบ้านสามชั้น"]
    )
    bedrooms = st.number_input(
        "จำนวนห้องนอน",
        min_value=1, max_value=10, step=1, value=2
    )
    area = st.number_input(
        "พื้นที่ใช้สอยขั้นต่ำ (ตร.ม.)",
        min_value=20, max_value=500, step=10, value=100
    )

with col2:
    bathrooms = st.number_input(
        "จำนวนห้องน้ำ",
        min_value=1, max_value=10, step=1, value=1
    )

search = st.button("🔍 ค้นหาแบบบ้าน")

# ------------------------
# 🧠 Query ข้อมูลจาก Supabase
# ------------------------
if search:

    with connect_db() as conn:
        query = """
            SELECT * FROM home_plan
            WHERE (%s = 'ทั้งหมด' OR floor = %s)
            AND bedroom = %s
            AND bathroom = %s
            AND area >= %s
            ORDER BY bedroom DESC, area ASC
        """
        params = (floor, floor, bedrooms, bathrooms, area)
        df = pd.read_sql_query(query, conn, params=params)

    try:
        with connect_db() as conn:
            query = """
                SELECT *
                FROM Public.home_plans
                WHERE (%s = 'ทั้งหมด' OR floor = %s)
                  AND bedroom = %s
                  AND bathroom = %s
                  AND area >= %s
                ORDER BY area ASC
            """
            params = (
                floor,
                floor,
                bedrooms,
                bathrooms,
                area
            )

            df = pd.read_sql_query(query, conn, params=params)

        st.markdown(f"### 📋 พบทั้งหมด {len(df)} แบบบ้าน")

        if df.empty:
            st.warning("ไม่พบแบบบ้านที่ตรงกับความต้องการ ลองเปลี่ยนเงื่อนไขดูนะครับ")
        else:
            for _, row in df.iterrows():
                st.subheader(f"🏡 {row['name']}")
                st.write(f"- ชั้น: {row['floor']}")
                st.write(f"- ห้องนอน: {row['bedroom']} ห้อง")
                st.write(f"- ห้องน้ำ: {row['bathroom']} ห้อง")
                st.write(f"- พื้นที่ใช้สอย: {row['area']} ตร.ม.")

                if 'price' in row and pd.notna(row['price']):
                    st.write(f"💰 ราคาโดยประมาณ: {row['price']}")

                if 'pdf_link' in row and pd.notna(row['pdf_link']) and row['pdf_link'] != "":
                    st.markdown(f"[📄 ดาวน์โหลดแบบบ้าน (PDF)]({row['pdf_link']})")

                st.markdown("---")

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")


# streamlit run yak4.py เปิดเว็บ

# ------------------------
# 🔌 ตรวจสอบการเชื่อมต่อ (Debug ใช้ตอนพรีเซนต์ได้)
# ------------------------
with st.expander("🔧 ตรวจสอบการเชื่อมต่อฐานข้อมูล"):
    try:
        conn = connect_db()
        conn.close()
        st.success("✅ เชื่อมต่อ Supabase PostgreSQL สำเร็จ")
    except Exception as e:
        st.error(f"❌ เชื่อมต่อไม่สำเร็จ: {e}")

# streamlit run yak4.py