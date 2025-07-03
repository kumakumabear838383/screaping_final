from flask import Flask, request, render_template, send_file
import requests
from bs4 import BeautifulSoup
import time
import random
import warnings
import pandas as pd
import os

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

app = Flask(__name__)
TEMP_EXCEL_PATH = "result.xlsx"

@app.route('/', methods=['GET', 'POST'])
def scrape():
    titles = []
    error = None

    # 変数初期化
    input_url = ''
    input_selector = ''
    input_selector_mode = ''
    input_pages = '1'

    if request.method == 'POST':
        input_url = request.form.get('url', '').strip()
        input_selector_mode = request.form.get('selector_mode', 'default')
        input_selector = request.form.get('custom_selector', '').strip()
        input_pages = request.form.get('pages', '1')

        try:
            pages = int(input_pages)
            if not input_url.startswith('http'):
                error = "URLは http:// または https:// から始めてください。"
            else:
                # セレクタ決定
                if input_selector_mode == 'default':
                    selector_template = 'a.m-mainlist-item__ttl'  # nth-of-typeには対応不要
                else:
                    selector_template = input_selector

                for page_num in range(1, pages + 1):
                    url = input_url.rstrip('/') if page_num == 1 else f"{input_url.rstrip('/')}/{page_num}.html"
                    print(f"取得中: {url}")
                    res = requests.get(url, verify=False)
                    if res.status_code != 200:
                        error = f"HTTPエラー（{res.status_code}）: {url}"
                        break

                    soup = BeautifulSoup(res.text, 'html.parser')

                    if input_selector_mode == 'default':
                        matches = soup.select(selector_template)
                        titles.extend([m.get_text(strip=True) for m in matches])
                        time.sleep(random.uniform(1, 3))
                    else:
                        for num in range(1, 150):
                            full_selector = selector_template.replace('{num}', str(num))
                            item = soup.select_one(full_selector)
                            if item:
                                titles.append(item.get_text(strip=True))
                                time.sleep(random.uniform(1, 3))
        except Exception as e:
            error = str(e)

        # Excel保存
        if titles:
            df = pd.DataFrame(titles, columns=["取得タイトル"])
            df.to_excel(TEMP_EXCEL_PATH, index=False)

    return render_template('index.html', titles=titles, error=error,
                           input_url=input_url,
                           input_selector=input_selector,
                           input_selector_mode=input_selector_mode,
                           input_pages=input_pages)


@app.route('/download')
def download():
    if os.path.exists(TEMP_EXCEL_PATH):
        return send_file(TEMP_EXCEL_PATH, as_attachment=True)
    else:
        return "ファイルが存在しません", 404

if __name__ == '__main__':
    app.run(debug=True)
