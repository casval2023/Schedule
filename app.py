import streamlit as st
import pandas as pd
import os
import calendar
from datetime import date
import uuid

# =========================================================
# ページ設定
# =========================================================

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

CUSTOMERS = {
    "guest01": {"password": "pass01", "name": "お客様01"},
    "guest02": {"password": "pass02", "name": "お客様02"},
    "guest03": {"password": "pass03", "name": "お客様03"},
    "guest04": {"password": "pass04", "name": "お客様04"},
    "guest05": {"password": "pass05", "name": "お客様05"},
    "guest06": {"password": "pass06", "name": "お客様06"},
    "guest07": {"password": "pass07", "name": "お客様07"},
    "guest08": {"password": "pass08", "name": "お客様08"},
    "guest09": {"password": "pass09", "name": "お客様09"},
    "guest10": {"password": "pass10", "name": "お客様10"},
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
        "備考",
    ]

    if os.path.exists(CSV_FILE):
        try:
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
                },
            )
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=columns)

        for col in columns:
            if col not in df.columns:
                df[col] = ""

        return df[columns]

    return pd.DataFrame(columns=columns)


def save_reservations(df):
    df.to_csv(CSV_FILE, index=False)


# =========================================================
# 空き状況
# =========================================================

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
    if len(available_times) <= 2:
        return "△"
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

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False


# =========================================================
# サイドバー
# =========================================================

st.sidebar.title("🍽️ 予約システム")

