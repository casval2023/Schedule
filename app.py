import streamlit as st
import pandas as pd
import os
import calendar
from datetime import date, datetime

st.set_page_config(
    page_title="レストラン予約",
    page_icon="🍽️",
    layout="centered"
)

# =========================
# 基本設定
# =========================
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

# 1時間帯あたり受付できる組数
MAX_RESERVATIONS_PER_SLOT = 1

# =========================
# CSV読み込み
# =========================
def load_reservations():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)

    return pd.DataFrame(
        columns=[
            "予約日",
            "時間",
            "名前",
            "人数",
            "電話番号",
            "備考"
        ]
    )


def save_reservation(new_data):
    df = load_reservations()

    df = pd.concat(
        [df, pd.DataFrame([new_data])],
        ignore_index=True
    )

    df.to_csv(
        CSV_FILE,
        index=False
    )


# =========================
# 空き状況判定
# =========================
def get_available_times(target_date):
    df = load_reservations()

    date_str = target_date.strftime("%Y-%m-%d")

    available = []

    for slot in TIME_SLOTS:

        count = len(
            df[
                (df["予約日"] == date_str)
                & (df["時間"] == slot)
            ]
        )

        if count < MAX_RESERVATIONS_PER_SLOT:
            available.append(slot)

    return available


def get_day_status(target_date):

    # 過去日は予約不可
    if target_date < date.today():
        return "―"

    available_times = get_available_times(target_date)

    if len(available_times) == 0:
        return "×"

    elif len(available_times) <= 2:
        return "△"

    else:
        return "○"


# =========================
# ログイン
# =========================
st.title("🍽️ レストラン予約")

password = st.text_input(
    "予約用パスワード",
    type="password"
)

if password != PASSWORD:
    st.info("ご案内したパスワードを入力してください。")
    st.stop()


# =========================
# 月選択
# =========================
today = date.today()

col1, col2 = st.columns(2)

with col1:
    selected_year = st.selectbox(
        "年",
        list(range(today.year, today.year + 2))
    )

with col2:
    selected_month = st.selectbox(
        "月",
        list(range(1, 13)),
        index=today.month - 1
    )


# =========================
# 月間カレンダー表示
# =========================
st.subheader(
    f"{selected_year}年{selected_month}月"
)

cal = calendar.Calendar(
    firstweekday=0
)

weeks = cal.monthdayscalendar(
    selected_year,
    selected_month
)

headers = [
    "月", "火", "水", "木", "金", "土", "日"
]

header_cols = st.columns(7)

for i, h in enumerate(headers):
    header_cols[i].markdown(
        f"**{h}**"
    )


selected_date = None

for week in weeks:

    cols = st.columns(7)

    for i, day_num in enumerate(week):

        if day_num == 0:
            cols[i].write("")

        else:

            target_date = date(
                selected_year,
                selected_month,
                day_num
            )

            status = get_day_status(
                target_date
            )

            label = f"{day_num}\n{status}"

            if status == "―":
                cols[i].button(
                    label,
                    disabled=True,
                    key=f"day_{target_date}"
                )

            elif status == "×":
                cols[i].button(
                    label,
                    disabled=True,
                    key=f"day_{target_date}"
                )

            else:

                clicked = cols[i].button(
                    label,
                    key=f"day_{target_date}",
                    use_container_width=True
                )

                if clicked:
                    st.session_state[
                        "selected_date"
                    ] = target_date


# =========================
# 選択日保持
# =========================
if "selected_date" in st.session_state:

    selected_date = st.session_state[
        "selected_date"
    ]

    st.divider()

    st.subheader(
        selected_date.strftime(
            "%Y年%m月%d日の予約"
        )
    )


    # =========================
    # 空き時間取得
    # =========================
    available_times = get_available_times(
        selected_date
    )

    if len(available_times) == 0:

        st.warning(
            "この日は満席です。"
        )

    else:

        reserve_time = st.radio(
            "ご希望時間",
            available_times,
            horizontal=True
        )

        st.divider()


        # =========================
        # 入力フォーム
        # =========================
        with st.form(
            "reservation_form"
        ):

            name = st.text_input(
                "お名前"
            )

            people = st.selectbox(
                "人数",
                [1, 2, 3, 4, 5, 6]
            )

            phone = st.text_input(
                "電話番号"
            )

            memo = st.text_area(
                "備考",
                placeholder="アレルギーなどございましたらご記入ください。"
            )

            submitted = st.form_submit_button(
                "この内容で予約する",
                type="primary",
                use_container_width=True
            )


            # =========================
            # 予約確定
            # =========================
            if submitted:

                if not name:
                    st.error(
                        "お名前を入力してください。"
                    )

                elif not phone:
                    st.error(
                        "電話番号を入力してください。"
                    )

                else:

                    # 念のため予約直前に再チェック
                    latest_available = get_available_times(
                        selected_date
                    )

                    if reserve_time not in latest_available:

                        st.error(
                            "申し訳ありません。"
                            "この時間は先ほど予約が入りました。"
                        )

                    else:

                        new_data = {
                            "予約日":
                                selected_date.strftime(
                                    "%Y-%m-%d"
                                ),
                            "時間":
                                reserve_time,
                            "名前":
                                name,
                            "人数":
                                people,
                            "電話番号":
                                phone,
                            "備考":
                                memo
                        }

                        save_reservation(
                            new_data
                        )

                        st.success(
                            f"""
予約を受け付けました。

**{selected_date.strftime('%Y年%m月%d日')}  
{reserve_time}**

{name} 様  
{people}名
"""
                        )

                        st.balloons()
