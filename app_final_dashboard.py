
summary = (
    main.groupby("หน่วยงานที่เช่าใช้")
    .agg({
        "หมายเลขเครื่องจักร": "count",
        "รายปี": "sum"
    })
    .reset_index()
)

summary.columns = [
    "หน่วยงานที่เช่าใช้",
    "จำนวนเครื่องจักร",
    "รายรับรวม"
]

summary = summary.sort_values(
    by="จำนวนเครื่องจักร",
    ascending=False
)
    st.info("กรุณาอัปโหลดไฟล์ Excel")