page = st.sidebar.radio(
    "メニュー",
    ["お客様", "管理者"],
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
        st.write("お客様IDとパスワードを入力してください。")

        customer_id = st.text_input("お客様ID")
        customer_password = st.text_input(
            "パスワード",
            type="password",
        )

        if st.button(
            "ログイン",
            type="primary",
            use_container_width=True,
        ):
            if customer_id not in CUSTOMERS:
                st.error("お客様IDまたはパスワードが違います。")

            elif CUSTOMERS[customer_id]["password"] != customer_password:
                st.error("お客様IDまたはパスワードが違います。")

            else:
                st.session_state.customer_logged_in = True
                st.session_state.customer_id = customer_id
                st.session_state.customer_name = CUSTOMERS[customer_id]["name"]
                st.rerun()

        st.stop()

    # -----------------------------------------------------
    # ログイン後
    # -----------------------------------------------------

    st.title(f"🍽️ {st.session_state.customer_name} 様")

    _, col_logout = st.columns([3, 1])

    with col_logout:
        if st.button("ログアウト"):
            st.session_state.customer_logged_in = False
            st.session_state.customer_id = None
            st.session_state.customer_name = None
            st.session_state.selected_date = None
            st.rerun()

    customer_menu = st.radio(
        "メニュー",
        ["新しく予約する", "予約を確認・キャンセル"],
        horizontal=True,
    )

    # =====================================================
    # 新規予約
    # =====================================================

    if customer_menu == "新しく予約する":
        st.subheader("新しく予約する")

        today = date.today()
        col1, col2 = st.columns(2)

        with col1:
            selected_year = st.selectbox(
                "年",
                list(range(today.year, today.year + 2)),
            )

        with col2:
            selected_month = st.selectbox(
                "月",
                list(range(1, 13)),
                index=today.month - 1,
            )

        st.markdown(f"### {selected_year}年{selected_month}月")
        st.caption("○ 空きあり　△ 残りわずか　× 満席")

        cal = calendar.Calendar(firstweekday=0)
        weeks = cal.monthdayscalendar(
            selected_year,
            selected_month,
        )

        headers = ["月", "火", "水", "木", "金", "土", "日"]
        header_cols = st.columns(7)

        for i, header in enumerate(headers):
            header_cols[i].markdown(f"**{header}**")

        for week in weeks:
            cols = st.columns(7)

            for i, day_num in enumerate(week):
                if day_num == 0:
                    cols[i].write("")
                    continue

                target_date = date(
                    selected_year,
                    selected_month,
                    day_num,
                )

                status = get_day_status(target_date)
                label = f"{day_num}\n{status}"

                button_key = (
                    f"customer_day_"
                    f"{selected_year}_"
                    f"{selected_month}_"
                    f"{day_num}"
                )

                if status in ["―", "×"]:
                    cols[i].button(
                        label,
                        disabled=True,
                        key=button_key,
                        use_container_width=True,
                    )
                else:
                    clicked = cols[i].button(
                        label,
                        key=button_key,
                        use_container_width=True,
                    )

                    if clicked:
                        st.session_state.selected_date = target_date

        # -------------------------------------------------
        # 日付選択後
        # -------------------------------------------------

        if st.session_state.selected_date:
            selected_date = st.session_state.selected_date

            st.divider()
            st.subheader(
                selected_date.strftime("%Y年%m月%d日の予約")
            )

            available_times = get_available_times(selected_date)

            if not available_times:
                st.warning("この日は満席です。")
            else:
                reserve_time = st.radio(
                    "ご希望時間",
                    available_times,
                    horizontal=True,
                )

                with st.form("reservation_form"):
                    people = st.selectbox(
                        "人数",
                        [1, 2, 3, 4, 5, 6],
                    )

                    phone = st.text_input("電話番号")

                    memo = st.text_area(
                        "備考",
                        placeholder=(
                            "アレルギーなどございましたら"
                            "ご記入ください。"
                        ),
                    )

                    submitted = st.form_submit_button(
                        "この内容で予約する",
                        type="primary",
                        use_container_width=True,
                    )

                if submitted:
                    if not phone:
                        st.error("電話番号を入力してください。")
                    else:
                        latest_available = get_available_times(
                            selected_date
                        )

                        if reserve_time not in latest_available:
                            st.error(
                                "申し訳ありません。"
                                "この時間は先ほど予約が入りました。"
                            )
                        else:
                            df = load_reservations()
                            reservation_id = str(uuid.uuid4())

                            new_data = {
                                "予約ID": reservation_id,
                                "顧客ID": st.session_state.customer_id,
                                "予約日": selected_date.strftime("%Y-%m-%d"),
                                "時間": reserve_time,
                                "名前": st.session_state.customer_name,
                                "人数": people,
                                "電話番号": phone,
                                "備考": memo,
                            }

                            df = pd.concat(
                                [
                                    df,
                                    pd.DataFrame([new_data]),
                                ],
                                ignore_index=True,
                            )

                            save_reservations(df)

                            st.success(
                                f"""
予約を受け付けました。

**{selected_date.strftime('%Y年%m月%d日')}  
{reserve_time}**

**{people}名**

「予約を確認・キャンセル」から
予約内容をご確認いただけます。
"""
                            )

                            st.session_state.selected_date = None

    # =====================================================
    # 自分の予約確認・キャンセル
    # =====================================================

    elif customer_menu == "予約を確認・キャンセル":
        st.subheader("予約を確認・キャンセル")

        df = load_reservations()

        my_df = df[
            df["顧客ID"] == st.session_state.customer_id
        ].copy()

        if my_df.empty:
            st.info("現在予約はありません。")
        else:
            my_df["予約日_dt"] = pd.to_datetime(
                my_df["予約日"],
                errors="coerce",
            )

            today_ts = pd.Timestamp(date.today())

            my_df = my_df[
                my_df["予約日_dt"] >= today_ts
            ].copy()

            my_df = my_df.sort_values(
                by=["予約日_dt", "時間"]
            )

            if my_df.empty:
                st.info("今後の予約はありません。")
            else:
                for _, row in my_df.iterrows():
                    reservation_date = pd.to_datetime(
                        row["予約日"]
                    ).strftime("%Y年%m月%d日")

                    with st.container(border=True):
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
                            and str(row["備考"]).lower() != "nan"
                        ):
                            st.write(f'備考：{row["備考"]}')

                        reservation_id = str(row["予約ID"])
                        confirm_key = (
                            f"confirm_cancel_{reservation_id}"
                        )

                        if confirm_key not in st.session_state:
                            st.session_state[confirm_key] = False

                        if not st.session_state[confirm_key]:
                            if st.button(
                                "この予約をキャンセル",
                                key=f"cancel_{reservation_id}",
                            ):
                                st.session_state[confirm_key] = True
                                st.rerun()

                        else:
                            st.warning(
                                "この予約をキャンセルしますか？"
                            )

                            col_yes, col_no = st.columns(2)

                            with col_yes:
                                if st.button(
                                    "はい、キャンセルする",
                                    key=f"yes_{reservation_id}",
                                    type="primary",
                                    use_container_width=True,
                                ):
                                    latest_df = load_reservations()

                                    latest_df = latest_df[
                                        latest_df["予約ID"]
                                        != reservation_id
                                    ]

                                    save_reservations(latest_df)

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
                                    key=f"no_{reservation_id}",
                                    use_container_width=True,
                                ):
                                    st.session_state[
                                        confirm_key
                                    ] = False
                                    st.rerun()


