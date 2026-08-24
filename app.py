import streamlit as st
import pandas as pd
import os
import calendar
from datetime import date
import uuid

st.set_page_config(
    page_title="レストラン予約",
    page_icon="🍽️",
    layout="centered"
)

# =========================================================
# 基本設定
# =========================================================

CSV_FILE = "reservations.csv"

ADMIN_ID = "admin"
ADMIN_PASSWORD = "admin2026"

TIME_SLOTS = [
    "17:00",
    "17:30",
    "18:00",
    "18:30",
    "19:00",
    "19:30",
    "20:00",
]

MAX_RESERVATIONS_PER_SLOT = 1


# =========================================================
# 仮のお客様アカウント 10個
# =========================================================
# 本番運用ではパスワードをコードに直接書かない方が安全です。

CUSTOMERS = {
    "guest01": {
        "password": "pass01",
        "name": "お客様01"
    },
    "guest02": {
        "password": "pass02",
        "name": "お客様02"
    },
    "guest03": {
        "password": "pass03",
        "name": "お客様03"
    },
    "guest04": {
        "password": "pass04",
        "name": "お客様04"
    },
    "guest05": {
        "password": "pass05",
        "name": "お客様05"
    },
    "guest06": {
        "password": "pass06",
        "name": "お客様06"
    },
    "guest07": {
        "password": "pass07",
        "name": "お客様07"
    },
    "guest08": {
        "password": "pass08",
        "name": "お客様08"
    },
    "guest09": {
        "password": "pass09",
        "name": "お客様09"
    },
    "guest10": {
        "password": "pass10",
        "name": "お客様10"
    },
}


# =========================================================
# データ読み込み
# =========================================================

def load_reservations():

    columns = [
        "予約ID",
        "顧客ID",
        "予約日",
        "時間",
        "名前",
        "人数",
        "電話番号",
        "備考"
    ]

    if os.path.exists(CSV_FILE):

        df = pd.read_csv(
            CSV_FILE,
            dtype={
                "予約ID": str,
                "顧客ID": str,
                "予約日": str,
                "時間": str,
                "名前": str,
                "電話番号": str,
                "備考": str,
            }
        )

        # 古いCSVとの互換性
        for col in columns:
            if col not in df.columns:
                df[col] = ""

        return df[columns]

    return pd.DataFrame(
        columns=columns
    )


def save_reservations(df):

    df.to_csv(
        CSV_FILE,
        index=False
    )


# =========================================================
# 空き枠確認
# =========================================================

def get_available_times(target_date):

    df = load_reservations()

    date_str = target_date.strftime(
        "%Y-%m-%d"
    )

    available = []

    for slot in TIME_SLOTS:

        count = len(
            df[
                (df["予約日"] == date_str)
                &
                (df["時間"] == slot)
            ]
        )

        if count < MAX_RESERVATIONS_PER_SLOT:
            available.append(slot)

    return available


def get_day_status(target_date):

    if target_date < date.today():
        return "―"

    available_times = get_available_times(
        target_date
    )

    if len(available_times) == 0:
        return "×"

    elif len(available_times) <= 2:
        return "△"

    else:
        return "○"


# =========================================================
# セッション初期化
# =========================================================

if "customer_logged_in" not in st.session_state:
    st.session_state.customer_logged_in = False

if "customer_id" not in st.session_state:
    st.session_state.customer_id = None

if "customer_name" not in st.session_state:
    st.session_state.customer_name = None

if "selected_date" not in st.session_state:
    st.session_state.selected_date = None


# =========================================================
# サイドバー
# =========================================================

st.sidebar.title("🍽️ 予約システム")

page = st.sidebar.radio(
    "メニュー",
    [
        "お客様",
        "管理者"
    ]
)


# =========================================================
# お客様画面
# =========================================================

