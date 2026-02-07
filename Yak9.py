import streamlit as st
import pandas as pd
import psycopg2
import requests
from io import BytesIO


# =====================================================
# 🔗 เชื่อมต่อ Supabase PostgreSQL
# =====================================================
def connect_db():
    return psycopg2.connect(
        "postgresql://postgres.nxevtwnbbeeacrypmpnx:akarapom24899@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
    )

# =====================================================
# 🧠 Session State
# =====================================================
if "search_result" not in st.session_state:
    st.session_state.search_result = None

if "house_1" not in st.session_state:
    st.session_state.house_1 = "— กรุณาเลือก —"

if "house_2" not in st.session_state:
    st.session_state.house_2 = "— กรุณาเลือก —"

if "show_compare" not in st.session_state:
    st.session_state.show_compare = False

if "show_compare_ui" not in st.session_state:
    st.session_state.show_compare_ui = False

# =====================================================
# 🎨 ตั้งค่า UI
# =====================================================
st.set_page_config(page_title="Yak Me Ban", layout="wide")

# =====================================================
# 🔝 Header
# =====================================================
st.markdown(
    """
    <style>
        /* ===== กล่อง Header ด้านบน ===== */
        .top-bar {
            background-color: white;          /* สีพื้นหลังกล่อง */
            padding: 24px 48px;               /* ระยะขอบด้านใน */
            display: flex;
            align-items: center;

            border-radius: 14px;              /* มุมโค้ง */
            
            /* 🔸 กรอบ */
            border: 2px solid #e63946;        /* สี + ความหนากรอบ */

            /* 🔸 เงา */
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);

            margin-bottom: 28px;
        }

        /* ===== กลุ่มโลโก้ + ชื่อเว็บ ===== */
        .top-left {
            display: flex;
            align-items: center;
            gap: 14px;

            font-size: 30px;                  /* 🔹 ขนาดตัวอักษร */
            font-weight: 700;                 /* ความหนา */
            color: #e63946;                   /* สีตัวอักษร */
        }

        /* ===== ไอคอนบ้าน ===== */
        .top-left span:first-child {
            font-size: 30px;                  /* 🔹 ขนาดไอคอน */
        }
    </style>

    <div class="top-bar">
        <div class="top-left">
            <span>🏠</span>
            <span>Yak Me Ban</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown("## 📝 โปรแกรมค้นหาแบบบ้านตามความต้องการ")


# =====================================================
# 🌐 เงื่อนไขการค้นหา (จัด Layout ใหม่ + Reset)
# =====================================================
left_col, right_col = st.columns([1, 1])

# -------------------------
# 🔹 ฝั่งซ้าย : ตัวเลือกประเภท
# -------------------------
with left_col:
    floor = st.radio(
        "จำนวนชั้น",
        ["ทั้งหมด", "แบบบ้านชั้นเดียว", "แบบบ้านสองชั้น", "แบบบ้านสามชั้น"],
        key="floor_filter"
    )

# -------------------------
# 🔹 ฝั่งขวา : ตัวเลขทั้งหมด
# -------------------------
with right_col:
    bedrooms = st.number_input(
        "จำนวนห้องนอน",
        min_value=1,
        max_value=10,
        value=2,
        key="bedrooms_filter"
    )

    bathrooms = st.number_input(
        "จำนวนห้องน้ำ",
        min_value=1,
        max_value=10,
        value=1,
        key="bathrooms_filter"
    )

    area = st.number_input(
        "พื้นที่ใช้สอยขั้นต่ำ (ตร.ม.)",
        min_value=20,
        max_value=500,
        value=100,
        step=10,
        key="area_filter"
    )

# -------------------------
# 🔘 ปุ่มค้นหา + รีเซ็ต
# -------------------------
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    search = st.button("🔍 ค้นหาแบบบ้าน")


if st.button("🔄 รีเซตผลการค้นหา"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()



# =====================================================
# 🔎 Query ข้อมูล
# =====================================================
if search:
    try:
        with connect_db() as conn:
            query = """
                SELECT *
                FROM home_plans
                WHERE (%s = 'ทั้งหมด' OR floor = %s)
                  AND bedroom = %s
                  AND bathroom = %s
                  AND area >= %s
                ORDER BY area ASC
            """
            params = (floor, floor, bedrooms, bathrooms, area)
            df = pd.read_sql_query(query, conn, params=params)

        st.session_state.search_result = df
        st.session_state.show_compare = False
        st.session_state.show_compare_ui = False

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")

# =====================================================
# 📦 แสดงผลลัพธ์
# =====================================================
df = st.session_state.search_result

if df is not None and not df.empty:

    st.markdown(f"## 📋 พบทั้งหมด {len(df)} แบบบ้าน")

    # =================================================
    # 📊 โหมดเปรียบเทียบ (กดก่อนค่อยแสดง)
    # =================================================
    #st.markdown("## 📊 เปรียบเทียบแบบบ้าน")

    if not st.session_state.show_compare_ui:
        if st.button("📊 เปิดโหมดเปรียบเทียบแบบบ้าน"):
            st.session_state.show_compare_ui = True
            st.rerun()

    if st.session_state.show_compare_ui:

        house_names = df["name"].tolist()

        st.markdown("### 🔍 เลือกแบบบ้านเพื่อเปรียบเทียบ")

        colA, colB = st.columns(2)

        with colA:
            st.selectbox(
                "แบบบ้านที่ 1",
                ["— กรุณาเลือก —"] + house_names,
                key="house_1"
            )

        with colB:
            st.selectbox(
                "แบบบ้านที่ 2",
                ["— กรุณาเลือก —"] + house_names,
                key="house_2"
            )

        col_btn1, col_btn2, col_btn3 = st.columns(3)

        with col_btn1:
            compare = st.button("📊 เปรียบเทียบ")

        with col_btn2:
            reset = st.button("🔄 Reset")

        with col_btn3:
            close = st.button("❌ ปิดโหมด")

        if reset:
            st.session_state.house_1 = "— กรุณาเลือก —"
            st.session_state.house_2 = "— กรุณาเลือก —"
            st.session_state.show_compare = False
            st.rerun()

        if close:
            st.session_state.show_compare_ui = False
            st.session_state.show_compare = False
            st.rerun()

        if compare:
            st.session_state.show_compare = True

        if st.session_state.show_compare:
            h1_name = st.session_state.house_1
            h2_name = st.session_state.house_2

            if h1_name == "— กรุณาเลือก —" or h2_name == "— กรุณาเลือก —":
                st.warning("⚠️ กรุณาเลือกแบบบ้านให้ครบทั้ง 2 แบบ")
            elif h1_name == h2_name:
                st.warning("⚠️ กรุณาเลือกแบบบ้านคนละแบบ")
            else:
                h1 = df[df["name"] == h1_name].iloc[0]
                h2 = df[df["name"] == h2_name].iloc[0]

                compare_df = pd.DataFrame({
                    "รายการ": [
                        "จำนวนชั้น",
                        "จำนวนห้องนอน",
                        "จำนวนห้องน้ำ",
                        "พื้นที่ใช้สอย (ตร.ม.)",
                        "ราคาโดยประมาณ"
                    ],
                    h1_name: [
                        h1["floor"],
                        h1["bedroom"],
                        h1["bathroom"],
                        h1["area"],
                        h1.get("price_link", "-")
                    ],
                    h2_name: [
                        h2["floor"],
                        h2["bedroom"],
                        h2["bathroom"],
                        h2["area"],
                        h2.get("price_link", "-")
                    ]
                })

                st.markdown("### 📊 ตารางเปรียบเทียบแบบบ้าน")
                st.table(compare_df)

    st.markdown("---")

    # =================================================
    # 🧱 เลือกรูปแบบการแสดงผล
    # =================================================
    

    # =================================================
    # 📋 แสดงผลแบบ Grid (3 คอลัมน์ตายตัว)
    # =================================================
    cols = st.columns(3)

    for i, row in df.iterrows():
        with cols[i % 3]:

            # =========================
            # 🖼️ แสดงรูปบ้าน (ถ้ามี)
            # =========================
            def load_image_from_url(url):
                try:
                    headers = {
                        "User-Agent": "Mozilla/5.0"
                    }
                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                    return BytesIO(response.content)
                except Exception:
                    return None

            img = load_image_from_url(row.get("image_link"))
            if img:
                st.image(img, use_container_width=True)

            # =========================
            # 🏠 การ์ดข้อมูลแบบบ้าน
            # =========================

            # --------- ฟังก์ชันแสดงราคา ----------
            def render_price(price_value):
                # ไม่มีข้อมูล
                if pd.isna(price_value) or str(price_value).strip() == "":
                    return "💰 ราคาประมาณ : -"

                price_str = str(price_value).strip()

                # เป็นลิงก์
                if price_str.startswith("http"):
                    return f'💰 <a href="{price_str}" target="_blank">ดูราคาประมาณ</a>'

                # เป็นข้อความราคา (เช่น 450,000 - 675,000 บาท)
                return f"💰 ราคาประมาณ : {price_str}"



            price_display = render_price(row.get("price_link"))

            st.markdown(
                f"""
                <div style="
                    background-color:#e5e7eb;
                    padding:16px;
                    border-radius:12px;
                    margin-bottom:16px;
                    box-shadow:0 4px 12px rgba(0,0,0,0.3);
                ">
                    <h4>🏡 {row['name']}</h4>
                    <ul>
                        <li>ชั้น: {row['floor']}</li>
                        <li>ห้องนอน: {row['bedroom']} ห้อง</li>
                        <li>ห้องน้ำ: {row['bathroom']} ห้อง</li>
                        <li>พื้นที่ใช้สอย: {row['area']} ตร.ม.</li>
                    </ul>
                    <p>{price_display}</p>
                """
                + (
                    f'<a href="{row["pdf_link"]}" target="_blank">📄 ดาวน์โหลดแบบบ้าน (PDF)</a>'
                    if pd.notna(row.get("pdf_link")) and row["pdf_link"] != ""
                    else ""
                )
                + "</div>",
                unsafe_allow_html=True
            )



elif df is not None and df.empty:
    st.warning("ไม่พบแบบบ้านที่ตรงกับเงื่อนไข")



