import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time
from io import BytesIO
import warnings

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

st.set_page_config(page_title="スクレイピングツール", layout="centered")
st.title("Webスクレイピングツール（nth-of-type対応）")

# 入力フォーム
url = st.text_input("対象URL（例：https://www.walkerplus.com/spot_list/ar0700/sg0107）")
selector_mode = st.radio("セレクタ選択", ["デフォルト（a.m-mainlist-item__ttl）", "カスタム"])
custom_selector = ""
if selector_mode == "カスタム":
    custom_selector = st.text_input("CSSセレクタ（{num}を含める）", placeholder="li:nth-of-type({num}) > div > a")
pages = st.number_input("取得ページ数", min_value=1, max_value=50, value=1)

# 実行ボタン
if st.button("スクレイピング開始") and url:
    try:
        titles = []
        for page_num in range(1, pages + 1):
            # URL構築（1ページ目は /1.html なし）
            full_url = url.rstrip('/') if page_num == 1 else f"{url.rstrip('/')}/{page_num}.html"
            st.write(f"取得中: {full_url}")
            res = requests.get(full_url, verify=False)
            soup = BeautifulSoup(res.text, "html.parser")

            if selector_mode.startswith("デフォルト"):
                matches = soup.select("a.m-mainlist-item__ttl")
                titles.extend([m.get_text(strip=True) for m in matches])
                time.sleep(random.uniform(1, 3))
            else:
                for i in range(1, 150):
                    selector = custom_selector.replace("{num}", str(i))
                    el = soup.select_one(selector)
                    if el:
                        titles.append(el.get_text(strip=True))
                        time.sleep(random.uniform(1, 3))

        if titles:
            df = pd.DataFrame(titles, columns=["取得タイトル"])
            st.success(f"{len(titles)} 件取得しました。")
            st.dataframe(df)

            # Excel出力用にバッファへ書き込み
            buffer = BytesIO()
            df.to_excel(buffer, index=False, engine="openpyxl")
            buffer.seek(0)
            st.download_button("Excelファイルをダウンロード", buffer, file_name="result.xlsx")

        else:
            st.warning("データが取得できませんでした。")

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