if page == "お客様":

    # -----------------------------------------------------
    # ログイン前
    # -----------------------------------------------------

    if not st.session_state.customer_logged_in:

        st.title("🍽️ ご予約")

        st.write(
            "お客様IDとパスワードを入力してください。"
        )

        customer_id = st.text_input(
            "お客様ID"
        )

        customer_password = st.text_input(
            "パスワード",
            type="password"
        )

        if st.button(
            "ログイン",
            type="primary",
            use_container_width=True
        ):

            if customer_id not in CUSTOMERS:

                st.error(
                    "お客様IDまたはパスワードが違います。"
                )

            elif (
                CUSTOMERS[customer_id]["password"]
                != customer_password
            ):

                st.error(
                    "お客様IDまたはパスワードが違います。"
                )

            else:

                st.session_state.customer_logged_in = True
                st.session_state.customer_id = customer_id
                st.session_state.customer_name = (
                    CUSTOMERS[customer_id]["name"]
                )

                st.rerun()

        st.stop()


    # -----------------------------------------------------
    # ログイン後
    # -----------------------------------------------------

    st.title(
        f"🍽️ {st.session_state.customer_name} 様"
    )

    col_logout1, col_logout2 = st.columns(
        [3, 1]
    )

    with col_logout2:

        if st.button(
            "ログアウト"
        ):

            st.session_state.customer_logged_in = False
            st.session_state.customer_id = None
            st.session_state.customer_name = None
            st.session_state.selected_date = None

            st.rerun()


    customer_menu = st.radio(
        "メニュー",
        [
            "新しく予約する",
            "予約を確認・キャンセル"
        ],
        horizontal=True
    )


    # =====================================================
    # 新規予約
    # =====================================================

    if customer_menu == "新しく予約する":

        st.subheader(
            "新しく予約する"
        )

        today = date.today()

        col1, col2 = st.columns(2)

        with col1:

            selected_year = st.selectbox(
                "年",
                list(
                    range(
                        today.year,
                        today.year + 2
                    )
                )
            )

        with col2:

            selected_month = st.selectbox(
                "月",
                list(range(1, 13)),
                index=today.month - 1
            )


        st.markdown(
            "### 空き状況"
        )

        st.caption(
            "○ 空きあり　△ 残りわずか　× 満席"
        )


        cal = calendar.Calendar(
            firstweekday=0
        )

        weeks = cal.monthdayscalendar(
            selected_year,
            selected_month
        )

        headers = [
            "月",
            "火",
            "水",
            "木",
            "金",
            "土",
            "日"
        ]

        header_cols = st.columns(7)

        for i, header in enumerate(headers):

            header_cols[i].markdown(
                f"**{header}**"
            )


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

                    label = (
                        f"{day_num}\n{status}"
                    )

                    if status in [
                        "―",
                        "×"
                    ]:

                        cols[i].button(
                            label,
                            disabled=True,
                            key=f"customer_day_{target_date}"
                        )

                    else:

                        if cols[i].button(
                            label,
                            key=f"customer_day_{target_date}",
                            use_container_width=True
                        ):

                            st.session_state.selected_date = (
                                target_date
                            )


        # -------------------------------------------------
        # 日付選択後
        # -------------------------------------------------

        if st.session_state.selected_date:

            selected_date = (
                st.session_state.selected_date
            )

            st.divider()

            st.subheader(
                selected_date.strftime(
                    "%Y年%m月%d日"
                )
            )

            available_times = get_available_times(
                selected_date
            )

            if not available_times:

                st.warning(
                    "この日は満席です。"
                )

            else:

                reserve_time = st.radio(
                    "ご希望時間",
                    available_times,
                    horizontal=True
                )

                with st.form(
                    "reservation_form"
                ):

                    people = st.selectbox(
                        "人数",
                        [
                            1,
                            2,
                            3,
                            4,
                            5,
                            6
                        ]
                    )

                    phone = st.text_input(
                        "電話番号"
                    )

                    memo = st.text_area(
                        "備考",
                        placeholder=(
                            "アレルギーなどございましたら"
                            "ご記入ください。"
                        )
                    )

                    submitted = (
                        st.form_submit_button(
                            "この内容で予約する",
                            type="primary",
                            use_container_width=True
                        )
                    )


                    if submitted:

                        if not phone:

                            st.error(
                                "電話番号を入力してください。"
                            )

                        else:

                            # 予約直前にもう一度確認
                            latest_available = (
                                get_available_times(
                                    selected_date
                                )
                            )

                            if (
                                reserve_time
                                not in latest_available
                            ):

                                st.error(
                                    "申し訳ありません。"
                                    "この時間は先ほど予約が入りました。"
                                )

                            else:

                                df = load_reservations()

                                reservation_id = str(
                                    uuid.uuid4()
                                )

                                new_data = {
                                    "予約ID":
                                        reservation_id,

                                    "顧客ID":
                                        st.session_state.customer_id,

                                    "予約日":
                                        selected_date.strftime(
                                            "%Y-%m-%d"
                                        ),

                                    "時間":
                                        reserve_time,

                                    "名前":
                                        st.session_state.customer_name,

                                    "人数":
                                        people,

                                    "電話番号":
                                        phone,

                                    "備考":
                                        memo
                                }

                                df = pd.concat(
                                    [
                                        df,
                                        pd.DataFrame(
                                            [new_data]
                                        )
                                    ],
                                    ignore_index=True
                                )

                                save_reservations(
                                    df
                                )

                                st.success(
                                    f"""
予約を受け付けました。

**{selected_date.strftime('%Y年%m月%d日')}  
{reserve_time}**

{people}名
"""
                                )

                                st.session_state.selected_date = None


    # =====================================================
    # 自分の予約確認・キャンセル
    # =====================================================

    elif customer_menu == "予約を確認・キャンセル":

        st.subheader(
            "予約を確認・キャンセル"
        )

        df = load_reservations()

        my_df = df[
            df["顧客ID"]
            ==
            st.session_state.customer_id
        ].copy()

        if my_df.empty:

            st.info(
                "現在予約はありません。"
            )

        else:

            my_df["予約日_dt"] = pd.to_datetime(
                my_df["予約日"],
                errors="coerce"
            )

            today_ts = pd.Timestamp(
                date.today()
            )

            my_df = my_df[
                my_df["予約日_dt"]
                >=
                today_ts
            ]

            my_df = my_df.sort_values(
                by=[
                    "予約日_dt",
                    "時間"
                ]
            )

            if my_df.empty:

                st.info(
                    "今後の予約はありません。"
                )

            else:

                for index, row in my_df.iterrows():

                    reservation_date = (
                        pd.to_datetime(
                            row["予約日"]
                        ).strftime(
                            "%Y年%m月%d日"
                        )
                    )

                    with st.container(
                        border=True
                    ):

                        st.markdown(
                            f"""
### {reservation_date}　{row["時間"]}

**{row["人数"]}名**

電話番号：{row["電話番号"]}
"""
                        )

                        if (
                            pd.notna(row["備考"])
                            and str(row["備考"]).strip()
                            and str(row["備考"]) != "nan"
                        ):

                            st.write(
                                f'備考：{row["備考"]}'
                            )


                        confirm_key = (
                            f"confirm_cancel_"
                            f'{row["予約ID"]}'
                        )

                        if confirm_key not in st.session_state:
                            st.session_state[
                                confirm_key
                            ] = False


                        if not st.session_state[
                            confirm_key
                        ]:

                            if st.button(
                                "この予約をキャンセル",
                                key=(
                                    f'cancel_{row["予約ID"]}'
                                )
                            ):

                                st.session_state[
                                    confirm_key
                                ] = True

                                st.rerun()

                        else:

                            st.warning(
                                "この予約をキャンセルしますか？"
                            )

                            col_yes, col_no = (
                                st.columns(2)
                            )

                            with col_yes:

                                if st.button(
                                    "はい、キャンセルする",
                                    key=(
                                        f'yes_{row["予約ID"]}'
                                    ),
                                    type="primary"
                                ):

                                    df = load_reservations()

                                    df = df[
                                        df["予約ID"]
                                        !=
                                        row["予約ID"]
                                    ]

                                    save_reservations(
                                        df
                                    )

                                    st.session_state[
                                        confirm_key
                                    ] = False

                                    st.success(
                                        "予約をキャンセルしました。"
                                    )

                                    st.rerun()


                            with col_no:

                                if st.button(
                                    "戻る",
                                    key=(
                                        f'no_{row["予約ID"]}'
                                    )
                                ):

                                    st.session_state[
                                        confirm_key
                                    ] = False

                                    st.rerun()


