import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(
    page_title="レストラン予約",
    page_icon="🍽️",
    layout="centered"
)

# -----------------------------
# 設定
# -----------------------------
PASSWORD = "restaurant2026"
CSV_FILE = "reservations.csv"

TIME_SLOTS = [
    "17:00",
    "17:30",
    "18:00",
    "18:30",
    "19:00",
    "19:30",
    "20:00",
]

# -----------------------------
# ログイン
# -----------------------------
st.title("🍽️ ご予約")

password = st.text_input(
    "予約用パスワード",
    type="password"
)

if password != PASSWORD:
    st.info("ご案内したパスワードを入力してください。")
    st.stop()

# -----------------------------
# 既存予約読込
# -----------------------------
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(
        columns=[
            "予約日",
            "時間",
            "名前",
            "人数",
            "電話番号",
            "備考"
        ]
    )

# -----------------------------
# 予約フォーム
# -----------------------------
st.success("予約ページにアクセスしました。")

reserve_date = st.date_input(
    "予約日",
    min_value=date.today()
)

# 選択された日の予約状況
date_str = reserve_date.strftime("%Y-%m-%d")

reserved_times = df.loc[
    df["予約日"] == date_str,
    "時間"
].tolist()

available_times = [
    t for t in TIME_SLOTS
    if t not in reserved_times
]

if len(available_times) == 0:
    st.warning("この日は満席です。")
    st.stop()

reserve_time = st.selectbox(
    "予約時間",
    available_times
)

name = st.text_input("お名前")

people = st.selectbox(
    "人数",
    [1, 2, 3, 4, 5, 6]
)

phone = st.text_input("電話番号")

memo = st.text_area(
    "備考",
    placeholder="アレルギーなどございましたらご記入ください。"
)

# -----------------------------
# 予約登録
# -----------------------------
if st.button(
    "予約する",
    type="primary",
    use_container_width=True
):

    if not name:
        st.error("お名前を入力してください。")

    elif not phone:
        st.error("電話番号を入力してください。")

    else:

        new_data = pd.DataFrame(
            [{
                "予約日": date_str,
                "時間": reserve_time,
                "名前": name,
                "人数": people,
                "電話番号": phone,
                "備考": memo
            }]
        )

        df = pd.concat(
            [df, new_data],
            ignore_index=True
        )

        df.to_csv(
            CSV_FILE,
            index=False
        )

        st.success(
            f"""
            予約を受け付けました。

            {reserve_date.strftime('%Y年%m月%d日')}
            {reserve_time}

            {name} 様
            {people}名
            """
        )

        st.balloons()
