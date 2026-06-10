
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="ส่วนเครื่องกล Dashboard", layout="wide")

st.title("🚜 ส่วนเครื่องกล Dashboard")

uploaded = st.sidebar.file_uploader("อัปโหลดไฟล์ Excel", type=["xlsx"])

def load_repair_sheet(file, sheet):
    raw = pd.read_excel(file, sheet_name=sheet, header=None)
    # ดึงคอลัมน์วันที่ตรวจรับและยังไม่ตรวจรับจากโครงสร้างไฟล์จริง
    if raw.shape[1] >= 5:
        df = pd.DataFrame({
            "วันที่ตรวจรับ": raw.iloc[3:, 3],
            "ยังไม่ตรวจรับ": raw.iloc[3:, 4]
        })
        df = df.dropna(how="all")
        return df
    return pd.DataFrame(columns=["วันที่ตรวจรับ","ยังไม่ตรวจรับ"])

if uploaded:
    main = pd.read_excel(uploaded, sheet_name="Sheet1")

    repair = load_repair_sheet(uploaded, "ซ่อมเอง")
    full = load_repair_sheet(uploaded, "เบ็ดเสร็จ")

    tab1, tab2 = st.tabs(["Dashboard เครื่องจักร", "Dashboard งานซ่อม"])

    with tab1:
        total = len(main.dropna(subset=["หมายเลขเครื่องจักร"]))
        wait = main["เครื่องจักรรอซ่อม"].notna().sum()
        free = main["เครื่องจักรว่าง"].notna().sum()
        income = pd.to_numeric(main["รายปี"], errors="coerce").fillna(0).sum()

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("เครื่องจักรทั้งหมด", total)
        c2.metric("เครื่องจักรรอซ่อม", wait)
        c3.metric("เครื่องจักรว่าง", free)
        c4.metric("รายรับรวม/ปี", f"{income:,.0f} บาท")

        left,right = st.columns(2)

        with left:
            fig = px.pie(
                values=[max(total-wait-free,0), wait, free],
                names=["ใช้งานอยู่","รอซ่อม","ว่าง"]
            )
            st.plotly_chart(fig, use_container_width=True)

        with right:
            summary = (
                main.groupby("หน่วยงานที่เช่าใช้")
                .agg(
                    จำนวนเครื่องจักร=("หมายเลขเครื่องจักร","count"),
                    รายรับรวม=("รายปี","sum")
                )
                .reset_index()
                .sort_values("จำนวนเครื่องจักร", ascending=False)
            )
            st.dataframe(summary, use_container_width=True)

        st.subheader("รายชื่อผู้ขับและเครื่องจักร")
        cols = ["หมายเลขเครื่องจักร","รายชื่อเช่าพร้อมผู้ขับ","หน่วยงานที่เช่าใช้","ระยะเวลาการเช่า"]
        st.dataframe(main[cols], use_container_width=True)

    with tab2:

        def repair_card(df,title):
            done = df["วันที่ตรวจรับ"].notna().sum()
            pending = df["ยังไม่ตรวจรับ"].notna().sum()

            st.subheader(title)

            a,b,c = st.columns(3)
            a.metric("ทั้งหมด", len(df))
            b.metric("ตรวจรับแล้ว", done)
            c.metric("ยังไม่ตรวจรับ", pending)

            fig = go.Figure(data=[go.Pie(
                labels=["ตรวจรับแล้ว","ยังไม่ตรวจรับ"],
                values=[done,pending],
                hole=.6
            )])
            st.plotly_chart(fig, use_container_width=True)

            return df[df["ยังไม่ตรวจรับ"].notna()]

        l,r = st.columns(2)

        with l:
            p1 = repair_card(repair,"ซ่อมเอง")

        with r:
            p2 = repair_card(full,"เบ็ดเสร็จ")

        st.subheader("รายการค้างตรวจรับ")

        c1,c2 = st.columns(2)
        c1.dataframe(p1, use_container_width=True)
        c2.dataframe(p2, use_container_width=True)

else:
    st.info("กรุณาอัปโหลดไฟล์ Excel")