# =========================================================
# 管理者画面
# =========================================================

elif page == "管理者":

    st.title(
        "🔐 予約管理"
    )

    admin_id = st.text_input(
        "管理者ID"
    )

    admin_password = st.text_input(
        "管理者パスワード",
        type="password"
    )

    if (
        admin_id != ADMIN_ID
        or
        admin_password != ADMIN_PASSWORD
    ):

        st.info(
            "管理者IDとパスワードを入力してください。"
        )

        st.stop()


    df = load_reservations()

    if df.empty:

        st.info(
            "現在予約はありません。"
        )

        st.stop()


    df["予約日_dt"] = pd.to_datetime(
        df["予約日"],
        errors="coerce"
    )


    today_ts = pd.Timestamp(
        date.today()
    )


    future_df = df[
        df["予約日_dt"]
        >=
        today_ts
    ].copy()


    future_df = future_df.sort_values(
        by=[
            "予約日_dt",
            "時間"
        ]
    )


    st.subheader(
        "今後の予約"
    )


    if future_df.empty:

        st.info(
            "今後の予約はありません。"
        )

    else:

        display_df = future_df[
            [
                "予約日",
                "時間",
                "顧客ID",
                "名前",
                "人数",
                "電話番号",
                "備考"
            ]
        ].copy()

        display_df["予約日"] = (
            pd.to_datetime(
                display_df["予約日"]
            ).dt.strftime(
                "%Y/%m/%d"
            )
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


    st.divider()


    # =====================================================
    # 日付別確認
    # =====================================================

    st.subheader(
        "日付別に確認"
    )

    selected_admin_date = (
        st.date_input(
            "確認する日付",
            value=date.today()
        )
    )

    date_str = (
        selected_admin_date.strftime(
            "%Y-%m-%d"
        )
    )


    day_df = df[
        df["予約日"] == date_str
    ].copy()


    if day_df.empty:

        st.info(
            "この日の予約はありません。"
        )

    else:

        day_df = day_df.sort_values(
            by="時間"
        )

        display_day = day_df[
            [
                "時間",
                "顧客ID",
                "名前",
                "人数",
                "電話番号",
                "備考"
            ]
        ].copy()

        st.dataframe(
            display_day,
            use_container_width=True,
            hide_index=True
        )


        col1, col2 = st.columns(2)

        col1.metric(
            "予約組数",
            f"{len(day_df)}組"
        )

        col2.metric(
            "予約人数",
            f'{int(day_df["人数"].sum())}名'
        )def load_reservations():
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
# 空き状況
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
# 画面切替
# =========================
st.sidebar.title("メニュー")

page = st.sidebar.radio(
    "画面を選択",
    [
        "お客様予約",
        "管理者"
    ]
)


# =====================================================
# お客様画面
# =====================================================
if page == "お客様予約":

    st.title("🍽️ レストラン予約")

    password = st.text_input(
        "予約用パスワード",
        type="password"
    )

    if password != CUSTOMER_PASSWORD:
        st.info(
            "ご案内したパスワードを入力してください。"
        )
        st.stop()


    today = date.today()

    col1, col2 = st.columns(2)

    with col1:
        selected_year = st.selectbox(
            "年",
            list(
                range(
                    today.year,
                    today.year + 2
                )
            )
        )

    with col2:
        selected_month = st.selectbox(
            "月",
            list(range(1, 13)),
            index=today.month - 1
        )


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
        "月",
        "火",
        "水",
        "木",
        "金",
        "土",
        "日"
    ]

    header_cols = st.columns(7)

    for i, h in enumerate(headers):
        header_cols[i].markdown(
            f"**{h}**"
        )


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

                label = (
                    f"{day_num}\n{status}"
                )

                if status in [
                    "―",
                    "×"
                ]:

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
    # 日付選択後
    # =========================
    if "selected_date" in st.session_state:

        selected_date = (
            st.session_state[
                "selected_date"
            ]
        )

        st.divider()

        st.subheader(
            selected_date.strftime(
                "%Y年%m月%d日の予約"
            )
        )


        available_times = (
            get_available_times(
                selected_date
            )
        )


        if len(
            available_times
        ) == 0:

            st.warning(
                "この日は満席です。"
            )

        else:

            reserve_time = st.radio(
                "ご希望時間",
                available_times,
                horizontal=True
            )

            with st.form(
                "reservation_form"
            ):

                name = st.text_input(
                    "お名前"
                )

                people = st.selectbox(
                    "人数",
                    [
                        1,
                        2,
                        3,
                        4,
                        5,
                        6
                    ]
                )

                phone = st.text_input(
                    "電話番号"
                )

                memo = st.text_area(
                    "備考",
                    placeholder=(
                        "アレルギーなどございましたら"
                        "ご記入ください。"
                    )
                )


                submitted = (
                    st.form_submit_button(
                        "この内容で予約する",
                        type="primary",
                        use_container_width=True
                    )
                )


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

                        latest_available = (
                            get_available_times(
                                selected_date
                            )
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


# =====================================================
# 管理者画面
# =====================================================
elif page == "管理者":

    st.title(
        "🔐 予約管理"
    )

    admin_password = st.text_input(
        "管理者パスワード",
        type="password"
    )

    if admin_password != ADMIN_PASSWORD:

        st.info(
            "管理者パスワードを入力してください。"
        )

        st.stop()


    df = load_reservations()


    if df.empty:

        st.info(
            "現在予約はありません。"
        )

        st.stop()


    # =========================
    # 日付型へ変換
    # =========================
    df["予約日"] = pd.to_datetime(
        df["予約日"]
    )


    # =========================
    # 今日以降の予約
    # =========================
    today_ts = pd.Timestamp(
        date.today()
    )

    future_df = df[
        df["予約日"] >= today_ts
    ].copy()


    future_df = future_df.sort_values(
        by=[
            "予約日",
            "時間"
        ]
    )


    st.subheader(
        "今後の予約"
    )


    if future_df.empty:

        st.info(
            "今後の予約はありません。"
        )

    else:

        # 表示用に日付を文字列化
        display_df = future_df.copy()

        display_df["予約日"] = (
            display_df[
                "予約日"
            ].dt.strftime(
                "%Y/%m/%d"
            )
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


    st.divider()


    # =========================
    # 日付指定
    # =========================
    st.subheader(
        "日付別に確認"
    )

    selected_admin_date = (
        st.date_input(
            "確認する日付",
            value=date.today()
        )
    )


    admin_date_str = (
        selected_admin_date.strftime(
            "%Y-%m-%d"
        )
    )


    day_df = df[
        df[
            "予約日"
        ].dt.strftime(
            "%Y-%m-%d"
        ) == admin_date_str
    ].copy()


    if day_df.empty:

        st.info(
            "この日の予約はありません。"
        )

    else:

        day_df = day_df.sort_values(
            by="時間"
        )

        display_day_df = (
            day_df.copy()
        )

        display_day_df["予約日"] = (
            display_day_df[
                "予約日"
            ].dt.strftime(
                "%Y/%m/%d"
            )
        )


        st.dataframe(
            display_day_df,
            use_container_width=True,
            hide_index=True
        )


        total_people = int(
            day_df[
                "人数"
            ].sum()
        )

        total_groups = len(
            day_df
        )


        col1, col2 = st.columns(2)

        col1.metric(
            "予約組数",
            f"{total_groups}組"
        )

        col2.metric(
            "予約人数",
            f"{total_people}名"
        )
