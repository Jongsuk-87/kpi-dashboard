import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="KPI 대시보드", layout="wide")
st.title("KPI 대시보드 (엑셀 업로드 방식)")

DATA_DIR = "data"
LAST_FILE_PATH = os.path.join(DATA_DIR, "latest.xlsx")
os.makedirs(DATA_DIR, exist_ok=True)

# 업로드
uploaded = st.file_uploader("엑셀 파일 업로드 (.xlsx)", type=["xlsx"])

if uploaded is not None:
    # 업로드 파일을 서버(배포된 앱)쪽에 저장
    with open(LAST_FILE_PATH, "wb") as f:
        f.write(uploaded.getbuffer())
    st.success("✅ 업로드 완료! 이제 휴대폰에서 들어와도 최신 파일로 보입니다.")

# 마지막 파일 불러오기
if not os.path.exists(LAST_FILE_PATH):
    st.info("업로드된 파일이 아직 없습니다. 엑셀을 업로드해주세요.")
    st.stop()

# 시트 선택
xls = pd.ExcelFile(LAST_FILE_PATH)
sheet_name = st.selectbox("시트 선택", xls.sheet_names)

df = pd.read_excel(LAST_FILE_PATH, sheet_name=sheet_name)

# 검색
search = st.text_input("통합 검색 (손님/이용내역/날짜/기사 등)", value="")

view = df.copy()
if search.strip():
    q = search.strip()
    mask = view.astype(str).apply(lambda row: row.str.contains(q, na=False).any(), axis=1)
    view = view[mask]

st.subheader("검색 결과")
st.dataframe(view, use_container_width=True, height=650)

# 다운로드
csv = view.to_csv(index=False).encode("utf-8-sig")
st.download_button("CSV 다운로드", csv, "filtered.csv", "text/csv")
