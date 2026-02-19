import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="KPI 대시보드", layout="wide")
st.title("손님 미수정리 (엑셀 업로드 방식)")

DATA_DIR = "data"
LAST_FILE_PATH = os.path.join(DATA_DIR, "latest.xlsx")
os.makedirs(DATA_DIR, exist_ok=True)

# =========================
# 업로드
# =========================
uploaded = st.file_uploader("엑셀 파일 업로드 (.xlsx)", type=["xlsx"])

if uploaded is not None:
    with open(LAST_FILE_PATH, "wb") as f:
        f.write(uploaded.getbuffer())
    st.success("✅ 업로드 완료! 이제 휴대폰에서도 최신 파일로 확인됩니다.")

# =========================
# 마지막 파일 불러오기
# =========================
if not os.path.exists(LAST_FILE_PATH):
    st.info("업로드된 파일이 아직 없습니다. 엑셀을 업로드해주세요.")
    st.stop()

# =========================
# 시트 선택
# =========================
xls = pd.ExcelFile(LAST_FILE_PATH)
sheet_name = st.selectbox("시트 선택", xls.sheet_names)

df = pd.read_excel(LAST_FILE_PATH, sheet_name=sheet_name)

# =========================
# 검색
# =========================
search = st.text_input("통합 검색 (손님/이용내역/날짜/기사 등)", value="")

view = df.copy()
if search.strip():
    q = search.strip()
    mask = view.astype(str).apply(lambda row: row.str.contains(q, na=False).any(), axis=1)
    view = view[mask]

# =========================
# 컬럼 순서 재배치
# =========================
preferred = ["손님(대표명)", "이용내역누적(Z)", "이용일시누적(Y)", "최신업데이트(H)"]
existing = [c for c in preferred if c in view.columns]
rest = [c for c in view.columns if c not in existing]
view = view[existing + rest]

# =========================
# 모바일/PC 표시 방식 분기
# - 모바일: 카드 리스트(빨간 박스 현상 제거)
# - PC: 테이블
# =========================
mode = st.radio("보기 방식", ["모바일(카드)", "PC(테이블)"], horizontal=True)

st.subheader("검색 결과")

if mode == "PC(테이블)":
    st.dataframe(view, use_container_width=True, height=650)
else:
    # 모바일 카드형 뷰
    # 많이 나오면 느릴 수 있으니 상단에서 일부만 보여주는 옵션 제공
    max_rows = st.slider("표시 개수", 10, 200, 50, step=10)
    show = view.head(max_rows)

    for idx, row in show.iterrows():
        name = str(row.get("손님(대표명)", ""))
        latest = str(row.get("최신업데이트(H)", ""))
        usage = str(row.get("이용내역누적(Z)", ""))
        dates = str(row.get("이용일시누적(Y)", ""))

        st.markdown(f"### {name}")
        if latest:
            st.caption(f"최근 업데이트: {latest}")

        with st.expander("이용내역 보기"):
            if usage:
                st.text(usage)
            else:
                st.write("-")

        if dates:
            with st.expander("이용일시 보기"):
                st.text(dates)

        st.divider()

# =========================
# 다운로드
# =========================
csv = view.to_csv(index=False).encode("utf-8-sig")
st.download_button("CSV 다운로드", csv, "filtered.csv", "text/csv")

