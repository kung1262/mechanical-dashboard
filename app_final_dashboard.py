import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="ระบบจัดการส่วนเครื่องกล")

# ฟังก์ชันตรวจสอบและดึงชื่อคอลัมน์แบบปลอดภัย
def get_col(df, keyword, default=None):
    matches = [c for c in df.columns if keyword in str(c)]
    return matches[0] if matches else default

st.title("📊 ส่วนเครื่องกล Dashboard")

with st.sidebar:
    st.header("อัปโหลดไฟล์ข้อมูล")
    uploaded_file = st.file_uploader("เลือกไฟล์ Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    
    # อ่านชีตตามเงื่อนไข
    df_main = pd.read_excel(xls, sheet_name=0)
    s_repair = next((s for s in xls.sheet_names if "ซ่อม" in s), None)
    s_full = next((s for s in xls.sheet_names if "เบ็ด" in s), None)
    
    df_repair = pd.read_excel(xls, sheet_name=s_repair) if s_repair else pd.DataFrame()
    df_full = pd.read_excel(xls, sheet_name=s_full) if s_full else pd.DataFrame()

    tab1, tab2 = st.tabs(["Dashboard เครื่องจักร", "Dashboard งานซ่อม"])

    with tab1:
        # ค้นหาชื่อคอลัมน์
        c_mach = get_col(df_main, 'หมายเลขเครื่องจักร', 'หมายเลขเครื่องจักร')
        c_wait = get_col(df_main, 'รอซ่อม')
        c_free = get_col(df_main, 'เครื่องจักรว่าง')
        c_inc = get_col(df_main, 'รายปี')
        c_drv = get_col(df_main, 'ผู้ขับ')
        c_unit = get_col(df_main, 'หน่วยงาน')

        # KPI
        total_m = len(df_main)
        wait_m = df_main[c_wait].notna().sum() if c_wait else 0
        free_m = df_main[c_free].notna().sum() if c_free else 0
        income = df_main[c_inc].sum() if c_inc and c_inc in df_main.columns else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("เครื่องจักรทั้งหมด", total_m)
        col2.metric("รอซ่อม", wait_m)
        col3.metric("ว่าง", free_m)
        col4.metric("รายรับรวม", f"{income:,.0f} บาท")

        # กราฟและตาราง
        ca, cb = st.columns(2)
        with ca:
            st.subheader("สถานะเครื่องจักร")
            df_pie = pd.DataFrame({'สถานะ': ['ใช้งาน', 'รอซ่อม', 'ว่าง'], 
                                   'จำนวน': [total_m - wait_m - free_m, wait_m, free_m]})
            st.plotly_chart(px.pie(df_pie, values='จำนวน', names='สถานะ'), use_container_width=True)
        
        with cb:
            st.subheader("ตารางสรุปหน่วยงาน")
            if c_unit:
                summary = df_main.groupby(c_unit).size().reset_index(name='จำนวนเครื่องจักร')
                st.dataframe(summary.sort_values(by='จำนวนเครื่องจักร', ascending=False), use_container_width=True)

        # ตารางรายละเอียดใหม่
        st.subheader("รายละเอียดและผู้ขับ")
        display_cols = [c for c in [c_mach, c_drv, c_unit, c_inc] if c in df_main.columns]
        st.dataframe(df_main[display_cols], use_container_width=True)

        if c_wait:
            st.subheader("รายการเครื่องจักรรอซ่อม")
            st.dataframe(df_main[df_main[c_wait].notna()], use_container_width=True)

    with tab2:
        def render_repair(df, title):
            st.subheader(title)
            c_date = get_col(df, 'วันที่')
            done = df[c_date].notna().sum() if c_date else 0
            pending = len(df) - done
            
            c1, c2, c3 = st.columns(3)
            c1.metric("ทั้งหมด", len(df))
            c2.metric("ตรวจรับแล้ว", done)
            c3.metric("ยังไม่ตรวจรับ", pending)
            
            fig = go.Figure(data=[go.Pie(labels=['ตรวจรับแล้ว', 'ค้าง'], values=[done, pending], hole=.6)])
            st.plotly_chart(fig, use_container_width=True)
            return df[df[c_date].isna()] if c_date else df

        cl, cr = st.columns(2)
        p_r = render_repair(df_repair, "ซ่อมเอง")
        p_f = render_repair(df_full, "เบ็ดเสร็จ")

        st.write("### รายการค้างตรวจรับ")
        c_t1, c_t2 = st.columns(2)
        c_t1.write("ซ่อมเอง:"); c_t1.dataframe(p_r)
        c_t2.write("เบ็ดเสร็จ:"); c_t2.dataframe(p_f)

else:
    st.info("กรุณาอัปโหลดไฟล์ Excel เพื่อเริ่มใช้งาน")