# =========================================================
# 管理者画面
# =========================================================

elif page == "管理者":

    # -----------------------------------------------------
    # 管理者ログイン前
    # -----------------------------------------------------

    if not st.session_state.admin_logged_in:
        st.title("🔐 予約管理")

        admin_id = st.text_input("管理者ID")
        admin_password = st.text_input(
            "管理者パスワード",
            type="password",
        )

        if st.button(
            "管理者ログイン",
            type="primary",
            use_container_width=True,
        ):
            if (
                admin_id == ADMIN_ID
                and admin_password == ADMIN_PASSWORD
            ):
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error(
                    "管理者IDまたはパスワードが違います。"
                )

        st.stop()

    # -----------------------------------------------------
    # 管理者ログイン後
    # -----------------------------------------------------

    st.title("🔐 予約管理")

    _, col_logout = st.columns([3, 1])

    with col_logout:
        if st.button(
            "ログアウト",
            key="admin_logout",
        ):
            st.session_state.admin_logged_in = False
            st.rerun()

    df = load_reservations()

    if df.empty:
        st.info("現在予約はありません。")
        st.stop()

    df["予約日_dt"] = pd.to_datetime(
        df["予約日"],
        errors="coerce",
    )

    today_ts = pd.Timestamp(date.today())

    # =====================================================
    # 今後の全予約
    # =====================================================

    st.subheader("今後の予約")

    future_df = df[
        df["予約日_dt"] >= today_ts
    ].copy()

    future_df = future_df.sort_values(
        by=["予約日_dt", "時間"]
    )

    if future_df.empty:
        st.info("今後の予約はありません。")
    else:
        display_df = future_df[
            [
                "予約日",
                "時間",
                "顧客ID",
                "名前",
                "人数",
                "電話番号",
                "備考",
            ]
        ].copy()

        display_df["予約日"] = pd.to_datetime(
            display_df["予約日"],
            errors="coerce",
        ).dt.strftime("%Y/%m/%d")

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "今後の予約組数",
            f"{len(future_df)}組",
        )

        total_future_people = pd.to_numeric(
            future_df["人数"],
            errors="coerce",
        ).fillna(0).sum()

        col2.metric(
            "今後の予約人数",
            f"{int(total_future_people)}名",
        )

    st.divider()

    # =====================================================
    # 日付別確認
    # =====================================================

    st.subheader("日付別に確認")

    selected_admin_date = st.date_input(
        "確認する日付",
        value=date.today(),
        key="admin_date",
    )

    date_str = selected_admin_date.strftime("%Y-%m-%d")

    day_df = df[
        df["予約日"] == date_str
    ].copy()

    if day_df.empty:
        st.info("この日の予約はありません。")
    else:
        day_df = day_df.sort_values(by="時間")

        display_day = day_df[
            [
                "時間",
                "顧客ID",
                "名前",
                "人数",
                "電話番号",
                "備考",
            ]
        ].copy()

        st.dataframe(
            display_day,
            use_container_width=True,
            hide_index=True,
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "予約組数",
            f"{len(day_df)}組",
        )

        total_day_people = pd.to_numeric(
            day_df["人数"],
            errors="coerce",
        ).fillna(0).sum()

        col2.metric(
            "予約人数",
            f"{int(total_day_people)}名",
        )

    st.divider()

    # =====================================================
    # 顧客別確認
    # =====================================================

    st.subheader("顧客別に確認")

    customer_ids = sorted(
        [
            str(customer_id)
            for customer_id in df["顧客ID"].dropna().unique()
            if str(customer_id).strip() != ""
        ]
    )

    if not customer_ids:
        st.info(
            "顧客情報の登録された予約はありません。"
        )
    else:
        selected_customer_id = st.selectbox(
            "お客様ID",
            customer_ids,
        )

        customer_df = df[
            df["顧客ID"] == selected_customer_id
        ].copy()

        customer_df = customer_df.sort_values(
            by=["予約日_dt", "時間"]
        )

        display_customer = custom
